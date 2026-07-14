diff -r 462e66461b20 executable/SequentialMain.hs
--- a/executable/SequentialMain.hs	Sun May 24 18:19:24 2026 +0200
+++ b/executable/SequentialMain.hs	Fri May 29 12:00:19 2026 +0200
@@ -46,6 +46,7 @@
 import Data.Hashable
 import Data.Binary.Sharing
 import qualified Data.ByteString.Lazy as BS
+import qualified Data.Intern
 
 data MainFlags =
   MainFlags {
@@ -1223,7 +1224,7 @@
 
 main = do
   hSetBuffering stdout LineBuffering
-  stampM (intern "twee") . join . parseCommandLineWithExtraArgs
+  stampM (Data.Intern.intern "twee") . join . parseCommandLineWithExtraArgs
     ["--no-conjunctive-conjectures", "--no-split"]
 #ifdef VERSION_twee
     "Twee, the wonderful equation engine" . version ("twee version " ++ VERSION_twee) $
diff -r 462e66461b20 src/Data/DynamicArray.hs
--- a/src/Data/DynamicArray.hs	Sun May 24 18:19:24 2026 +0200
+++ b/src/Data/DynamicArray.hs	Fri May 29 12:00:19 2026 +0200
@@ -18,6 +18,8 @@
   -- | The default value.
   def :: a
 
+instance Default (Maybe a) where def = Nothing
+
 -- | An array.
 data Array a =
   Array {
diff -r 462e66461b20 src/Twee.hs
--- a/src/Twee.hs	Sun May 24 18:19:24 2026 +0200
+++ b/src/Twee.hs	Fri May 29 12:00:19 2026 +0200
@@ -973,6 +973,7 @@
 {-# INLINE complete #-}
 complete :: (Function f, MonadIO m) => Output m f -> Config f -> State f -> m (State f)
 complete Output{..} config@Config{..} state =
+  stampM "complete" $
   flip StateM.execStateT state $ do
     tasks <- sequence
       [newTask 10 (fromIntegral cfg_renormalise_percent / 100) $ do
@@ -1031,6 +1032,7 @@
     (False, state)
   | solved state && not cfg_always_complete = (False, state)
   | otherwise =
+    stamp "complete1" $
     case st_random_seed state of
       Nothing -> -- normal mode
         case dequeue config state of
diff -r 462e66461b20 src/Twee/Profile.hs
--- a/src/Twee/Profile.hs	Sun May 24 18:19:24 2026 +0200
+++ b/src/Twee/Profile.hs	Fri May 29 12:00:19 2026 +0200
@@ -1,5 +1,5 @@
 -- Basic support for profiling.
-{-# LANGUAGE CPP, OverloadedStrings #-}
+{-# LANGUAGE CPP, FlexibleInstances #-}
 module Twee.Profile(stamp, stampWith, stampM, stampGen, stampGen', profile) where
 
 #ifdef PROFILE
@@ -14,13 +14,16 @@
 import Control.Monad.IO.Class
 import qualified Data.HashMap.Strict as HashMap
 import Data.HashMap.Strict(HashMap)
-import Data.Symbol
-import Data.Symbol.Unsafe
 import Data.Hashable
 import Test.QuickCheck.Gen
+import Data.String
+import Data.Intern
+import Data.Array.IO
+import Data.Array.Base
+import Control.Exception
 
-instance Hashable Symbol where
-  hashWithSalt s (Symbol n _) = hashWithSalt s n
+instance IsString (Sym String) where
+  fromString = intern
 
 data Record =
   Record {
@@ -28,91 +31,111 @@
     rec_cumulative :: {-# UNPACK #-} !Word64,
     rec_count      :: {-# UNPACK #-} !Word64 }
 
-data Running =
-  Running {
-    run_started  :: {-# UNPACK #-} !Word64,
-    run_skipped  :: {-# UNPACK #-} !Word64,
-    run_overhead :: {-# UNPACK #-} !Word64 }
-
 data State =
   State {
-    st_map      :: !(HashMap Symbol Record),
-    st_overhead :: {-# UNPACK #-} !Word64,
-    st_running  :: {-# UNPACK #-} !Running,
-    st_stack    :: [Running] }
+    st_capacity   :: {-# UNPACK #-} !Int,
+    st_individual :: {-# UNPACK #-} !(IOUArray Int Word64),
+    st_cumulative :: {-# UNPACK #-} !(IOUArray Int Word64),
+    st_total      :: {-# UNPACK #-} !(IOUArray Int Word64) }
+
+{-# NOINLINE state #-}
+state :: IORef State
+state = unsafePerformIO $ do
+  ind <- newArray (0, -1) undefined
+  cum <- newArray (0, -1) undefined
+  tot <- newArray (0, -1) undefined
+  newIORef (State 0 ind cum tot)
+
+resizeArr :: (Ix i, Num i, MArray IOUArray e IO) => e -> i -> i -> IOUArray i e -> IO (IOUArray i e)
+resizeArr def hi ix arr =
+  newGenArray (0, ix) $ \ix ->
+    if ix <= hi then readArray arr ix else return def
 
-{-# NOINLINE eventLog #-}
-eventLog :: IORef State
-eventLog = unsafePerformIO (newIORef (State HashMap.empty 0 (Running 0 0 0) []))
+-- TODO atomicity
+{-# INLINE reserve #-}
+reserve :: Sym String -> IO State
+reserve sym = do
+  state@State{..} <- readIORef state
+  if symId sym < st_capacity then
+    return state
+  else slowPathReserve sym state
 
-{-# NOINLINE enter #-}
-enter :: IO (HashMap Symbol Record)
+{-# NOINLINE slowPathReserve #-}
+slowPathReserve :: Sym String -> State -> IO State
+slowPathReserve sym State{..} = do
+  st_individual <- resizeArr 0 (st_capacity-1) n st_individual
+  st_cumulative <- resizeArr 0 (st_capacity-1) n st_cumulative
+  st_total <- resizeArr 0 (st_capacity-1) n st_total
+  let state' = State (n+1) st_individual st_cumulative st_total
+  writeIORef state state'
+  return state'
+  where
+    n = max (symId sym) (st_capacity*2)
+
+{-
+{-# INLINE enter #-}
+enter :: IO (Sym String -> IO ())
 enter = do
-  State{..} <- readIORef eventLog
+  state@State{..} <- readIORef eventLog
   tsc <- rdtsc
   let !running = Running tsc 0 0
-  writeIORef eventLog (State st_map st_overhead running (st_running:st_stack))
-  return st_map
+  writeIORef eventLog state{st_running = running, st_stack=running:st_stack}
+-}
+
+exit :: Word64 -> Sym String -> IO ()
+exit tsc1 str = do
+  tsc2 <- rdtsc
+  let n = symId str
+  State{..} <- reserve str
+
+  let cumulative = tsc2 - tsc1
+      individual = cumulative
+      -- To make sure recursive functions are accounted for properly,
+      -- we reset cumulative time to what it was on entry
+      --Record _ c2 _ = HashMap.lookupDefault (Record 0 0 0) str old_st
 
-{-# NOINLINE exit #-}
-exit :: HashMap Symbol Record -> Symbol -> IO ()
-exit old_st str = do
-  tsc <- rdtsc
-  State st_map st_overhead Running{..} st_stack <- readIORef eventLog
-  str `pseq` do
-    let cumulative = tsc - run_started - run_overhead
-        individual = cumulative - run_skipped
-        -- To make sure recursive functions are accounted for properly,
-        -- we reset cumulative time to what it was on entry
-        Record _ c2 _ = HashMap.lookupDefault (Record 0 0 0) str old_st
-        plus (Record i1 c1 m) (Record i2 _ n) =
-          Record (i1+i2) (c1+c2) (m+n)
-        rec = Record individual cumulative 1
-        m = HashMap.insertWith plus str rec st_map
-    case st_stack of
-      [] -> error "mismatched enter/exit"
-      Running{..}:st_stack -> m `pseq` do
-        tsc' <- rdtsc
-        let overhead = tsc' - tsc
-            run =
-              Running run_started
-                (run_skipped+cumulative)
-                (run_overhead+overhead)
-        writeIORef eventLog $! State m (st_overhead + overhead) run st_stack
+  --modifyArray individualTimes n (+ individual)
+  unsafeModify st_cumulative n (+ cumulative)
+  unsafeModify st_total n (+ 1)
 
-{-# NOINLINE stamp #-}
-stamp :: Symbol -> a -> a
-stamp str x =
-  unsafePerformIO $ do
-    m <- enter
-    x `pseq` exit m str
+unsafeModify :: (Ix i, MArray IOUArray e IO) => IOUArray i e -> Int -> (e -> e) -> IO ()
+unsafeModify arr ix f = do
+  val <- unsafeRead arr ix
+  unsafeWrite arr ix (f val)
+
+stamp :: Sym String -> a -> a
+stamp !str x =
+  unsafeDupablePerformIO $ do
+    tsc <- rdtsc
+    evaluate x
+    exit tsc str
     return x
 
-stampWith :: Symbol -> (a -> b) -> a -> a
+stampWith :: Sym String -> (a -> b) -> a -> a
 stampWith str f x = stamp str (f x) `pseq` x
 
-stampM :: MonadIO m => Symbol -> m a -> m a
+stampM :: MonadIO m => Sym String -> m a -> m a
 stampM str mx = do
-  m <- liftIO enter
+  tsc <- liftIO rdtsc
   x <- mx
-  liftIO (exit m str)
+  liftIO (exit tsc str)
   return x
 
-stampGen :: Symbol -> Gen a -> Gen a
+stampGen :: Sym String -> Gen a -> Gen a
 stampGen sym gen = MkGen (\g n -> stamp sym (unGen gen g n))
 
-stampGen' :: (a -> Symbol) -> Gen a -> Gen a
+stampGen' :: (a -> Sym String) -> Gen a -> Gen a
 stampGen' sym gen = MkGen (\g n -> let x = unGen gen g n in stamp (sym x) x)
 
-report :: (Record -> Word64) -> HashMap Symbol Record -> IO ()
+report :: (Record -> Word64) -> [(Sym String, Record)] -> IO ()
 report f cs = mapM_ pr ts
   where
     ts =
       sortBy (comparing (negate . f . snd)) $
       sortBy (comparing fst) $
-      HashMap.toList $
+      --HashMap.toList $
       {-HashMap.filter ((>= tot `div` 200) . f)-} cs
-    tot = sum (map rec_individual (HashMap.elems cs))
+    tot = {-sum (map (rec_individual . snd) cs)-} head [rec_individual t | (x, t) <- cs, x == intern "twee"]
     pr (str, rec) =
       printf "%10.2f Mclocks (%6.2f%% of total): %s, %d calls\n"
         (fromIntegral n / 10^6 :: Double)
@@ -124,13 +147,16 @@
 
 profile :: IO ()
 profile = do
-  State{..} <- readIORef eventLog
-  let log = HashMap.insert "OVERHEAD" (Record st_overhead st_overhead 0) st_map
+  State{..} <- reserve (intern "OVERHEAD")
+  individual <- getElems st_individual
+  cumulative <- getElems st_cumulative
+  total <- getElems st_total
+  let times = [(unsafeMkSym n, Record ind cum t) | (n, ind, cum, t) <- zip4 [0..] individual cumulative total, t > 0]
   putStrLn "Individual time:"
-  report rec_individual log
+  report rec_individual times
   putStrLn ""
   putStrLn "Cumulative time:"
-  report rec_cumulative log
+  report rec_cumulative times
 #else
 import Control.Monad.IO.Class
 import Test.QuickCheck
diff -r 462e66461b20 src/twee-lib.cabal
--- a/src/twee-lib.cabal	Sun May 24 18:19:24 2026 +0200
+++ b/src/twee-lib.cabal	Fri May 29 12:00:19 2026 +0200
@@ -90,7 +90,8 @@
     QuickCheck,
     deepseq >= 1.4.0.0,
     unordered-containers,
-    hashable
+    hashable,
+    array
   hs-source-dirs:      .
   ghc-options:         -W -fno-warn-incomplete-patterns -fno-warn-dodgy-imports -fno-warn-deprecations
   default-language:    Haskell2010
