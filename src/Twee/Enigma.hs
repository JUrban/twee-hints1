-- | ENIGMA-style learned rule evaluation.
--
-- A LightGBM model (text format) is evaluated on "enigmatic" features of
-- an equation: vertical walks, horizontal features, symbol counts and
-- depths, length statistics. The featurizer must agree with
-- @hints/enigfeats.py@, which produces the training data.
{-# LANGUAGE BangPatterns, RecordWildCards #-}
module Twee.Enigma(
  Tree, Forest, parseForest, predictRaw,
  eqnFeatures, RuleModel(..), ruleModelRow, ruleModelRaw) where

import Data.Array.Unboxed
import Data.Bits
import Data.List
import qualified Data.Map.Strict as Map
import Data.Map.Strict(Map)
import qualified Data.IntMap.Strict as IntMap
import Data.IntMap.Strict(IntMap)
import qualified Data.Set as Set
import Data.Set(Set)
import Twee.Base
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
          ints k = maybe [] (map read . words) (Map.lookup k kv) :: [Int]
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
    readD s = case s of
      "inf" -> 1/0
      "-inf" -> -1/0
      ('+':r) -> readD r
      _ | '.' `elem` s || 'e' `elem` s || 'E' `elem` s -> read (fixup s)
        | otherwise -> fromIntegral (read s :: Integer)
    -- Haskell's read does not accept "1e-35" without a leading digit
    -- dot form issues like ".5" or "5."; normalise those.
    fixup s =
      let (sign, r) = case s of ('-':t) -> ("-", t); _ -> ("", s)
          r1 = if "." `isPrefixOf` r then '0':r else r
          (m, e) = break (`elem` "eE") r1
          m1 = if "." `isSuffixOf` m then m ++ "0" else m
          m2 = if '.' `elem` m1 then m1 else m1 ++ ".0"
      in sign ++ m2 ++ e

-- | Raw score (sum of leaf values) of a forest on a sparse feature vector.
predictRaw :: Forest -> IntMap Double -> Double
predictRaw forest x = foldl' (\ !s t -> s + evalTree t) 0 forest
  where
    val f = IntMap.findWithDefault 0 f x
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

data RuleModel f =
  RuleModel {
    rm_forest    :: Forest,
    rm_vocab     :: Map String Int,  -- "c:<feature>" -> column
    rm_goal      :: [(Int, Double)], -- goal block columns
    rm_gkeys     :: Set String,      -- goal V/H/C features (for overlap)
    rm_name      :: f -> String,
    rm_threshold :: Double,          -- on the raw score
    rm_penalty   :: Float,
    rm_debug     :: Bool }

-- | The feature row of a rule (equation) added as the idx-th rule.
ruleModelRow :: RuleModel f -> Int -> Term f -> Term f -> IntMap Double
ruleModelRow RuleModel{..} idx t u =
  let hf = eqnFeatures rm_name t u
      sh = [ k | k <- Map.keys hf, k `Set.member` rm_gkeys ]
      cnt c = fromIntegral (length (filter ((== c) . head) sh))
      ncs = length (filter ((== 'C') . head) (Map.keys hf))
      fixed =
        [(0, cnt 'V'), (1, cnt 'H'), (2, cnt 'C' / fromIntegral (max 1 ncs)),
         (3, log (1 + fromIntegral idx))]
      cs = [ (i, v) | (k, v) <- Map.toList hf, Just i <- [Map.lookup ("c:" ++ k) rm_vocab] ]
  in IntMap.fromList (fixed ++ cs ++ rm_goal)

ruleModelRaw :: RuleModel f -> Int -> Term f -> Term f -> Double
ruleModelRaw rm idx t u = predictRaw (rm_forest rm) (ruleModelRow rm idx t u)
