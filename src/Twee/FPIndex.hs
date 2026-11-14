-- | A fingerprint index (S. Schulz, "Fingerprint Indexing for Paramodulation
-- and Rewriting", IJCAR 2012) for finding overlap partners.
--
-- A term is summarised by what it has at a few fixed positions: a function
-- symbol, a variable, "below a variable" or "no such position". Two terms can
-- only unify if their summaries are compatible at every sampled position, so
-- the index returns a superset of the unifiable keys (never fewer).
{-# LANGUAGE BangPatterns, PatternSynonyms #-}
module Twee.FPIndex(
  FPIndex, empty, null, insert, delete, query, fingerprint) where

import Prelude hiding (null)
import Twee.Term(Term, pattern Var, pattern App, unpack)
import Data.Intern(symId)
import qualified Data.IntMap.Strict as IntMap
import Data.IntMap.Strict(IntMap)
import qualified Data.IntSet as IntSet
import Data.IntSet(IntSet)
import Data.Maybe

-- Feature codes. A function symbol f is coded as 3 + its number.
fN, fA, fB :: Int
fN = 0  -- the position does not exist (a symbol above it has too few arguments)
fA = 1  -- a variable is at the position
fB = 2  -- the position is below a variable

-- The sampled positions (argument paths, 0-based): the root, the first three
-- arguments, and the first two arguments of the first two arguments.
paths :: [[Int]]
paths = [[], [0], [1], [2], [0,0], [0,1], [1,0], [1,1]]

{-# INLINE fingerprint #-}
fingerprint :: Term f -> [Int]
fingerprint t = map (feature t) paths

feature :: Term f -> [Int] -> Int
feature (Var _) [] = fA
feature (Var _) _ = fB
feature (App f _) [] = 3 + symId f
feature (App _ ts) (i:is) =
  case drop i (unpack ts) of
    (u:_) -> feature u is
    [] -> fN

-- | A multiset of keys (Ints), each stored under a fingerprint.
data FPIndex = Leaf !IntSet | Node !(IntMap FPIndex)

empty :: FPIndex
empty = emptyAt (length paths)

emptyAt :: Int -> FPIndex
emptyAt 0 = Leaf IntSet.empty
emptyAt _ = Node IntMap.empty

null :: FPIndex -> Bool
null (Leaf s) = IntSet.null s
null (Node m) = IntMap.null m

insert :: [Int] -> Int -> FPIndex -> FPIndex
insert [] !k (Leaf s) = Leaf (IntSet.insert k s)
insert (x:xs) !k (Node m) =
  Node (IntMap.alter (Just . insert xs k . fromMaybe (emptyAt (length xs))) x m)
insert _ _ _ = error "FPIndex.insert: fingerprint of the wrong length"

delete :: [Int] -> Int -> FPIndex -> FPIndex
delete [] !k (Leaf s) = Leaf (IntSet.delete k s)
delete (x:xs) !k (Node m) = Node (IntMap.update del x m)
  where
    del t = let t' = delete xs k t in if null t' then Nothing else Just t'
delete _ _ _ = error "FPIndex.delete: fingerprint of the wrong length"

-- | All keys whose fingerprint is compatible (for unification) with the given one.
query :: [Int] -> FPIndex -> IntSet
query [] (Leaf s) = s
query (q:qs) (Node m) = IntSet.unions [ query qs t | t <- children q ]
  where
    look k = maybeToList (IntMap.lookup k m)
    children q
      | q == fB = IntMap.elems m
      | q == fA = IntMap.elems (IntMap.delete fN m)
      | q == fN = look fN ++ look fB
      | otherwise = look q ++ look fA ++ look fB
query _ _ = IntSet.empty
