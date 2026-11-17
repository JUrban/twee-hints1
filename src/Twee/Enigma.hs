-- | ENIGMA-style learned rule evaluation.
--
-- A LightGBM model (text format) is evaluated on "enigmatic" features of
-- an equation: vertical walks, horizontal features, symbol counts and
-- depths, length statistics. The featurizer must agree with
-- @hints/enigfeats.py@, which produces the training data.
{-# LANGUAGE BangPatterns, RecordWildCards #-}
module Twee.Enigma(
  Tree, Forest, parseForest, parseForestBin, predictRaw, predictDense, predictWith, treeFeatures,
  eqnFeatures, eqnFeaturesH, RuleModel(..), mkRuleModel, ruleModelRow, ruleModelRaw) where

import Data.Array.Unboxed
import Data.Array.ST(runSTUArray, newArray, writeArray)
import Data.Array.Base(unsafeAt)
import Data.Bits
import Data.Word(Word64)
import qualified Data.IntSet as IntSet
import Data.IntSet(IntSet)
import Data.Char(isDigit)
import Data.Ratio((%))
import Data.List
import qualified Data.Map.Strict as Map
import Data.Map.Strict(Map)
import qualified Data.IntMap.Strict as IntMap
import Data.IntMap.Strict(IntMap)
import qualified Data.Set as Set
import Data.Set(Set)
import Twee.Base
import qualified Data.ByteString.Lazy as BL
import Data.Binary.Get
import Control.Monad(replicateM)
import Data.Intern(unintern)

data Tree =
  Tree {
    t_feat  :: !(UArray Int Int),
    t_thr   :: !(UArray Int Double),
    t_dt    :: !(UArray Int Int),
    t_left  :: !(UArray Int Int),
    t_right :: !(UArray Int Int),
    t_leaf  :: !(UArray Int Double) }

type Forest = [Tree]

-- | The features a tree splits on.
treeFeatures :: Tree -> UArray Int Int
treeFeatures = t_feat

-- | Parse the trees of a LightGBM text model.
parseForest :: String -> Forest
parseForest str = map mk (blocks (lines str))
  where
    blocks [] = []
    blocks (l:ls)
      | "Tree=" `isPrefixOf` l =
        let (b, rest) = break (\x -> "Tree=" `isPrefixOf` x || "end of trees" `isPrefixOf` x) ls
        in b : blocks rest
      | otherwise = blocks ls
    mk b =
      let kv = Map.fromList [ (k, drop 1 v) | x <- b, let (k, v) = break (== '=') x, not (null v) ]
          ints k = maybe [] (map readI . words) (Map.lookup k kv) :: [Int]
          dbls k = maybe [] (map readD . words) (Map.lookup k kv) :: [Double]
          arr :: IArray UArray e => [e] -> UArray Int e
          arr xs = listArray (0, length xs - 1) xs
      in Tree {
           t_feat = arr (ints "split_feature"),
           t_thr = arr (dbls "threshold"),
           t_dt = arr (ints "decision_type"),
           t_left = arr (ints "left_child"),
           t_right = arr (ints "right_child"),
           t_leaf = arr (dbls "leaf_value") }
    readI ('-':r) = negate (readI r)
    readI r = foldl' (\ !n c -> n * 10 + (fromEnum c - 48)) 0 r
    readD ('-':r) = negate (readD r)
    readD ('+':r) = readD r
    readD "inf" = 1/0
    readD r =
      let (ip, r1) = span isDigit r
          (fp, r2) = case r1 of ('.':t) -> span isDigit t; _ -> ("", r1)
          ex = case r2 of
                 (c:t) | c == 'e' || c == 'E' -> readI (dropWhile (== '+') t)
                 _ -> 0
          mant = foldl' (\ !n c -> n * 10 + toInteger (fromEnum c - 48)) 0 (ip ++ fp) :: Integer
          e = ex - length fp
      in if e >= 0 then fromInteger (mant * 10 ^ e) else fromRational (mant % (10 ^ negate e))

-- | Parse the binary forest format written by hints/lgb2bin.py.
parseForestBin :: BL.ByteString -> Forest
parseForestBin = runGet $ do
  n <- getInt32le
  replicateM (fromIntegral n) $ do
    ns <- fromIntegral <$> getInt32le
    nl <- fromIntegral <$> getInt32le
    let ints k = map fromIntegral <$> replicateM k getInt32le
        arr :: IArray UArray e => Int -> [e] -> UArray Int e
        arr k xs = listArray (0, k - 1) xs
    sf <- ints ns
    th <- replicateM ns getDoublele
    dt <- ints ns
    lc <- ints ns
    rc <- ints ns
    lv <- replicateM nl getDoublele
    return Tree { t_feat = arr ns sf, t_thr = arr ns th, t_dt = arr ns dt,
                  t_left = arr ns lc, t_right = arr ns rc, t_leaf = arr nl lv }

-- | Raw score (sum of leaf values) of a forest on a sparse feature vector.
predictRaw :: Forest -> IntMap Double -> Double
predictRaw forest x = predictDense forest (dense x)
  where
    n = if IntMap.null x then 1 else fst (IntMap.findMax x) + 1
    dense m = runSTUArray $ do
      a <- newArray (0, n - 1) 0
      mapM_ (\(i, v) -> writeArray a i v) (IntMap.toList m)
      return a

predictDense :: Forest -> UArray Int Double -> Double
predictDense forest x = predictWith forest val
  where
    (_, hi) = bounds x
    val f = if f <= hi then unsafeAt x f else 0

-- | Raw score of a forest on the features given by a function (no array is built).
{-# INLINE predictWith #-}
predictWith :: Forest -> (Int -> Double) -> Double
predictWith forest val = foldl' (\ !s t -> s + evalTree t) 0 forest
  where
    evalTree t
      | snd (bounds (t_feat t)) < 0 = t_leaf t ! 0
      | otherwise = go 0
      where
        go !i
          | i < 0 = t_leaf t ! (complement i)
          | otherwise =
            let v = val (t_feat t ! i)
                dt = t_dt t ! i
                missing = (dt `shiftR` 2) .&. 3
                defLeft = dt .&. 2 /= 0
                left
                  | missing == 1 && abs v <= 1e-35 = defLeft
                  | missing == 2 && isNaN v = defLeft
                  | otherwise = v <= t_thr t ! i
            in go (if left then t_left t ! i else t_right t ! i)

-- | Enigmatic features of an equation, as in enigfeats.features.
eqnFeatures :: (f -> String) -> Term f -> Term f -> Map String Double
eqnFeatures name tl tr =
  let
    symName (Var _) = "*"
    symName (App f _) = name (unintern f)
    -- state: (features, symbol depths, var occurrences, len, depth, width)
    walk path d (fs, ds, vs, !len, !dep, !wid) t =
      let s = symName t
          path' = s:path
          len' = len + 1
          vs' = case t of Var (V x) -> IntMap.insertWith (+) x (1::Int) vs; _ -> vs
          args = case t of App _ ts -> unpack ts; _ -> []
          (fs1, ds1, vs1, len1, dep1, wid1) =
            case args of
              [] -> (fs, ds, vs', len', max dep d, wid + 1)
              _ ->
                let fsH = Map.insertWith (+) ("H" ++ s ++ "." ++ intercalate "." (map symName args)) 1 fs
                in foldl' (walk path' (d + 1)) (fsH, ds, vs', len', dep, wid) args
          fs2 = foldl' (\m k -> Map.insertWith (+) ('V':intercalate "|" (reverse (take k path'))) 1 m)
                  fs1 [ k | k <- [2..3], length (take k path') >= k ]
          (fs3, ds3) = case t of
            Var _ -> (fs2, ds1)
            _ -> (Map.insertWith (+) ('C':s) 1 fs2, Map.insertWith max s d ds1)
      in (fs3, ds3, vs1, len1, dep1, wid1)
    (f1, d1, v1, len1, dep1, wid1) =
      walk ["="] (1 :: Int) (walk ["="] 1 (Map.empty, Map.empty, IntMap.empty, 1 :: Int, 0, 0 :: Int) tl) tr
    f2 = Map.insertWith (+) ("H=." ++ intercalate "." (sort [symName tl, symName tr])) 1 f1
    f3 = Map.union f2 (Map.fromList [ ('D':s, fromIntegral d) | (s, d) <- Map.toList d1 ])
    vocc = sum (IntMap.elems v1)
    isV (Var _) = True
    isV _ = False
    stats =
      [("Llen", len1), ("Ldepth", dep1), ("Lwidth", wid1),
       ("Lvars", IntMap.size v1), ("Lvocc", vocc),
       ("Lvuniq", length (filter (== 1) (IntMap.elems v1))),
       ("Lvshared", length (filter (> 1) (IntMap.elems v1))),
       ("Lfuncs", Map.size d1), ("Lfocc", len1 - 1 - vocc),
       ("Lsizediff", abs (len tl - len tr)),
       ("Lvarside", if isV tl || isV tr then 1 else 0)]
  in Map.union (Map.fromList [ (k, fromIntegral v) | (k, v) <- stats ]) f3

-- FNV-1a hashes of feature names, computed without building the strings.
fnvStart :: Word64
fnvStart = 14695981039346656037

fnvStep :: Word64 -> Char -> Word64
fnvStep h c = (h `xor` fromIntegral (fromEnum c)) * 1099511628211

fnvStr :: Word64 -> String -> Word64
fnvStr = foldl' fnvStep

-- hash of prefix ++ intercalate [sep] xs
fnvJoin :: Word64 -> Char -> [String] -> Word64
fnvJoin h _ [] = h
fnvJoin h sep (x:xs) = foldl' (\h' y -> fnvStr (fnvStep h' sep) y) (fnvStr h x) xs

hkey :: String -> Int
hkey = fromIntegral . fnvStr fnvStart

-- | eqnFeatures with hashed names: all features, and the V, H and C keys.
eqnFeaturesH :: (f -> String) -> Term f -> Term f -> (IntMap Double, IntSet, IntSet, IntSet)
eqnFeaturesH name tl tr =
  let
    symName (Var _) = "*"
    symName (App f _) = name (unintern f)
    hV = fnvStep fnvStart 'V'
    hH = fnvStep fnvStart 'H'
    hC = fnvStep fnvStart 'C'
    hD = fnvStep fnvStart 'D'
    ins k = IntMap.insertWith (+) (fromIntegral k) 1
    walk path d (fs, ds, vs, !len, !dep, !wid) t =
      let s = symName t
          path' = s:path
          len' = len + 1
          vs' = case t of Var (V x) -> IntMap.insertWith (+) x (1::Int) vs; _ -> vs
          args = case t of App _ ts -> unpack ts; _ -> []
          (fs1, ds1, vs1, len1, dep1, wid1) =
            case args of
              [] -> (fs, ds, vs', len', max dep d, wid + 1)
              _ ->
                let fsH = ins (fnvJoin hH '.' (s : map symName args)) fs
                in foldl' (walk path' (d + 1)) (fsH, ds, vs', len', dep, wid) args
          fs2 = case path' of
                  (a:b:rest) ->
                    let f2 = ins (fnvJoin hV '|' [b, a]) fs1
                    in case rest of
                         (c:_) -> ins (fnvJoin hV '|' [c, b, a]) f2
                         [] -> f2
                  _ -> fs1
          (fs3, ds3) = case t of
            Var _ -> (fs2, ds1)
            _ -> (ins (fnvStr hC s) fs2, Map.insertWith max s d ds1)
      in (fs3, ds3, vs1, len1, dep1, wid1)
    (f1, d1, v1, len1, dep1, wid1) =
      walk ["="] (1 :: Int) (walk ["="] 1 (IntMap.empty, Map.empty, IntMap.empty, 1 :: Int, 0, 0 :: Int) tl) tr
    f2 = ins (fnvJoin hH '.' ("=" : sort [symName tl, symName tr])) f1
    dfs = IntMap.fromList [ (fromIntegral (fnvStr hD s), fromIntegral d) | (s, d) <- Map.toList d1 ]
    vocc = sum (IntMap.elems v1)
    isV (Var _) = True
    isV _ = False
    stats =
      [("Llen", len1), ("Ldepth", dep1), ("Lwidth", wid1),
       ("Lvars", IntMap.size v1), ("Lvocc", vocc),
       ("Lvuniq", length (filter (== 1) (IntMap.elems v1))),
       ("Lvshared", length (filter (> 1) (IntMap.elems v1))),
       ("Lfuncs", Map.size d1), ("Lfocc", len1 - 1 - vocc),
       ("Lsizediff", abs (len tl - len tr)),
       ("Lvarside", if isV tl || isV tr then 1 else 0)]
    syms = Map.keys d1
    cKeys = IntSet.fromList [ fromIntegral (fnvStr hC s) | s <- syms ]
    allF = IntMap.unions [IntMap.fromList [ (hkey k, fromIntegral v) | (k, v) <- stats ], dfs, f2]
  in (allF, IntSet.empty, IntSet.empty, cKeys)

data RuleModel f =
  RuleModel {
    rm_forest    :: Forest,
    rm_vocab     :: Map String Int,  -- "c:<feature>" -> column
    rm_goal      :: [(Int, Double)], -- goal block columns
    rm_gkeys     :: Set String,      -- goal V/H/C features (for overlap)
    rm_name      :: f -> String,
    rm_threshold :: Double,          -- on the raw score
    rm_penalty   :: Float,
    rm_defer_max :: Int,             -- defer each critical pair at most this often
    rm_debug     :: Bool,
    rm_parents   :: Bool,            -- the vocabulary has a "p:" block
    rm_hvocab_c  :: IntMap Int,      -- hashed "c:" vocabulary
    rm_hvocab_p  :: IntMap Int,      -- hashed "p:" vocabulary
    rm_hgoal_v   :: IntSet,          -- hashed goal V/H/C features, by kind
    rm_hgoal_h   :: IntSet,
    rm_hgoal_c   :: IntSet }

-- | Fill in the hashed fields from rm_vocab and rm_gkeys.
mkRuleModel :: RuleModel f -> RuleModel f
mkRuleModel rm =
  rm { rm_hvocab_c = IntMap.fromList [ (hkey k, i) | (pk, i) <- Map.toList (rm_vocab rm), Just k <- [stripPrefix "c:" pk] ],
       rm_hvocab_p = IntMap.fromList [ (hkey k, i) | (pk, i) <- Map.toList (rm_vocab rm), Just k <- [stripPrefix "p:" pk] ],
       rm_hgoal_v = kind 'V', rm_hgoal_h = kind 'H', rm_hgoal_c = kind 'C' }
  where
    kind c = IntSet.fromList [ hkey k | k@(c':_) <- Set.toList (rm_gkeys rm), c' == c ]

-- | The feature row of a rule (equation) added as the idx-th rule.
ruleModelRow :: RuleModel f -> Int -> Term f -> Term f -> [(Term f, Term f)] -> IntMap Double
ruleModelRow RuleModel{..} idx t u parents =
  let (hf, _, _, ckeys) = eqnFeaturesH rm_name t u
      inG = IntMap.keysSet hf
      cnt g = fromIntegral (IntSet.size (IntSet.intersection inG g))
      fixed =
        [(0, cnt rm_hgoal_v), (1, cnt rm_hgoal_h),
         (2, cnt rm_hgoal_c / fromIntegral (max 1 (IntSet.size ckeys))),
         (3, log (1 + fromIntegral idx))]
      cs = [ (i, v) | (k, v) <- IntMap.toList hf, Just i <- [IntMap.lookup k rm_hvocab_c] ]
      pf = IntMap.unionsWith (+) [ let (f, _, _, _) = eqnFeaturesH rm_name pt pu in f | rm_parents, (pt, pu) <- parents ]
      ps = [ (i, v) | (k, v) <- IntMap.toList pf, Just i <- [IntMap.lookup k rm_hvocab_p] ]
  in IntMap.fromList (fixed ++ cs ++ ps ++ rm_goal)

-- | The row computed with string feature names (reference implementation).
ruleModelRowS :: RuleModel f -> Int -> Term f -> Term f -> [(Term f, Term f)] -> IntMap Double
ruleModelRowS RuleModel{..} idx t u parents =
  let hf = eqnFeatures rm_name t u
      sh = [ k | k <- Map.keys hf, k `Set.member` rm_gkeys ]
      cnt c = fromIntegral (length (filter ((== c) . head) sh))
      ncs = length (filter ((== 'C') . head) (Map.keys hf))
      fixed =
        [(0, cnt 'V'), (1, cnt 'H'), (2, cnt 'C' / fromIntegral (max 1 ncs)),
         (3, log (1 + fromIntegral idx))]
      cs = [ (i, v) | (k, v) <- Map.toList hf, Just i <- [Map.lookup ("c:" ++ k) rm_vocab] ]
      pf = Map.unionsWith (+) [ eqnFeatures rm_name pt pu | rm_parents, (pt, pu) <- parents ]
      ps = [ (i, v) | (k, v) <- Map.toList pf, Just i <- [Map.lookup ("p:" ++ k) rm_vocab] ]
  in IntMap.fromList (fixed ++ cs ++ ps ++ rm_goal)

ruleModelRaw :: RuleModel f -> Int -> Term f -> Term f -> [(Term f, Term f)] -> Double
ruleModelRaw rm idx t u parents = predictRaw (rm_forest rm) (ruleModelRow rm idx t u parents)
