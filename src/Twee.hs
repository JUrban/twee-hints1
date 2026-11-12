-- | The main prover loop.
{-# LANGUAGE MultiParamTypeClasses, GADTs, OverloadedStrings, GeneralizedNewtypeDeriving, FlexibleInstances, RankNTypes, TupleSections, DeriveAnyClass, CPP #-}
module Twee where

import Twee.Base
import Twee.Enigma
import qualified Data.Set as Set
import Twee.Rule hiding (normalForms)
import qualified Twee.Rule as Rule
import Twee.Equation
import qualified Twee.Proof as Proof
import Twee.Proof(Axiom(..), Proof(..), Derivation, ProvedGoal(..), provedGoal, certify, derivation)
import Twee.CP hiding (Config)
import qualified Twee.CP as CP
import Twee.Join hiding (Config, defaultConfig)
import qualified Twee.Join as Join
import qualified Twee.Rule.Index as RuleIndex
import Twee.Rule.Index(RuleIndex(..))
import qualified Twee.Index as Index
import Twee.Index(Index)
import Twee.Constraints
import Twee.Utils
import Twee.Task
import qualified Data.BatchedQueue as Queue
import Data.BatchedQueue(Queue)
import qualified Data.IntMap.Strict as IntMap
import Data.IntMap(IntMap)
import Data.Maybe
import Data.List
import Data.Function
import qualified Data.Map.Strict as Map
import Data.Map(Map)
import Data.Int
import Control.Monad
import Control.Monad.IO.Class
import Control.Monad.Trans.Class
import qualified Control.Monad.Trans.State.Strict as StateM
import qualified Data.IntSet as IntSet
import Data.IntSet(IntSet)
import Twee.Profile
import Data.Ord
import Data.PackedSequence(PackedSequence)
import qualified Data.PackedSequence as PackedSequence
import Test.QuickCheck.Gen hiding (sample)
import Test.QuickCheck.Random
import qualified Debug.Trace
import Twee.Generate
import qualified System.Random as Random
import GHC.Generics
import Data.Binary.Sharing
import Data.Bits
import Data.Hashable(hash)
import Data.Intern(symId)

----------------------------------------------------------------------
-- * Configuration and prover state.
----------------------------------------------------------------------

-- | The prover configuration.
data Config f =
  Config {
    cfg_accept_term               :: Maybe (Term f -> Bool),
    cfg_max_critical_pairs        :: Int64,
    cfg_max_cp_depth              :: Int,
    cfg_max_rules                 :: Int,
    cfg_max_time                  :: Maybe Double,
    cfg_simplify                  :: Bool,
    cfg_renormalise_percent       :: Int,
    cfg_cp_sample_size            :: Int,
    cfg_renormalise_threshold     :: Int,
    cfg_set_join_goals            :: Bool,
    cfg_always_simplify           :: Bool,
    cfg_complete_subsets          :: Bool,
    cfg_hint_func                 :: Int -> Float -> Sym f,
    cfg_cp_config                 :: !CP.Config,
    cfg_join                      :: Join.Config,
    cfg_proof_presentation        :: Proof.Config f,
    cfg_eliminate_axioms          :: [Axiom f],
    cfg_random_mode               :: Bool,
    cfg_random_mode_goal_directed :: Bool,
    cfg_random_mode_simple        :: Bool,
    cfg_random_mode_best_of       :: Int,
    cfg_always_complete           :: Bool,
    cfg_hint_skel_cost            :: Float,
    cfg_hint_skel_factor          :: Float,
    cfg_eqhint_factor             :: Float,
    cfg_eqhint_weight             :: Float,
    cfg_eqhint_normalise          :: Bool,
    cfg_eqhint_fullnorm           :: Bool,
    cfg_eqhint_debug              :: Bool,
    cfg_eqhint_consider           :: Bool,
    cfg_eqhint_requeue            :: Double,
    cfg_print_score               :: Bool,
    cfg_log_given                 :: Bool,
    cfg_rule_model                :: Maybe (RuleModel f),
    cfg_eqhint_stall              :: Int,
    cfg_eqhint_watch              :: Float }

-- | The prover state.
data State f =
  State {
    st_axioms         :: ![Axiom f],
    st_rules          :: !(RuleIndex f (Rule f)),
    st_active_set     :: !(IntMap (Active f)),
    st_joinable       :: !(Index f (Equation f)),
    st_goals          :: ![Goal f],
    st_queue          :: !(Queue Batch),
    st_hints          :: {-# UNPACK #-} !(Hints f),
    st_eqhints        :: !(EqHints f),
    st_given          :: [Equation f],
    st_cur_passive    :: !(Maybe Passive),
    st_deferred       :: !(Set.Set (Id, Id, How)),
    st_ndeferred      :: !Int,
    st_next_active    :: {-# UNPACK #-} !Id,
    st_considered     :: {-# UNPACK #-} !Int64,
    st_simplified_at  :: {-# UNPACK #-} !Id,
    st_cp_sample      :: !(Sample (Maybe (Overlap (Active f) f))),
    st_not_complete   :: !IntSet,
    st_complete       :: !(Index f (Rule f)),
    st_messages_rev   :: ![Message f],
    st_random_seed    :: Maybe (ReadShowBinary QCGen),
    st_problem_term   :: Maybe (ConfluenceFailure f) }
  deriving (Generic, Binary)

-- | The default prover configuration.
defaultConfig :: Function f => Config f
defaultConfig =
  Config {
    cfg_accept_term = Nothing,
    cfg_max_critical_pairs = maxBound,
    cfg_max_cp_depth = maxBound,
    cfg_max_rules = maxBound,
    cfg_max_time = Nothing,
    cfg_simplify = True,
    cfg_renormalise_percent = 5,
    cfg_renormalise_threshold = 20,
    cfg_cp_sample_size = 100,
    cfg_set_join_goals = True,
    cfg_always_simplify = False,
    cfg_complete_subsets = False,
    cfg_hint_func = \_ _ -> error "cfg_hint_func not configured",
    cfg_cp_config = CP.defaultConfig,
    cfg_join = Join.defaultConfig,
    cfg_proof_presentation = Proof.defaultConfig,
    cfg_eliminate_axioms = [],
    cfg_random_mode = False,
    cfg_random_mode_goal_directed = False,
    cfg_random_mode_best_of = 1,
    cfg_random_mode_simple = False,
    cfg_always_complete = False,
    cfg_hint_skel_cost = 1,
    cfg_hint_skel_factor = 0,
    cfg_eqhint_factor = 0.01,
    cfg_eqhint_weight = 0,
    cfg_eqhint_normalise = True,
    cfg_eqhint_fullnorm = False,
    cfg_eqhint_debug = False,
    cfg_eqhint_consider = True,
    cfg_eqhint_requeue = 0,
    cfg_print_score = False,
    cfg_log_given = False,
    cfg_rule_model = Nothing,
    cfg_eqhint_stall = 0,
    cfg_eqhint_watch = 0 }

-- | Compute cfg_score_cp from the CP configuration.
{-# INLINE scoreCP #-}
scoreCP :: Function f => Config f -> Depth -> Hints f -> Equation f -> Float
scoreCP config@Config{..} d hints eqn =
  let s1 = score cfg_cp_config d (scoreTerm config hints) eqn
      -- s2 = score cfg_cp_config d (scoreTerm config (Hints [] Index.empty 0)) eqn
  {-
  in if s1 /= s2 then trace ("used hint for " ++ prettyShow eqn) (trace (prettyShow eqn ++ " => " ++ prettyShow (bothSides (applyHints hints) eqn)) s1) else s1
  -}
  in s1

{-# INLINE scoreTerm #-}
scoreTerm :: Function f => Config f -> Hints f -> Term f -> Float
scoreTerm Config{..} hints t = termScore cfg_cp_config (applyHints hints t)

-- | Does this configuration run the prover in a complete mode?
configIsComplete :: Config f -> Bool
configIsComplete Config{..} =
  isNothing cfg_accept_term &&
  isNothing cfg_max_time &&
  cfg_max_critical_pairs == maxBound &&
  cfg_max_cp_depth == maxBound &&
  cfg_max_rules == maxBound

-- | The initial state.
initialState :: Config f -> State f
initialState Config{..} =
  State {
    st_axioms = [],
    st_rules = RuleIndex.empty,
    st_active_set = IntMap.empty,
    st_joinable = Index.empty,
    st_goals = [],
    st_queue = Queue.empty,
    st_hints =
      Hints {
        hints_list = [],
        hints_index = Index.empty,
        hints_next = 0 },
    st_eqhints = emptyEqHints,
    st_given = [],
    st_cur_passive = Nothing,
    st_deferred = Set.empty,
    st_ndeferred = 0,
    st_next_active = 1,
    st_considered = 0,
    st_simplified_at = 1,
    st_cp_sample = emptySample cfg_cp_sample_size,
    st_not_complete = IntSet.empty,
    st_complete = Index.empty,
    st_messages_rev = [],
    st_random_seed =
      case cfg_random_mode of
        False -> Nothing
        True -> Just (ReadShowBinary (mkQCGen 12345)),
    st_problem_term = Nothing }

----------------------------------------------------------------------
-- * Messages.
----------------------------------------------------------------------

-- | A message which is produced by the prover when something interesting happens.
data Message f =
    -- | A new rule.
    NewActive !(Maybe Float) !(Active f)
    -- | A new joinable equation.
  | NewEquation !(Equation f)
    -- | A new hint was added.
  | NewHint !(Rule f) !HintKind
    -- | A new rule matched an equation hint.
  | HintMatched !Int !(Active f)
    -- | A rule was deleted.
  | DeleteActive !(Active f)
    -- | The CP queue was simplified.
  | SimplifyQueue
    -- | All except these axioms are complete (with a suitable-chosen subset of the rules).
  | NotComplete !IntSet
    -- | The rules were reduced wrt each other.
  | Interreduce
    -- | Status update: how many queued critical pairs there are.
  | Status !Int
    -- | New problem term discovered.
  | NewProblemTerm !(ConfluenceFailure f)
  deriving (Generic, Binary)

instance Function f => Pretty (Message f) where
  pPrint (NewActive mscore rule) =
    case mscore of
      Nothing -> pPrint rule
      Just score -> parens (pPrint score) <+> pPrint rule
 --   $$ case cp_top (active_cp rule) of { Just t -> text "  (normal forms of term" <+> pPrint t <#> text ")"; Nothing -> pPrintEmpty }
  pPrint (NewEquation eqn) =
    text "  (hard)" <+> pPrint eqn
  pPrint (HintMatched n active) =
    text "  (matched hint" <+> pPrint n <#> text ")" <+> pPrint active
  pPrint (NewHint rule kind) =
    text "  (" <#> pPrint kind <+> text "hint)" <+> pPrint rule
  pPrint (DeleteActive rule) =
    text "  (delete rule " <#> pPrint (active_id rule) <#> text ")"
  pPrint SimplifyQueue =
    text "  (simplifying queued critical pairs...)"
  pPrint (NotComplete ax) =
    case IntSet.toList ax of
      [n] ->
        text "  (axiom" <+> pPrint n <+> "is not completed yet)"
      xs ->
        text "  (axioms" <+> text (show xs) <+> "are not completed yet)"
  pPrint Interreduce =
    text "  (simplifying rules with respect to one another...)"
  pPrint (Status n) =
    text "  (" <#> pPrint n <+> text "queued critical pairs)"
  pPrint (NewProblemTerm cf) =
    text "" $$
    text "Problem term:" <+> pPrint (cf_term cf) $$
    text "  NF 1:" $$ ppR (cf_term cf) (cf_left cf) $$
    text "  NF 2:" $$ ppR (cf_term cf) (cf_right cf)
    where
      ppR _ [] = pPrintEmpty
      ppR t (rr@(r,_,_):rs) =
        text "    -> {by" <+> pPrint r <#> text "}" $$
        text "       " <#> pPrint (ruleResult1 t rr) $$
        ppR (ruleResult1 t rr) rs

-- | Emit a message.
message :: PrettyTerm f => Message f -> State f -> State f
message !msg state@State{..} =
  state { st_messages_rev = msg:st_messages_rev }

-- | Forget about all emitted messages.
clearMessages :: State f -> State f
clearMessages state@State{..} =
  state { st_messages_rev = [] }

-- | Get all emitted messages.
messages :: State f -> [Message f]
messages state = reverse (st_messages_rev state)

----------------------------------------------------------------------
-- * The CP queue.
----------------------------------------------------------------------

-- | Compute all critical pairs from a rule.
{-# INLINEABLE makePassives #-}
makePassives :: Function f => Config f -> State f -> Active f -> [Passive]
-- don't generate critical pairs when in random mode
makePassives Config{cfg_random_mode = True} _ _ = []
makePassives config@Config{..} state@State{..} rule =
-- XXX factor out depth calculation
  stampWith "make critical pair" length
  [ makePassive config state overlap
  | ok rule,
    overlap <- overlaps (index_oriented st_rules) (filter ok rules) rule ]
  where
    rules = IntMap.elems st_active_set
    ok rule = the rule < Depth cfg_max_cp_depth

data Passive =
  Passive {
    passive_score :: {-# UNPACK #-} !Float,
    passive_rule1 :: {-# UNPACK #-} !Id,
    passive_rule2 :: {-# UNPACK #-} !Id,
    passive_how   :: !How }
  deriving (Eq, Generic, Binary)

instance Ord Passive where
  compare = comparing f
    where
      f Passive{..} =
        (passive_score,
         intMax (fromIntegral passive_rule1) (fromIntegral passive_rule2),
         intMin (fromIntegral passive_rule1) (fromIntegral passive_rule2),
         passive_how)

data Batch =
  Batch {
    batch_kind      :: !BatchKind,
    batch_rule      :: {-# UNPACK #-} !Id,
    batch_best      :: {-# UNPACK #-} !Passive,
    batch_rest      :: {-# UNPACK #-} !(PackedSequence (Float, Id, How)) }
  deriving (Eq, Generic, Binary)

data BatchKind = Rule1 | Rule2 deriving (Eq, Generic, Binary)

instance Queue.Batch Batch where
  type Label Batch = Id
  type Entry Batch = Passive

  makeBatch rule ps =
    make1 Rule1 ps1 ++ make1 Rule2 ps2
    where
      (ps1, ps2) = partition isRule1 ps
      isRule1 Passive{..} = rule == passive_rule1

      make1 _ [] = []
      make1 kind (p:ps) =
        [Batch {
           batch_kind = kind,
           batch_rule = rule,
           batch_best = p,
           batch_rest = 
             PackedSequence.fromList $
               [ (passive_score, if kind == Rule1 then passive_rule2 else passive_rule1, passive_how)
               | Passive{..} <- ps ] }]

  unconsBatch batch@Batch{..} =
    (batch_best,
     do (p, ps) <- PackedSequence.uncons batch_rest
        return batch{batch_best = unpack batch_kind p, batch_rest = ps})
    where
      unpack Rule1 (score, rule2, how) =
        Passive score batch_rule rule2 how
      unpack Rule2 (score, rule1, how) =
        Passive score rule1 batch_rule how

  batchLabel Batch{..} = batch_rule
  batchSize Batch{..} = 1 + PackedSequence.size batch_rest

{-# INLINEABLE makePassive #-}
makePassive :: Function f => Config f -> State f -> Overlap (Active f) f -> Passive
makePassive config@Config{..} state@State{..} Overlap{..} =
  Passive {
    passive_score = eqHintScore config state overlap_top overlap_eqn (scoreCP config depth st_hints overlap_eqn),
    passive_rule1 = active_id overlap_rule1,
    passive_rule2 = active_id overlap_rule2,
    passive_how   = overlap_how }
  where
    depth = Depth (succ (getDepth (the overlap_rule1) `max` getDepth (the overlap_rule2)))

-- | Turn a Passive back into an overlap.
-- Doesn't try to simplify it.
{-# INLINEABLE findPassive #-}
findPassive :: forall f. Function f => State f -> Passive -> Maybe (Overlap (Active f) f)
findPassive State{..} Passive{..} = do
  rule1 <- IntMap.lookup (fromIntegral passive_rule1) st_active_set
  rule2 <- IntMap.lookup (fromIntegral passive_rule2) st_active_set
  overlapAt passive_how rule1 rule2
    (renameAvoiding (the rule2 :: Rule f) (the rule1)) (the rule2)

-- | Renormalise a queued Passive.
{-# INLINEABLE simplifyPassive #-}
simplifyPassive :: Function f => Config f -> State f -> Passive -> Maybe (Passive)
simplifyPassive config@Config{..} state@State{..} passive = do
  overlap <- findPassive state passive
  overlap <- simplifyOverlap (index_oriented st_rules) overlap
  let r1 = overlap_rule1 overlap
      r2 = overlap_rule2 overlap
  return passive {
    passive_score =
#ifndef USE_LPO
      passive_score passive `min`
#endif
      -- XXX factor out depth calculation
      eqHintScore config state (overlap_top overlap) (overlap_eqn overlap)
        (scoreCP config (Depth (succ (getDepth (the r1) `max` getDepth (the r2)))) st_hints (overlap_eqn overlap)) }

-- | Check if we should renormalise the queue.
{-# INLINEABLE shouldSimplifyQueue #-}
shouldSimplifyQueue :: Function f => Config f -> State f -> Bool
shouldSimplifyQueue Config{..} State{..} =
  length (filter isNothing (sampleValue st_cp_sample)) * 100 >= cfg_renormalise_threshold * cfg_cp_sample_size

-- | Renormalise the entire queue.
{-# INLINEABLE simplifyQueue #-}
simplifyQueue :: Function f => Config f -> State f -> State f
simplifyQueue config state =
  resetSample config state { st_queue = simp (st_queue state) }
  where
    simp =
      Queue.mapMaybe (simplifyPassive config state)

-- | Enqueue a set of critical pairs.
{-# INLINEABLE enqueue #-}
enqueue :: Function f => State f -> Id -> [Passive] -> State f
enqueue state rule passives =
  state { st_queue = Queue.insert rule passives (st_queue state) }

-- | Dequeue a critical pair.
--
-- Also takes care of:
--
--   * removing any orphans from the head of the queue
--   * ignoring CPs that are too big
--   * putting back any CPs whose score got bigger since they were enqueued
{-# INLINEABLE dequeue #-}
dequeue :: Function f => Config f -> State f -> (Maybe (Info, CriticalPair f, Active f, Active f, Passive), State f)
dequeue config@Config{..} state@State{..} =
  case deq 0 st_queue of
    -- Explicitly make the queue empty, in case it e.g. contained a
    -- lot of orphans
    Nothing -> (Nothing, state { st_queue = Queue.empty })
    Just (overlap, n, queue) ->
      (Just overlap,
       state { st_queue = queue, st_considered = st_considered + n })
  where
    deq !n queue = do
      let ok id = fromIntegral id `IntMap.member` st_active_set
      (passive, queue) <- Queue.removeMinFilter ok queue
      case findPassive state passive of
        Just (overlap@Overlap{overlap_eqn = t :=: u, overlap_rule1 = rule1, overlap_rule2 = rule2})
          | fromMaybe True (cfg_accept_term <*> pure t),
            fromMaybe True (cfg_accept_term <*> pure u),
            cp <- makeCriticalPair overlap,
            Just newPassive <- simplifyPassive config state passive ->
              if passive_score newPassive <= passive_score passive then
                (if cfg_eqhint_debug && passive_score passive < 1 then Debug.Trace.trace ("DEQ " ++ show (passive_score passive) ++ " at " ++ show st_next_active ++ ": " ++ prettyShow (cp_eqn cp)) else id) $
                return ((combineInfo (active_info rule1) (active_info rule2), cp, rule1, rule2, newPassive), n+1, queue)
              else
                deq (n+1) (Queue.insert (passive_rule1 newPassive) [newPassive] queue)

        _ -> deq (n+1) queue

    combineInfo i1 i2 =
      Info {
        -- XXX factor out depth calculation
        info_depth = Depth (succ (max (getDepth (info_depth i1)) (getDepth (info_depth i2)))),
        info_max = IntSet.union (info_max i1) (info_max i2) }

----------------------------------------------------------------------
-- * Active rewrite rules.
----------------------------------------------------------------------

data Active f =
  Active {
    active_id    :: {-# UNPACK #-} !Id,
    active_info  :: {-# UNPACK #-} !Info,
    active_rule  :: {-# UNPACK #-} !(Rule f),
    active_top   :: !(Maybe (Term f)),
    active_proof :: {-# UNPACK #-} !(Proof f),
    -- A model in which the rule is false (used when reorienting)
    active_model :: !(Model f),
    active_positions :: !(Positions2 f) }
  deriving (Generic, Binary)

active_cp :: Active f -> CriticalPair f
active_cp Active{..} =
  CriticalPair {
    cp_eqn = unorient active_rule,
    cp_top = active_top,
    cp_proof = derivation active_proof }

activeScore :: Function f => Config f -> State f -> Active f -> Float
activeScore config@Config{..} State{..} Active{..} =
  scoreCP config (info_depth active_info) st_hints (equation active_proof)

activeRules :: Active f -> [Rule f]
activeRules Active{..} =
  case active_positions of
    ForwardsPos _ -> [active_rule]
    BothPos _ _ -> [active_rule, backwards active_rule]

data Info =
  Info {
    info_depth :: {-# UNPACK #-} !Depth,
    info_max   :: !IntSet }
  deriving (Generic, Binary)

instance Eq (Active f) where
  (==) = (==) `on` active_id

instance Function f => Pretty (Active f) where
  pPrint Active{..} =
    pPrint active_id <#> text "." <+> pPrint (canonicalise active_rule)

instance Has (Active f) Id where the = active_id
instance Has (Active f) Depth where the = info_depth . active_info
instance f ~ g => Has (Active f) (Rule g) where the = active_rule
instance f ~ g => Has (Active f) (Positions2 g) where the = active_positions

-- Add a new active.
{-# INLINEABLE addActive #-}
addActive :: Function f => Config f -> State f -> (Id -> Active f) -> State f
addActive config state@State{..} active0 =
  let
    active@Active{..} = active0 st_next_active
    mscore
      | cfg_print_score config = Just (activeScore config state active)
      | otherwise = Nothing
    state' =
      recordEqHintMatch active $
      message (NewActive mscore active) $
      addActiveOnly config state{st_next_active = st_next_active+1} active
    logGiven st
      | cfg_log_given config = st{st_given = unorient active_rule : st_given}
      | otherwise = st
  in if subsumed (st_joinable, st_complete) st_rules (unorient active_rule) then
    state
  else
    normaliseGoals config $
    enqueueRule (logGiven state') active
  where
    enqueueRule state rule =
      sample (length passives) passives $
      enqueue state (the rule) passives
      where
        passives = makePassives config state rule

-- Update the list of sampled critical pairs.
{-# INLINEABLE sample #-}
sample :: Function f => Int -> [Passive] -> State f -> State f
sample m passives state@State{..} =
  state{st_cp_sample = addSample (m, map find passives) st_cp_sample}
  where
    find passive = do
      overlap <- findPassive state passive
      simplifyOverlap (index_oriented st_rules) overlap

-- Reset the list of sampled critical pairs.
{-# INLINEABLE resetSample #-}
resetSample :: Function f => Config f -> State f -> State f
resetSample Config{..} state@State{..} =
  foldl' sample1 state' (Queue.toBatches st_queue)
  where
    state' =
      state {
        st_cp_sample = emptySample cfg_cp_sample_size }

    sample1 state batch = sample (Queue.batchSize batch) (Queue.unbatch batch) state

-- Simplify the sampled critical pairs.
-- (A sampled critical pair is replaced with Nothing if it can be
-- simplified.)
{-# INLINEABLE simplifySample #-}
simplifySample :: Function f => State f -> State f
simplifySample state@State{..} =
  state{st_cp_sample = mapSample (>>= simp) st_cp_sample}
  where
    simp overlap = do
      overlap' <- simplifyOverlap (index_oriented st_rules) overlap
      guard (overlap_eqn overlap == overlap_eqn overlap')
      return overlap

-- Add an active without generating critical pairs. Used in interreduction.
{-# INLINEABLE addActiveOnly #-}
addActiveOnly :: Function f => Config f -> State f -> Active f -> State f
addActiveOnly config state@State{..} active@Active{..} =
  addHintsRulePairs config active $
  state {
    st_rules = foldl' insertRule st_rules (activeRules active),
    st_active_set = IntMap.insert (fromIntegral active_id) active st_active_set }
  where
    insertRule rules rule =
      RuleIndex.insert (lhs rule) rule rules

-- Add an active without generating critical pairs. Used in interreduction.
{-# INLINEABLE addActiveSimp #-}
addActiveSimp :: Function f => Config f -> State f -> Active f -> State f
addActiveSimp config state@State{..} active@Active{..} =
  addHintsRulePairs config active $
  state {
    st_rules = foldl' insertRule st_rules (activeRules active) }
  where
    insertRule rules rule =
      RuleIndex.insert (lhs rule) rule rules

-- Delete an active. Used in interreduction, not suitable for general use.
{-# INLINE deleteActive #-}
deleteActive :: Function f => State f -> Active f -> State f
deleteActive state@State{..} active@Active{..} =
  state {
    st_rules = foldl' deleteRule st_rules (activeRules active),
    st_active_set = IntMap.delete (fromIntegral active_id) st_active_set }
  where
    deleteRule rules rule =
      RuleIndex.delete (lhs rule) rule rules

-- Try to join a critical pair.
{-# INLINEABLE consider #-}
consider :: Function f => Config f -> State f -> Info -> CriticalPair f -> State f
consider config state info cp =
  considerUsing (st_rules state) config state info cp

-- Try to join a critical pair, but using a different set of critical
-- pairs for normalisation.
{-# INLINEABLE considerUsing #-}
considerUsing ::
  Function f =>
  RuleIndex f (Rule f) -> Config f -> State f -> Info -> CriticalPair f -> State f
considerUsing rules config@Config{..} state@State{..} info cp0 =
  stamp "consider critical pair" $
  -- Important to canonicalise the rule so that we don't get
  -- bigger and bigger variable indices over time
  let cp = canonicalise cp0 in
  case joinCriticalPair cfg_join (st_joinable, st_complete) rules Nothing cp of
    Right (mcp, cps) ->
      let
        state' = foldl' (\state cp -> considerUsing rules config state info cp) state{st_cur_passive = Nothing} cps
      in case mcp of
        Just cp -> addJoinable state' (cp_eqn cp)
        Nothing -> state'

    Left (cp, model)
      | Just rm <- cfg_rule_model,
        Just p <- st_cur_passive,
        let key = (passive_rule1 p, passive_rule2 p, passive_how p),
        not (key `Set.member` st_deferred),
        let t :=: u = fromMaybe (cp_eqn cp) (expandGoalConsts st_eqhints (cp_eqn cp)),
        let raw = ruleModelRaw rm (fromIntegral st_next_active - 1) t u,
        (if rm_debug rm then Debug.Trace.trace ("RULEPRED " ++ show raw ++ " " ++ show (st_next_active - 1) ++ " " ++ prettyShow (t :=: u)) else id) (raw < rm_threshold rm) ->
        state {
          st_cur_passive = Nothing,
          st_deferred = Set.insert key st_deferred,
          st_ndeferred = st_ndeferred + 1,
          st_queue = Queue.insert (passive_rule1 p) [p{passive_score = passive_score p * rm_penalty rm}] st_queue }
      | otherwise ->
      generaliseCP cp $
      foldl' (\state cp -> addCP config model state info cp) state{st_cur_passive = Nothing} (split cp)

  where
    generaliseCP cp state
      | null cfg_eliminate_axioms = state
      | canonicalise (cp_eqn cp) == canonicalise (cp_eqn cp') = state
      | otherwise =
        consider config{cfg_eliminate_axioms = []} state info cp'
      where
        deriv =
          let d1 = Proof.eliminateDefinitions cfg_eliminate_axioms (cp_proof cp)
              [d2] = fixpointOn (map (equation . certify)) (Proof.generaliseProof False) [d1]
          in d2
        cp' = cp { cp_eqn = equation (certify deriv), cp_proof = deriv }

{-# INLINEABLE addCP #-}
addCP :: Function f => Config f -> Model f -> State f -> Info -> CriticalPair f -> State f
addCP config model state@State{..} info CriticalPair{..} =
  let
    pf = certify cp_proof
    rule = orient cp_eqn pf
  in
  addActive config state $ \n ->
  Active {
    active_id = n,
    active_info = info,
    active_rule = rule,
    active_model = model,
    active_top = cp_top,
    active_proof = pf,
    active_positions = positionsRule rule }

-- Add a new equation.
{-# INLINEABLE addAxiom #-}
addAxiom :: Function f => Config f -> State f -> Axiom f -> State f
addAxiom config state axiom =
  consider config state{st_axioms = axiom:st_axioms state}
    Info { info_depth = Depth 0, info_max = IntSet.fromList [axiom_number axiom | cfg_complete_subsets config] }
    CriticalPair {
      cp_eqn = axiom_eqn axiom,
      cp_top = Nothing,
      cp_proof = Proof.axiom axiom }

-- Record an equation as being joinable.
{-# INLINEABLE addJoinable #-}
addJoinable :: Function f => State f -> Equation f -> State f
addJoinable state eqn@(t :=: u) =
  message (NewEquation eqn) $
  state {
    st_joinable =
      Index.insert t (t :=: u) $
      Index.insert u (u :=: t) (st_joinable state) }

-- Find a confluent subset of the rules.
{-# INLINEABLE checkCompleteness #-}
checkCompleteness :: Function f => Config f -> State f -> State f
checkCompleteness _ state@State{..} | st_simplified_at == st_next_active = state
checkCompleteness _config state =
  state { st_not_complete = excluded,
          st_complete = Index.fromListWith lhs rules }
  where
    maxSet s = if IntSet.null s then minBound else IntSet.findMax s
    maxN = maximum [maxSet (info_max (active_info r)) | r <- IntMap.elems (st_active_set state)]
    excluded = go IntSet.empty
    go excl
      | m > maxN = excl
      | otherwise = go (IntSet.insert m excl)
      where
        m = bound excl

    bound excl = minimum . map (passiveMax excl) . Queue.toList $ st_queue state

    passiveMax excl p = fromMaybe maxBound $ do
      Overlap{overlap_rule1 = r1, overlap_rule2 = r2} <- findPassive state p
      let s = info_max (active_info r1) `IntSet.union` info_max (active_info r2)
      guard (s `IntSet.disjoint` excl)
      (n, _) <- IntSet.maxView s
      return n
    rules = concatMap activeRules (filter ok (IntMap.elems (st_active_set state)))
    ok r = info_max (active_info r) `IntSet.disjoint` excluded

-- Assume that all rules form a confluent rewrite system.
{-# INLINEABLE assumeComplete #-}
assumeComplete :: Function f => State f -> State f
assumeComplete state =
  state { st_not_complete = IntSet.empty,
          st_complete = Index.fromListWith lhs (concatMap activeRules (IntMap.elems (st_active_set state))) }

-- For goal terms we store the set of all their normal forms.
-- Name and number are for information only.
data Goal f =
  Goal {
    goal_name         :: String,
    goal_number       :: Int,
    goal_eqn          :: Equation f,
    goal_expanded_lhs :: Map (Term f) (Derivation f),
    goal_expanded_rhs :: Map (Term f) (Derivation f),
    goal_lhs          :: Map (Term f) (Term f, Reduction f),
    goal_rhs          :: Map (Term f) (Term f, Reduction f) }
  deriving (Show, Generic, Binary)

-- Add a new goal.
{-# INLINEABLE addGoal #-}
addGoal :: Function f => Config f -> State f -> Goal f -> State f
addGoal config state@State{..} goal =
  normaliseGoals config state { st_goals = goal:st_goals }

-- Normalise all goals.
{-# INLINEABLE normaliseGoals #-}
normaliseGoals :: Function f => Config f -> State f -> State f
normaliseGoals Config{..} state@State{..} =
  state {
    st_goals =
      map (goalMap (nf (rewrite reduces (index_all st_rules)))) st_goals }
  where
    goalMap f goal@Goal{..} =
      goal { goal_lhs = f goal_lhs, goal_rhs = f goal_rhs }
    nf reduce goals
      | cfg_set_join_goals =
        let pair (t, red) = (fst (goals Map.! t), red) in
        Map.map pair $ Rule.normalForms reduce (Map.map snd goals)
      | otherwise =
        Map.fromList $
          [ (result t q, (u, r `trans` q))
          | (t, (u, r)) <- Map.toList goals,
            let q = Rule.normaliseWith (const True) reduce t ]

-- Recompute all normal forms of all goals. Starts from the original goal term.
-- Different from normalising all goals, because there may be an intermediate
-- term on one of the reduction paths which we can now rewrite in a different
-- way.
{-# INLINEABLE recomputeGoals #-}
recomputeGoals :: Function f => Config f -> State f -> State f
recomputeGoals config state =
  -- Make this strict so that newTask can time it correctly
  forceList (map goal_lhs (st_goals state')) `seq`
  forceList (map goal_rhs (st_goals state')) `seq`
  state'
  where
    state' =
      normaliseGoals config (state { st_goals = map resetGoal (st_goals state) })

    forceList [] = ()
    forceList (x:xs) = x `seq` forceList xs

resetGoal :: Goal f -> Goal f
resetGoal goal@Goal{..} =
  goal { goal_lhs = expansions goal_expanded_lhs,
         goal_rhs = expansions goal_expanded_rhs }
  where
    expansions m =
      Map.mapWithKey (\t _ -> (t, [])) m

-- Rewrite goal terms backwards using rewrite rules.
{-# INLINEABLE rewriteGoalsBackwards #-}
rewriteGoalsBackwards :: Function f => State f -> State f
rewriteGoalsBackwards state =
  state { st_goals = map backwardsGoal (st_goals state) }
  where
    backwardsGoal goal@Goal{..} =
      resetGoal goal {
        goal_expanded_lhs = backwardsMap goal_expanded_lhs,
        goal_expanded_rhs = backwardsMap goal_expanded_rhs }
    backwardsMap m =
      Map.fromList $
        Map.toList m ++
        [ (ruleResult t r, p `Proof.trans` q)
        | (t, p) <- Map.toList m,
          r <- backwardsTerm t,
          let q = ruleProof t r ]
    backwardsTerm t = do
      rule <- map the (Index.elems (RuleIndex.index_all (st_rules state)))
      guard (usort (vars (lhs rule)) == usort (vars (rhs rule)))
      [r] <- anywhere (tryRule (\_ _ -> True) (backwards rule)) t
      return r

-- Create a goal.
{-# INLINE goal #-}
goal :: Int -> String -> Equation f -> Goal f
goal n name (t :=: u) =
  Goal {
    goal_name = name,
    goal_number = n,
    goal_eqn = t :=: u,
    goal_expanded_lhs = Map.singleton t (Proof.Refl t),
    goal_expanded_rhs = Map.singleton u (Proof.Refl u),
    goal_lhs = Map.singleton t (t, []),
    goal_rhs = Map.singleton u (u, []) }

----------------------------------------------------------------------
-- Hints.
----------------------------------------------------------------------

data Hints f =
  Hints {
    -- contains only user-provided hints
    hints_list  :: ![Rule f],
    -- also contains hints formed through CPs
    hints_index :: !(Index f (Rule f)),
    hints_next   :: !Int }
  deriving (Generic, Binary)

data HintKind = UserHint | DerivedHint deriving (Eq, Show, Generic, Binary)

instance Pretty HintKind where
  pPrint UserHint = text "show"
  pPrint DerivedHint = text "auto"

-- Add a new hint.
{-# INLINEABLE addHint #-}
addHint :: Function f => Config f -> State f -> Term f -> State f
addHint config@Config{..} state@State{..} hint =
  addHint' config state hint UserHint cost
  where
    cost = fromIntegral (len hint - length (vars hint)) * cfg_hint_skel_factor + cfg_hint_skel_cost

-- Add a new hint, with a specified kind and cost.
{-# INLINEABLE addHint' #-}
addHint' :: Function f => Config f -> State f -> Term f -> HintKind -> Float -> State f
addHint' config@Config{..} state@State{st_hints = Hints{..}, ..} hint kind cost =
  (if kind == UserHint then addHintRulesPairs config rule . addHintHintsPairs config rule else id) $
  {-
  trace ("hint: " ++ prettyShow hint) $
  trace ("kind: " ++ show kind) $
  trace ("cost: " ++ show cost) $
  trace ("hint term: " ++ prettyShow hintTerm) $
  trace "" $
  -}
  message (NewHint rule kind) $
  state {
    st_hints = Hints {
      hints_list = if kind == UserHint then rule:hints_list else hints_list,
      hints_index = Index.insert hint rule hints_index,
      hints_next = hints_next + 1 } }
  where
    args = usort (vars hint)

    hintTerm = build (app (cfg_hint_func hints_next cost) (map var args))

    -- A rule expressing applying the hint. Uses a dummy value for the proof
    -- field since this rule should never be used in a proof anyway. 
    rule = Rule Oriented (certify (Proof.Refl hintTerm)) hint hintTerm

-- Add various kiknds of derived hints.
{-# INLINEABLE addHintsRulePairs #-}
addHintsRulePairs :: Function f => Config f -> Active f -> State f -> State f
addHintsRulePairs config active state =
  foldl' (\state rule -> addHintRulePairs config rule active state) state (hints_list (st_hints state))

{-# INLINEABLE addHintRulesPairs #-}
addHintRulesPairs :: Function f => Config f -> Rule f -> State f -> State f
addHintRulesPairs config rule state =
  foldl' (\state active -> addHintRulePairs config rule active state) state (IntMap.elems (st_active_set state))

{-# INLINEABLE addHintRulePairs #-}
addHintRulePairs :: Function f => Config f -> Rule f -> Active f -> State f -> State f
addHintRulePairs config rule active state =
  foldl' considerOverlap state (overlaps (Index.empty :: Index f (Rule f)) [makeActive rule] active)
    where
      -- hack: need to turn the turn into an Active to invoke 'overlaps'
      makeActive rule = Active 0 (Info (Depth 0) IntSet.empty) rule Nothing (rule_proof rule) (modelFromOrder []) (positionsRule rule)
      considerOverlap state Overlap{..} = considerNorm (simplifyTerm state) t u state
        where
          t = eqn_lhs overlap_eqn
          u = eqn_rhs overlap_eqn

      -- t: term we are considering adding a hint for
      -- u: version of the term where perhaps a hint has already been added
      considerNorm norm t u state
        | st > su =
        {-
          trace ("rule: " ++ prettyShow rule) $
          trace ("active: " ++ prettyShow (active_id active)) $
          trace ("term: " ++ prettyShow t) $
          trace ("norm first: " ++ prettyShow t' ++ " (cost " ++ show st ++ ")") $
          trace ("hint first: " ++ prettyShow u' ++ " (cost " ++ show su ++ ")") $
        -}
          addHint' config state t' DerivedHint su
        | otherwise = state
        where
          t' = norm t
          u' = norm u
          st = scoreTerm config (st_hints state) t'
          su = scoreTerm config (st_hints state) u'

{-# INLINEABLE addHintHintsPairs #-}
addHintHintsPairs :: Function f => Config f -> Rule f -> State f -> State f
addHintHintsPairs _ _ state = state

----------------------------------------------------------------------
-- Equation hints (Veroff-style).
--
-- A hint is an equation. A critical pair whose (simplified) equation is
-- a variant of a hint, in either orientation, gets a very low score, so
-- that it is selected almost at once. Hints are kept normalised with
-- respect to the oriented rules (like Prover9's back_demod_hints), and
-- every normal form a hint has had is remembered, since queued critical
-- pairs were simplified at different times.
----------------------------------------------------------------------

data EqHints f =
  EqHints {
    -- canonical variants (both orientations) of all forms of all hints
    eh_map       :: !(Map (Equation f) Int),
    -- current form of each live (not yet joinable) hint
    eh_live      :: !(IntMap (Equation f)),
    -- hints that a new rule has matched
    eh_matched   :: !IntSet,
    -- number of hints added
    eh_next      :: !Int,
    -- hints that became joinable by normalisation
    eh_joined    :: !Int,
    -- value of st_next_active when hints were last normalised
    eh_norm_at   :: !Id,
    -- fingerprints of all forms of all hints
    eh_fps       :: !IntSet,
    -- goal constants: flattening constants (with their definitions)
    -- and skolem constants (Nothing), keyed by symbol id
    eh_goalconsts :: !(IntMap (Maybe (Term f))),
    -- fingerprint contributions of goal constants
    eh_gcfps :: !(IntMap Int),
    eh_ntracked :: !Int,
    -- number of matched hints at the last hint-triggered queue simplification
    eh_requeued_at :: !Int,
    eh_last_match :: !Int,
    eh_max_gap :: !Int,
    -- ProofWatch: the source proofs (groups) of each hint, the number of
    -- hints of each group, and how many of them have been matched
    eh_hgroups :: !(IntMap [Int]),
    eh_gsize :: !(IntMap Int),
    eh_gdone :: !(IntMap Int),
    -- per-hint score factors (overriding cfg_eqhint_factor)
    eh_factor :: !(IntMap Float) }
  deriving (Generic, Binary)

-- | Hints numbered from here on are only tracked (reported when a rule
-- matches them), they do not change scores.
trackBase :: Int
trackBase = 1000000

-- | Add a tracked hint (see 'trackBase').
{-# INLINEABLE addTrackedHint #-}
addTrackedHint :: Function f => State f -> Equation f -> State f
addTrackedHint state eqn =
  let eh = st_eqhints state
      n = eh_next eh
      state' = addEqHint state{st_eqhints = eh{eh_next = trackBase + eh_ntracked eh}} eqn
      eh' = st_eqhints state'
  in state'{st_eqhints = eh'{eh_next = n, eh_ntracked = eh_ntracked eh + 1}}

emptyEqHints :: EqHints f
emptyEqHints = EqHints {
  eh_map = Map.empty, eh_live = IntMap.empty, eh_matched = IntSet.empty, eh_next = 0,
  eh_joined = 0, eh_norm_at = 0, eh_fps = IntSet.empty, eh_goalconsts = IntMap.empty,
  eh_gcfps = IntMap.empty, eh_ntracked = 0, eh_requeued_at = 0, eh_last_match = 0,
  eh_max_gap = 0, eh_hgroups = IntMap.empty, eh_gsize = IntMap.empty, eh_gdone = IntMap.empty,
  eh_factor = IntMap.empty }

-- | Add a hint with an optional factor and the proofs (groups) it comes from.
{-# INLINEABLE addEqHintFull #-}
addEqHintFull :: Function f => State f -> (Equation f, Maybe Float, [Int]) -> State f
addEqHintFull state (eqn, w, gs) =
  let state' = addEqHintWithFactor state (eqn, w)
      eh = st_eqhints state'
  in case lookupEqHint eh eqn of
       Just n | not (null gs), n < trackBase ->
         state' { st_eqhints = eh { eh_hgroups = IntMap.insertWith (\new old -> usort (new ++ old)) n gs (eh_hgroups eh) } }
       _ -> state'

-- | Count the hints of each group (after all hints are added).
finishEqHintGroups :: State f -> State f
finishEqHintGroups state =
  let eh = st_eqhints state
  in state { st_eqhints = eh { eh_gsize = IntMap.fromListWith (+) [ (g, 1) | gs <- IntMap.elems (eh_hgroups eh), g <- gs ] } }

-- | ProofWatch completion of a hint: the best completion ratio of its groups.
hintCompletion :: EqHints f -> Int -> Maybe Float
hintCompletion EqHints{..} n = do
  gs <- IntMap.lookup n eh_hgroups
  guard (not (null gs))
  return $ maximum
    [ fromIntegral (IntMap.findWithDefault 0 g eh_gdone) / fromIntegral (max 1 (IntMap.findWithDefault 1 g eh_gsize))
    | g <- gs ]

-- | Add an equation hint with its own score factor.
{-# INLINEABLE addEqHintWithFactor #-}
addEqHintWithFactor :: Function f => State f -> (Equation f, Maybe Float) -> State f
addEqHintWithFactor state (eqn, Nothing) = addEqHint state eqn
addEqHintWithFactor state (eqn, Just w) =
  let n = eh_next (st_eqhints state)
      state' = addEqHint state eqn
      eh = st_eqhints state'
  in if eh_next eh == n then state'
     else state' { st_eqhints = eh { eh_factor = IntMap.insert n w (eh_factor eh) } }

-- | Tell the hint matcher about goal constants.
setEqHintGoalConsts :: Function f => State f -> IntMap (Maybe (Term f)) -> State f
setEqHintGoalConsts state gcs =
  state { st_eqhints = (st_eqhints state) { eh_goalconsts = gcs, eh_gcfps = fps } }
  where
    -- definitions are ground and mention only skolems and ordinary symbols
    fps = IntMap.map fp gcs
    fp Nothing = varFingerprint
    fp (Just d) = termFingerprint skolemFps d
    skolemFps = IntMap.map (const varFingerprint) (IntMap.filter isNothing gcs)

-- | Replace goal constants: flattening constants by their definitions,
-- skolem constants by fresh variables. Returns Nothing if there are none.
{-# INLINEABLE expandGoalConsts #-}
expandGoalConsts :: Function f => EqHints f -> Equation f -> Maybe (Equation f)
expandGoalConsts EqHints{..} eqn@(t :=: u)
  | IntMap.null eh_goalconsts = Nothing
  | not (any isGoal (subterms t) || any isGoal (subterms u)) = Nothing
  | otherwise = Just (build (ex t) :=: build (ex u))
  where
    isGoal (App f Nil) = IntMap.member (symId f) eh_goalconsts
    isGoal _ = False
    base = 1 + maximum (0 : [ x | V x <- vars eqn ])
    ex (Var x) = var x
    ex (App f ts) =
      case IntMap.lookup (symId f) eh_goalconsts of
        Just (Just d) | Nil <- ts -> ex d
        Just Nothing | Nil <- ts -> var (V (base + symId f))
        _ -> app f (map ex (unpack ts))

-- | Look up an equation among the hints, also after expanding goal constants.
{-# INLINEABLE lookupEqHintG #-}
lookupEqHintG :: Function f => EqHints f -> Equation f -> Maybe Int
lookupEqHintG eh eqn =
  case lookupEqHint eh eqn of
    Just n -> Just n
    Nothing -> expandGoalConsts eh eqn >>= lookupEqHint eh

-- | Add an equation hint.
{-# INLINEABLE addEqHint #-}
addEqHint :: Function f => State f -> Equation f -> State f
addEqHint state@State{st_eqhints = eh@EqHints{..}} eqn
  | eqn_lhs eqn == eqn_rhs eqn = state
  | canonicalise eqn `Map.member` eh_map = state
  | otherwise =
    state {
      st_eqhints = eh {
        eh_map = insertEqHintForms eh_next eqn eh_map,
        eh_fps = IntSet.insert (eqnFingerprint eqn) eh_fps,
        eh_live = IntMap.insert eh_next eqn eh_live,
        eh_next = eh_next + 1 } }

insertEqHintForms :: Function f => Int -> Equation f -> Map (Equation f) Int -> Map (Equation f) Int
insertEqHintForms n (t :=: u) m =
  Map.insertWith (\_ old -> old) (canonicalise (t :=: u)) n $
  Map.insertWith (\_ old -> old) (canonicalise (u :=: t)) n m

-- | Look up an equation among the hints.
{-# INLINE lookupEqHint #-}
lookupEqHint :: Function f => EqHints f -> Equation f -> Maybe Int
lookupEqHint EqHints{..} eqn
  | Map.null eh_map = Nothing
  | otherwise = Map.lookup (canonicalise eqn) eh_map

-- | Adjust the score of a critical pair if it matches a hint.
{-# INLINE eqHintScore #-}
eqHintScore :: Function f => Config f -> State f -> Term f -> Equation f -> Float -> Float
eqHintScore config@Config{..} state top eqn s
  | Map.null (eh_map eh) = s
  | not (goalFingerprint eh eqn `IntSet.member` eh_fps eh) = s
  | Just n <- lookupEqHintG eh eqn, n < trackBase = dbg n "cheap" (hinted n)
  | cfg_eqhint_consider,
    n:_ <- filter (< trackBase) (mapMaybe (lookupEqHintG eh) (considerForms config state top eqn)) = dbg n "consider" (hinted n)
  | cfg_eqhint_fullnorm,
    Just n <- lookupEqHintG eh (fullNormEqn state eqn), n < trackBase = dbg n "full" (hinted n)
  | otherwise = s
  where
    eh = st_eqhints state
    hinted n = cfg_eqhint_weight + s * factor n
    factor n
      | cfg_eqhint_watch > 0, Just c <- hintCompletion eh n =
        cfg_eqhint_watch * (base n / cfg_eqhint_watch) ** c
      | otherwise = base n
    base n = IntMap.findWithDefault cfg_eqhint_factor n (eh_factor eh)
    dbg n kind x
      | cfg_eqhint_debug = Debug.Trace.trace ("HINTCP " ++ show n ++ " " ++ kind ++ " at " ++ show (st_next_active state) ++ ": " ++ prettyShow eqn) x
      | otherwise = x

-- | The rules that 'consider' would make from a critical pair
-- (without ground joining).
{-# INLINEABLE considerForms #-}
considerForms :: Function f => Config f -> State f -> Term f -> Equation f -> [Equation f]
considerForms Config{..} State{..} top eqn =
  case allSteps cfg_join (st_joinable, st_complete) st_rules cp of
    Nothing -> []
    Just cp' -> map cp_eqn (split cp')
  where
    cp = CriticalPair { cp_eqn = eqn, cp_top = Just top, cp_proof = Proof.Refl (eqn_lhs eqn) }

-- | A hash of the multiset of symbols of an equation; invariant under
-- orientation, variable renaming and permutative rewriting.
{-# INLINEABLE eqnFingerprint #-}
eqnFingerprint :: Function f => Equation f -> Int
eqnFingerprint (t :=: u) = termFingerprint IntMap.empty t + termFingerprint IntMap.empty u

-- | Fingerprint of a term; symbols in the table contribute the given
-- value instead (used for goal constants).
{-# INLINE termFingerprint #-}
termFingerprint :: IntMap Int -> Term f -> Int
termFingerprint tbl t = go 0 (Twee.Base.singleton t)
  where
    go !acc Nil = acc
    go !acc ConsSym{hd = Var _, rest = ts} = go (acc + varFingerprint) ts
    go !acc ConsSym{hd = App f _, rest = ts} =
      let !k = symId f in
      go (acc + IntMap.findWithDefault (symFingerprint k) k tbl) ts

varFingerprint :: Int
varFingerprint = 0x5bd1e995

{-# INLINE symFingerprint #-}
symFingerprint :: Int -> Int
symFingerprint z0 =
  let z1 = (z0 `xor` (z0 `shiftR` 30)) * (-4658895280553007687)
      z2 = (z1 `xor` (z1 `shiftR` 27)) * (-7723592293110705685)
  in z2 `xor` (z2 `shiftR` 31)

-- | Fingerprint of an equation after expanding goal constants.
{-# INLINE goalFingerprint #-}
goalFingerprint :: EqHints f -> Equation f -> Int
goalFingerprint EqHints{..} (t :=: u) = termFingerprint eh_gcfps t + termFingerprint eh_gcfps u

-- | Normalise both sides of an equation with all rules (ordered rewriting).
{-# INLINEABLE fullNormEqn #-}
fullNormEqn :: Function f => State f -> Equation f -> Equation f
fullNormEqn State{..} (t :=: u) = nf t :=: nf u
  where
    nf x = result x (normaliseWith (const True) (rewrite reduces (index_all st_rules)) x)

-- | Record that a new active rule matched a hint.
{-# INLINEABLE recordEqHintMatch #-}
recordEqHintMatch :: Function f => Active f -> State f -> State f
recordEqHintMatch active state@State{st_eqhints = eh}
  | Map.null (eh_map eh) = state
  | otherwise =
    case lookupEqHintG eh (unorient (active_rule active)) of
      Nothing -> state
      Just n ->
        message (HintMatched n active) $
        state { st_eqhints = eh { eh_matched = IntSet.insert n (eh_matched eh),
                                  eh_gdone =
                                    if n < trackBase && not (IntSet.member n (eh_matched eh))
                                    then foldl' (\m g -> IntMap.insertWith (+) g 1 m) (eh_gdone eh) (IntMap.findWithDefault [] n (eh_hgroups eh))
                                    else eh_gdone eh,
                                  eh_last_match = if n < trackBase then fromIntegral (active_id active) else eh_last_match eh,
                                  eh_max_gap = if n < trackBase then max (eh_max_gap eh) (fromIntegral (active_id active) - eh_last_match eh) else eh_max_gap eh } }

-- | Normalise all live hints with respect to the oriented rules.
{-# INLINEABLE normaliseEqHints #-}
normaliseEqHints :: Function f => State f -> State f
normaliseEqHints state@State{st_eqhints = eh@EqHints{..}, ..}
  | IntMap.null eh_live || eh_norm_at == st_next_active = state
  | otherwise =
    state {
      st_eqhints = eh {
        eh_live = live', eh_map = map', eh_joined = eh_joined + joined,
        eh_norm_at = st_next_active,
        eh_fps = foldl' (flip IntSet.insert) eh_fps (map eqnFingerprint (IntMap.elems live')) } }
  where
    idx = index_oriented st_rules
    (live', map', joined) = IntMap.foldlWithKey' step (IntMap.empty, eh_map, 0 :: Int) eh_live
    step (live, m, j) n eqn@(t :=: u)
      | t' == u' = (live, m, j+1)
      | t' == t && u' == u = (IntMap.insert n eqn live, addFull m, j)
      | otherwise = (IntMap.insert n (t' :=: u') live, addFull (insertEqHintForms n (t' :=: u') m), j)
      where
        t' = simplify idx t
        u' = simplify idx u
        full@(t'' :=: u'') = fullNormEqn state (t' :=: u')
        addFull m
          | t'' == u'' = m
          | otherwise = insertEqHintForms n full m

-- Apply hints to a term.
applyHints :: Function f => Hints f -> Term f -> Term f
applyHints Hints{..} t =
  {-let u = simplify idx t in
  if t == u then u else traceShow ("hint: " ++ prettyShow t ++ " => " ++ prettyShow u) u-}
  simplify hints_index t

----------------------------------------------------------------------
-- Interreduction.
----------------------------------------------------------------------

-- Simplify all rules.
{-# INLINEABLE interreduce #-}
interreduce :: Function f => Config f -> State f -> State f
interreduce _ state@State{..} | st_simplified_at == st_next_active = state
interreduce config@Config{..} state =
  let
    state' =
      foldl' (interreduce1 config)
        -- Clear out st_joinable, since we don't know which
        -- equations have made use of each active.
        state { st_joinable = Index.empty, st_complete = Index.empty }
        (IntMap.elems (st_active_set state))
    in state' { st_joinable = st_joinable state, st_complete = st_complete state, st_simplified_at = st_next_active state' }

{-# INLINEABLE interreduce1 #-}
interreduce1 :: Function f => Config f -> State f -> Active f -> State f
interreduce1 config@Config{..} state active@Active{..} =
  -- Exclude the active from the rewrite rules when testing
  -- joinability, otherwise it will be trivially joinable.
  case
    joinCriticalPair cfg_join
      (Index.empty, Index.empty) -- (st_joinable state)
      (st_rules (deleteActive state active))
      (Just active_model) (active_cp active)
  of
    Right (_, cps) ->
      flip (addActiveSimp config) active $
      flip (foldl' (\state cp -> consider config state active_info cp)) cps $
      message (DeleteActive active) $
      deleteActive state active
    Left (cp, model)
      | cp_eqn cp `simplerThan` cp_eqn (active_cp active) ->
        flip (addActiveSimp config) active $
        flip (foldl' (\state cp -> consider config state active_info cp)) (split cp) $
        message (DeleteActive active) $
        deleteActive state active
      | model /= active_model ->
        flip (addActiveOnly config) active { active_model = model } $
        deleteActive state active
      | otherwise ->
        state

----------------------------------------------------------------------
-- The main loop.
----------------------------------------------------------------------

data Output m f =
  Output {
    output_message :: Message f -> m () }

{-# INLINE complete #-}
complete :: (Function f, MonadIO m) => Output m f -> Config f -> State f -> m (State f)
complete Output{..} config@Config{..} state =
  flip StateM.execStateT state $ do
    tasks <- sequence
      [newTask 10 (fromIntegral cfg_renormalise_percent / 100) $ do
         state <- StateM.get
         when (shouldSimplifyQueue config state) $ do
           lift $ output_message SimplifyQueue
           StateM.put $! simplifyQueue config state,
       newTask 1 0.02 $ do
         when cfg_complete_subsets $ do
           state <- StateM.get
           let !state' = checkCompleteness config state
           lift $ output_message (NotComplete (st_not_complete state'))
           StateM.put $! state',
       newTask 1 0.05 $ do
         when cfg_simplify $ do
           lift $ output_message Interreduce
           state <- StateM.get
           StateM.put $! simplifySample $! interreduce config state,
       newTask 1 0.02 $ do
          state <- StateM.get
          StateM.put $! recomputeGoals config state,
       newTask 0.02 0.05 $ do
          when cfg_eqhint_normalise $ do
            state <- StateM.get
            StateM.put $! normaliseEqHints state,
       newTask 0.05 cfg_eqhint_requeue $ do
          state <- StateM.get
          let eh = st_eqhints state
          when (cfg_eqhint_requeue > 0 && IntSet.size (eh_matched eh) /= eh_requeued_at eh) $ do
            lift $ output_message SimplifyQueue
            let state' = normaliseEqHints state
            StateM.put $! (simplifyQueue config state') {
              st_eqhints = (st_eqhints state') { eh_requeued_at = IntSet.size (eh_matched eh) } },
       newTask 60 0.01 $ do
          State{..} <- StateM.get
          let !n = Queue.size st_queue
          lift $ output_message (Status n)]

    checkTimeout <-
      case cfg_max_time of
        Nothing -> return (return False)
        Just timeout -> do
          task <- newTask timeout 100 (return ())
          return $ fmap isJust (checkTask task)

    let
      loop = do
        progress <- StateM.state (complete1 config)
        when cfg_always_simplify $ do
          lift $ output_message Interreduce
          state <- StateM.get
          StateM.put $! simplifySample $! interreduce config state
        state <- StateM.get
        lift $ mapM_ output_message (messages state)
        StateM.put (clearMessages state)
        mapM_ checkTask tasks
        timedOut <- checkTimeout
        when (progress && not timedOut) loop

    loop

{-# INLINEABLE complete1 #-}
complete1 :: Function f => Config f -> State f -> (Bool, State f)
complete1 config@Config{..} state
  | fromIntegral (st_next_active state) > cfg_max_rules =
    (False, state)
  | st_considered state >= cfg_max_critical_pairs =
    (False, state)
  | solved state && not cfg_always_complete = (False, state)
  | cfg_eqhint_stall > 0,
    not (Map.null (eh_map (st_eqhints state))),
    fromIntegral (st_next_active state) - eh_last_match (st_eqhints state) > cfg_eqhint_stall =
    (False, state)
  | otherwise =
    case st_random_seed state of
      Nothing -> -- normal mode
        case dequeue config state of
          (Nothing, state) -> (False, state)
          (Just (info, overlap, _, _, passive), state) ->
            (True, (consider config state{st_cur_passive = Just passive} info overlap){st_cur_passive = Nothing})
      Just (ReadShowBinary g) -> -- random mode
        let (g1, g2) = Random.split g in
        let state' = state { st_random_seed = Just (ReadShowBinary g2) } in
        case findCriticalPair config state' g1 of
          Nothing -> (True, state'{st_problem_term = Nothing})
          Just (info, overlap, changed, cf) ->
            let maybeMessage st =
                  case st_problem_term st of
                    Just cf | changed -> message (NewProblemTerm cf) st
                    _ -> st
                state'' = consider config (maybeMessage state'{st_problem_term = Just cf}) info overlap
                progress = st_next_active state' /= st_next_active state'' in
            (True, state''{st_problem_term = if progress then st_problem_term state'' else Nothing})

{-# INLINEABLE findCriticalPair #-}
findCriticalPair :: Function f => Config f -> State f -> QCGen -> Maybe (Info, CriticalPair f, Bool, ConfluenceFailure f)
findCriticalPair config state g = retry `mplus` random
  where
    trace _ x = x
    traceM _ = return ()
    sizes = concat [replicate 10 i | i <- [10,20..100]]

    retry = (hasUNFRetry strat <$> st_problem_term state) >>= toOverlap False >>= return . snd
    random = pickBest randoms
      where
        pickBest =
          listToMaybe . map snd . sortBy (comparing fst) . take (cfg_random_mode_best_of config) . catMaybes
        randoms = unGen (sequence [resize n test | n <- sizes]) g 0

    test = do
      !(t, rs) <- gen
      () <- traceM ("checking " ++ prettyShow t)
      --toOverlap True <$> (hasUNF strat t rs <>) <$> hasUNFRandom strat t
      return $ toOverlap True $ if cfg_random_mode_simple config then hasUNFSimple strat t rs else hasUNF strat t rs

    gen =
      if cfg_random_mode_goal_directed config then
        generateGoalTerm (goalTerms state) (Index.elems (index_all (st_rules state)))
      else do
        t <- generateTerm lhss
        r <- normaliseWith1Random (const True) strat t
        return (t, r)

    strat = basic (rewrite reducesSkolem (index_all (st_rules state)))
    lhss = map lhs (Index.elems (index_all (st_rules state)))

    toOverlap _ UniqueNormalForm{} = Nothing
    toOverlap changed (HasCriticalPair r1 (r2, n) cf) =
    {-
      Debug.Trace.trace
        (prettyShow $
          text "" $$
          text "Problem term before shrinking:" <+> pPrint (cf_orig_term cf) $$
          text "  NF 1:" <+> pPrint (cf_orig_left_term cf) $$
          text "  NF 2:" <+> pPrint (cf_orig_right_term cf)) $
      -}
      trace ("Term " ++ prettyShow (cf_term cf) ++ " has critical pair (" ++ prettyShow r1 ++ ", " ++ prettyShow r2 ++ ", " ++ show n ++ ")") $
      let r2' = renameAvoiding r1 r2 in
      let Just o = overlapAt (How n Forwards Forwards) r1 r2' r1 r2' in
      case simplifyOverlap (index_all (st_rules state)) o of
        Nothing ->
          trace ("Overlap " ++ prettyShow (overlap_eqn o) ++ " was spurious") Nothing -- should be rare
        Just o' ->
          Just (scoreCP config (Depth 0) (st_hints state) (overlap_eqn o'), (Info (Depth 0) IntSet.empty, makeCriticalPair o, changed, cf))

-- Return all goal terms. Handles the $equals coding.
goalTerms :: Function f => State f -> [Term f]
goalTerms state =
  -- Goals that are not related to $equals.
  [ t
  | eqn <- map goal_eqn (st_goals state),
    t <- concatMap unpack (terms eqn), 
    True ]
{-
    not (isTrueTerm t), not (isFalseTerm t)] ++
  -- Axioms of the form $equals(t, u) = $false.
  [ goalTerm
  | t :=: u <- map axiom_eqn (st_axioms state),
    (lhs, rhs) <- maybeToList $
      if isFalseTerm t then decodeEquality u 
      else if isFalseTerm u then decodeEquality t
      else Nothing,
    goalTerm <- [t, u] ]
-}


{-# INLINEABLE solved #-}
solved :: Function f => State f -> Bool
solved = not . null . solutions

-- Return whatever goals we have proved and their proofs.
{-# INLINEABLE solutions #-}
solutions :: Function f => State f -> [ProvedGoal f]
solutions State{..} = do
  Goal{goal_lhs = ts, goal_rhs = us, ..} <- st_goals
  let sols = Map.keys (Map.intersection ts us)
  guard (not (null sols))
  let sol:_ = sols
  let t = ts Map.! sol
      u = us Map.! sol
      -- Strict so that we check the proof before returning a solution
      !p =
        Proof.certify $
          expandedProof goal_expanded_lhs t `Proof.trans`
          Proof.symm (expandedProof goal_expanded_rhs u)
  return (provedGoal goal_number goal_name p)
  where
    expandedProof m (t, red) =
      m Map.! t `Proof.trans` reductionProof t red

-- Return all current rewrite rules.
{-# INLINEABLE rules #-}
rules :: Function f => State f -> [Rule f]
rules = map active_rule . IntMap.elems . st_active_set

----------------------------------------------------------------------
-- For code which uses twee as a library.
----------------------------------------------------------------------

{-# INLINEABLE completePure #-}
completePure :: Function f => Config f -> State f -> State f
completePure cfg state
  | progress = completePure cfg (clearMessages state')
  | otherwise = state'
  where
    (progress, state') = complete1 cfg state

{-# INLINEABLE normaliseTerm #-}
normaliseTerm :: Function f => State f -> Term f -> Reduction f
normaliseTerm State{..} t =
  normaliseWith (const True) (rewrite reduces (index_all st_rules)) t

{-# INLINEABLE normalForms #-}
normalForms :: Function f => State f -> Term f -> Map (Term f) (Reduction f)
normalForms State{..} t =
  Map.map snd $
  Rule.normalForms (rewrite reduces (index_all st_rules)) (Map.singleton t [])

{-# INLINEABLE simplifyTerm #-}
simplifyTerm :: Function f => State f -> Term f -> Term f
simplifyTerm State{..} t =
  simplify (index_oriented st_rules) t
