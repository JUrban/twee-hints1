-- | A module which can run housekeeping tasks every so often.
module Twee.Task(Task, newTask, newTaskCost, checkTask, useAbstractTime, setAbstractTime) where

import System.CPUTime
import System.IO.Unsafe
import Data.IORef
import Control.Monad.IO.Class

-- | An abstract clock, in picoseconds like getCPUTime. When it is set,
-- tasks and timeouts follow it instead of CPU time, so that runs do not
-- depend on machine load.
{-# NOINLINE abstractClock #-}
abstractClock :: IORef (Maybe Integer)
abstractClock = unsafePerformIO (newIORef Nothing)

-- | Switch to the abstract clock, starting at the given time.
useAbstractTime :: MonadIO m => Integer -> m ()
useAbstractTime t = liftIO $ writeIORef abstractClock (Just t)

-- | Advance the abstract clock (no effect unless it is in use).
setAbstractTime :: MonadIO m => Integer -> m ()
setAbstractTime t = liftIO $ modifyIORef' abstractClock (fmap (const t))

getClock :: IO Integer
getClock = readIORef abstractClock >>= maybe getCPUTime return

data TaskData m a =
  TaskData {
    -- When was the task created?
    task_start :: !Integer,
    -- When was the task last run?
    task_last :: !Integer,
    -- How long have we spent on this task so far?
    task_spent :: !Integer,
    -- How often should we run this task at most, in seconds?
    task_frequency :: !Double,
    -- What proportion of our time should we spend on the task?
    task_budget :: !Double,
    -- The task itself, with its abstract cost in picoseconds (see newTaskCost)
    task_what :: m (a, Integer) }

-- | A task which runs in the monad @m@ and produces a value of type @a@.
newtype Task m a = Task (IORef (TaskData m a))

-- | Create a new task that should be run a certain proportion
-- of the time. The first argument is how often in seconds the
-- task should run, at most. The second argument is the maximum
-- percentage of time that should be spent on the task.
newTask :: MonadIO m => Double -> Double -> m a -> m (Task m a)
newTask freq budget what = newTaskCost freq budget (fmap (\x -> (x, 0)) what)

-- | A task that also reports its cost in abstract picoseconds. The abstract
-- clock does not move while a task runs, so without a cost the budget of a
-- task never binds in abstract time and it runs at its full frequency,
-- however expensive it is. The cost is charged to the task only when the
-- abstract clock is in use, and keeps runs deterministic.
newTaskCost :: MonadIO m => Double -> Double -> m (a, Integer) -> m (Task m a)
newTaskCost freq budget what = liftIO $ do
  now <- getClock
  Task <$> newIORef (TaskData now now 0 freq budget what)

-- | Run a task if it's time to run it.
checkTask :: MonadIO m => Task m a -> m (Maybe a)
checkTask (Task ref) = do
  task@TaskData{..} <- liftIO $ readIORef ref
  now <- liftIO getClock
  if not (taskDue now task) then return Nothing else do
    (res, cost) <- task_what
    after <- liftIO getClock
    abstract <- liftIO $ fmap (maybe False (const True)) (readIORef abstractClock)
    liftIO $ writeIORef ref task {
      task_last = after,
      task_spent = task_spent + (after-now) + (if abstract then cost else 0) }
    return (Just res)

-- Check if a task should be run now.
taskDue :: Integer -> TaskData m a -> Bool
taskDue now TaskData{..} =
  -- Don't run more than the frequency says.
  fromInteger (now - task_last) >= task_frequency * 10^12 &&
  -- Run if we spent less than task_budget proportion of the total time so far.
  -- Use > rather than >= so that tasks with zero budget never get run.
  fromInteger (now - task_start) * task_budget > fromInteger task_spent
