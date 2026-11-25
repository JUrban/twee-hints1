{-# LANGUAGE CPP, RecordWildCards, FlexibleInstances, PatternGuards, DeriveAnyClass, RankNTypes, ApplicativeDo, DeriveGeneric #-}
{-# OPTIONS_GHC -flate-specialise #-}
module SequentialMain(main, Constant(..)) where

import Control.Monad
import Data.Char
import Data.Either
import Twee hiding (message)
import Twee.Enigma
import Twee.Base hiding (char, lookup, vars, ground)
--import qualified Twee.Base as Twee
import Twee.Rule(lhs, rhs, unorient)
import Twee.Equation
import qualified Twee.Proof as Proof
import Twee.Proof hiding (Config, defaultConfig)
import qualified Twee.Join as Join
import Twee.Utils
import qualified Twee.CP as CP
import Data.Ord
import Data.Map(Map)
import qualified Data.Map.Strict as Map
import qualified Twee.KBO as KBO
#ifdef USE_LPO
import qualified Twee.LPO as LPO
#endif
import Data.List.Split
import Data.List
import Data.Maybe
import Jukebox.Options
import Jukebox.Toolbox
import qualified Jukebox.Name as Jukebox
import Jukebox.Name hiding (lhs, rhs, label)
import qualified Jukebox.Form as Jukebox
import Jukebox.Form hiding ((:=:), Var, Symbolic(..), Term, Axiom, size, Subst, subst)
import Jukebox.Tools.EncodeTypes
import Jukebox.TPTP.Print
import Jukebox.Tools.HornToUnit
import qualified Data.IntMap.Strict as IntMap
import qualified Data.IntSet as IntSet
import qualified Data.BatchedQueue as Queue
import System.IO
import System.CPUTime (getCPUTime)
import System.Exit
import qualified Data.Set as Set
import qualified Data.Intern as Intern
import Data.Intern(symId)
import System.Console.ANSI
import Data.Symbol
import Twee.Profile
import GHC.Generics
import Data.Hashable
import Data.Binary.Sharing
import qualified Data.ByteString.Lazy as BS
import System.Process
import qualified Jukebox.TPTP.Parse.Core as TPTP
import qualified Jukebox.TPTP.ParseSnippet as Snippet

data MainFlags =
  MainFlags {
    flags_proof :: Bool,
    flags_proof_on_saturation :: Bool,
    flags_proof_all_rules :: Bool,
    flags_trace :: Maybe (String, String),
    flags_formal_proof :: Bool,
    flags_explain_encoding :: Bool,
    flags_flip_ordering :: Bool,
    flags_give_up_on_saturation :: Bool,
    flags_hint_goals :: Bool,
    flags_flatten_goals :: Bool,
    flags_flatten_nonground :: Bool,
    flags_flatten_goals_lightly :: Bool,
    flags_flatten_all :: Bool,
    flags_flatten_regeneralise :: Bool,
    flags_flatten_every :: Int,
    flags_eliminate :: [String],
    flags_backwards_goal :: Int,
    flags_flatten_backwards_goal :: Int,
    flags_equals_transformation :: Bool,
    flags_distributivity_heuristic :: Bool,
    flags_kbo_weight0 :: Bool,
    flags_kbo_weight0_unary :: Bool,
    flags_goal_heuristic :: Bool,
    flags_funweight :: Float,
    flags_dump_proof :: Maybe FilePath,
    flags_dump_state :: Maybe FilePath,
    flags_load_state :: Maybe FilePath,
    flags_resume_requeue :: Bool,
    flags_print_given_unsolved :: Bool,
    flags_stitch :: Maybe FilePath,
    flags_print_hints :: Bool,
    flags_print_hint_matchers :: Bool,
    flags_print_goal_nf :: Int,
    flags_hints_file :: Maybe FilePath,
    flags_track_hints :: Maybe FilePath,
    flags_rule_model :: Maybe FilePath,
    flags_pg_model :: Maybe FilePath,
    flags_pg_enigma :: Int,

    flags_rule_vocab :: Maybe FilePath,
    flags_rule_goal :: Maybe FilePath,
    flags_rule_threshold :: Double,
    flags_rule_penalty :: Float,
    flags_rule_defer_max :: Int,
    flags_rule_debug :: Bool }

parseMainFlags :: OptionParser MainFlags
parseMainFlags = do
  let argModule = arg "<module>" "expected a Prolog module name" Just
  flags_proof <-
    inGroup "Output options" $
    bool "proof" ["Produce proofs (on by default)."]
    True
  flags_proof_on_saturation <-
    expert $
    inGroup "Output options" $
    bool "proof-on-saturation" ["Produce proofs of all rewrite rules on saturation (off by default)."]
    False
  flags_proof_all_rules <-
    expert $
    inGroup "Output options" $
    bool "proof-all-rules" ["Produce proofs of all rewrite rules (off by default)."]
    False
  flags_trace <-
    expert $
    inGroup "Output options" $
    flag "trace"
      ["Write a Prolog-format execution trace to this file (off by default)."]
      Nothing ((\x y -> Just (x, y)) <$> argFile <*> argModule)
  flags_formal_proof <-
    expert $
    inGroup "Output options" $
    bool "formal-proof" ["Print proof as formal TSTP derivation (requires --tstp; off by default)."] False
  flags_explain_encoding <-
    expert $
    inGroup "Output options" $
    bool "explain-encoding" ["In CASC mode, explain the conditional encoding (off by default)."] False
  flags_flip_ordering <-
    expert $
    inGroup "Term order options" $
    bool "flip-ordering" ["Make more common function symbols smaller (off by default)."] False
  flags_kbo_weight0 <-
    expert $
    inGroup "Term order options" $
    bool "kbo-weight0" ["Give functions of arity >= 2 a weight of 0."] False
  flags_kbo_weight0_unary <-
    expert $
    inGroup "Term order options" $
    bool "kbo-weight0-unary" ["Give one function of arity 1 a weight of 0."] True
  flags_give_up_on_saturation <-
    expert $
    inGroup "Output options" $
    bool "give-up-on-saturation" ["Report SZS status GiveUp rather than Unsatisfiable on saturation (off by default)."] False
  flags_hint_goals <-
    expert $
    inGroup "Completion heuristics" $
    bool "hint-goal" ["Add hints representing goal terms (off by default)."] False
  flags_flatten_goals <-
    expert $
    inGroup "Completion heuristics" $
    bool "flatten-goal" ["Flatten goal by adding new axioms (on by default)."] True
  flags_flatten_nonground <-
    expert $
    inGroup "Completion heuristics" $
    bool "flatten-nonground" ["Flatten even non-ground clauses (off by default)."] False
  flags_flatten_goals_lightly <-
    expert $
    inGroup "Completion heuristics" $
    bool "flatten-goal-lightly" ["Flatten goal non-recursively by adding new axioms (off by default)."] False
  flags_flatten_all <-
    expert $
    inGroup "Completion heuristics" $
    bool "flatten" ["Flatten all clauses by adding new axioms (off by default)."] False
  flags_flatten_every <-
    expert $
    inGroup "Completion heuristics" $
    flag "flatten-every" ["Flatten only every nth subterm (default = 1)."] 1 argNum
  flags_flatten_regeneralise <-
    expert $
    inGroup "Completion heuristics" $
    bool "flatten-regeneralise" ["Regeneralise rules involving flattened goal terms (off by default)."] False
  flags_backwards_goal <-
    expert $
    inGroup "Completion heuristics" $
    flag "backwards-goal" ["Try rewriting backwards from the goal this many times (0 by default)."] 0 argNum
  flags_flatten_backwards_goal <-
    expert $
    inGroup "Completion heuristics" $
    flag "flatten-backwards-goal" ["Try rewriting backwards from the goal this many times when flattening (0 by default)."] 0 argNum
  flags_equals_transformation <-
    expert $
    inGroup "Completion heuristics" $
    bool "equals-transformation" ["Apply the 'equals transformation' even to ground goals (off by default)."] False
  flags_distributivity_heuristic <-
    expert $
    inGroup "Completion heuristics" $
    bool "distributivity-heuristic" ["Treat distributive operators specially (off by default)."] False
  flags_goal_heuristic <-
    expert $
    inGroup "Completion heuristics" $
    bool "goal-heuristic" ["Use the CP weighting heuristic from Anantharaman and Andrianarievelo (off by default)."] False
  flags_eliminate <-
    inGroup "Proof presentation" $
    concat <$>
    manyFlags "eliminate"
      ["Treat these axioms as definitions and eliminate them from the proof.",
       "The axiom must have the shape f(x1...xn) = t, where x1...xn are",
       "distinct variables. The term f must not otherwise appear in the problem!",
       "This is not checked."]
      (splitOn "," <$> arg "<axioms>" "expected a list of axiom names" Just)
  flags_funweight <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "fun-weight" ["Weight given to function symbols"] 1 argNum
  flags_dump_proof <-
    expert $
    inGroup "Debugging options" $
    flag "dump-proof"
      ["Dump a binary proof to this file (off by default)."]
      Nothing (Just <$> argFile)
  flags_dump_state <-
    expert $
    inGroup "Debugging options" $
    flag "dump-state"
      ["Dump prover state to this file on termination, unless the problem was solved (off by default)."]
      Nothing (Just <$> argFile)
  flags_load_state <-
    expert $
    inGroup "Debugging options" $
    flag "load-state"
      ["Resume from a state written by --dump-state for the same problem; hints given now replace the old ones."]
      Nothing (Just <$> argFile)
  flags_resume_requeue <-
    expert $
    inGroup "Debugging options" $
    bool "resume-requeue"
      ["With --load-state and hints: re-score the whole saved queue against the new hints (costly for big states)."]
      True
  flags_print_given_unsolved <-
    expert $
    inGroup "Debugging options" $
    bool "print-given-unsolved"
      ["With --print-given: print the given rules also when the problem is not solved (for the hint generator, hints/gen.py)."]
      False
  flags_stitch <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "stitch"
      ["Path to 'stitch' tool for discovering abstractions (disabled by default)."]
      Nothing (Just <$> argFile)
  flags_hints_file <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "hints-file"
      ["File of equation hints, one 'lhs<TAB>rhs' per line, in TPTP term syntax (none by default)."]
      Nothing (Just <$> argFile)
  flags_track_hints <-
    expert $
    inGroup "Debugging options" $
    flag "track-hints"
      ["File of equations (as for --hints-file) to report when a rule matches them, without changing the search."]
      Nothing (Just <$> argFile)
  flags_print_hints <-
    expert $
    inGroup "Output options" $
    bool "print-hints"
      ["On success, print all lemmas of the raw proof as hints (off by default)."]
      False
  flags_print_hint_matchers <-
    expert $
    inGroup "Output options" $
    bool "print-hint-matchers"
      ["Print each rule that matches a hint, as it is added (a HINTMATCHER line with a TPTP clause), for Veroff's P9loop: the matchers of a failed run become lemmas of the next."]
      False
  flags_print_goal_nf <-
    expert $
    inGroup "Output options" $
    flag "print-goal-nf"
      ["When the goal is not proved, print the N smallest normal forms of each side of each goal (GOALNF L|R lines with a TPTP clause t = t), for subgoal conjectures (0 by default)."]
      0 argNum
  flags_rule_model <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "rule-model"
      ["LightGBM model (text) predicting whether a new rule is useful; rules predicted useless are deferred once."]
      Nothing (Just <$> argFile)
  flags_pg_model <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "pg-model"
      ["Parental model for --pg-threshold: a LightGBM forest (hints/lgb2bin.py format, hints/pgtrain.py) on the two rules' features (twee's pgRuleFeatures, side by side, and the id gap) in place of the sum of their --rule-model scores. An additive forest (each tree on one rule's features) is scored once per rule."]
      Nothing (Just <$> argFile)
  flags_pg_enigma <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "pg-enigma" ["--pg-model is a Pcat model on hashed ENIGMA features (FroCoS 2021) with this hash base B: the new rule's and the partner's ENIGMA features (computed as the rule model's, on the rule with the goal constants expanded) hashed to B buckets each, then both rules' 10 features and the id gap (hints/pgtrain_enigma.py; 0 = not an ENIGMA model)."] 0 argNum
  flags_rule_vocab <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "rule-vocab" ["Feature vocabulary of --rule-model (column<TAB>name lines)."] Nothing (Just <$> argFile)
  flags_rule_goal <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "rule-goal" ["Goal features for --rule-model (column<TAB>value lines, and K<TAB>feature lines for overlap)."] Nothing (Just <$> argFile)
  flags_rule_threshold <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "rule-threshold" ["Defer new rules whose predicted probability is below this (default 0.1)."] 0.1 argNum
  flags_rule_penalty <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "rule-penalty" ["Score factor for deferred rules (default 2)."] 2 argNum
  flags_rule_defer_max <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "rule-defer-max" ["Defer each critical pair at most this many times (default 1)."] 1 argNum
  flags_rule_debug <-
    expert $
    inGroup "Debugging options" $
    bool "rule-debug" ["Trace the predictions of --rule-model."] False

  return MainFlags{..}

parseConfig :: OptionParser (Config Constant)
parseConfig = do
  cfg_accept_term <-
    let checkSize n t = KBO.size (t :: Term Constant) <= n in
    inGroup "Resource limits" $
    flag "max-term-size" ["Discard rewrite rules whose left-hand side is bigger than this limit (unlimited by default)."] Nothing (Just <$> checkSize <$> argNum)
  cfg_max_critical_pairs <-
    inGroup "Resource limits" $
    flag "max-cps" ["Give up after considering this many critical pairs (unlimited by default)."] maxBound argNum
  cfg_max_cp_depth <-
    inGroup "Resource limits" $
    flag "max-cp-depth" ["Only consider critical pairs up to this depth (unlimited by default)."] maxBound argNum
  cfg_max_rules <-
    inGroup "Resource limits" $
    flag "max-rules" ["Give up after generating this many rules (unlimited by default)."] maxBound argNum
  cfg_max_time <-
    inGroup "Resource limits" $
    flag "max-time" ["Give up after running for this long in seconds (unlimited by default)."] Nothing (Just <$> argNum)
  cfg_abstract_time <-
    inGroup "Resource limits" $
    flag "abstract-time" ["Count time in critical pairs considered: this many make one second, for --max-time and housekeeping tasks (0 = CPU time, the default). Runs then do not depend on machine load."] 0 argNum
  cfg_simplify <-
    expert $
    inGroup "Completion heuristics" $
    bool "simplify"
      ["Simplify rewrite rules with respect to one another (on by default)."]
      True
  cfg_renormalise_percent <-
    expert $
    inGroup "Completion heuristics" $
    defaultFlag "normalise-queue-percent" "Percent of time spent renormalising queued critical pairs" cfg_renormalise_percent argNum
  cfg_cp_sample_size <-
    expert $
    inGroup "Completion heuristics" $
    defaultFlag "cp-sample-size" "Size of random CP sample used to trigger renormalisation" cfg_cp_sample_size argNum
  cfg_renormalise_threshold <-
    expert $
    inGroup "Completion heuristics" $
    defaultFlag "cp-renormalise-threshold" "Trigger renormalisation when this percentage of CPs can be simplified" cfg_renormalise_threshold argNum
  cfg_set_join_goals <-
    expert $
    inGroup "Critical pair joining heuristics" $
    bool "set-join-goals"
      ["Compute all normal forms when joining goal terms (on by default)."]
      True
  cfg_always_simplify <-
    expert $
    inGroup "Debugging options" $
    bool "always-simplify"
      ["Interreduce rules after every step."]
      False
  cfg_complete_subsets <-
    expert $
    inGroup "Critical pair joining heuristics" $
    bool "complete-subsets"
      ["Identify and exploit complete subsets of the axioms in joining (off by default)."]
      False
  let cfg_hint_func i x = Intern.intern (Hint i x)

  cfg_join <- do
    cfg_ground_join <-
      expert $
      inGroup "Critical pair joining heuristics" $
      bool "ground-joining"
        ["Test terms for ground joinability (on by default)."]
        True
    cfg_use_connectedness_standalone <-
      expert $
      inGroup "Critical pair joining heuristics" $
      bool "connectedness"
        ["Test terms for subconnectedness, as a separate check (on by default)."]
        True
    cfg_use_connectedness_in_ground_joining <-
      expert $
      inGroup "Critical pair joining heuristics" $
      bool "ground-connectedness"
        ["Test terms for subconnectedness, as part of ground joinability testing (off by default)."]
        False
    cfg_set_join <-
      expert $
      inGroup "Critical pair joining heuristics" $
      bool "set-join"
        ["Compute all normal forms when joining critical pairs (off by default)."]
        False
    cfg_ground_join_limit <-
      inGroup "Critical pair joining heuristics" $
      flag "ground-joining-limit" ["Assume not ground joinable after considering this many orderings (unlimited by default)."] maxBound argNum
    cfg_ground_join_incomplete_limit <-
      inGroup "Critical pair joining heuristics" $
      flag "ground-joining-incomplete-limit" ["Assume ground joinable after considering this many orderings (unlimited by default)."] maxBound argNum
    cfg_ground_join_branch_limit <-
      inGroup "Critical pair joining heuristics" $
      flag "ground-joining-branch-limit" ["Assume not ground joinable when the case split has more than this many branches (unlimited by default)."] maxBound argNum
    return Join.Config{..}

  cfg_proof_presentation <- do
    cfg_all_lemmas <-
      inGroup "Proof presentation" $
      bool "all-lemmas"
        ["Produce a proof with one lemma for each critical pair (off by default)."]
        False
    cfg_no_lemmas <-
      inGroup "Proof presentation" $
      bool "no-lemmas"
        ["Produce a proof with no lemmas (off by default).",
         "May lead to exponentially large proofs."]
        False
    cfg_ground_proof <-
      inGroup "Proof presentation" $
      bool "ground-proof"
        ["Produce a ground proof (off by default).",
         "May lead to exponentially large proofs."]
        False
    cfg_show_instances <-
      inGroup "Proof presentation" $
      bool "show-instances"
        ["Show which instance of a lemma or axiom each rewrite step uses (off by default)."]
        False
    cfg_use_colour <-
      let
        colourFlag =
          inGroup "Proof presentation" $
          primFlag "(no-)colour"
            ["Produce output in colour (on by default if writing output to a terminal)."]
            (`elem` map fst colourFlags)
            (\_ y -> return y)
            Nothing
            (pure (`lookup` colourFlags))
        colourFlags = [("--colour", True), ("--no-colour", False),
                       ("--color", True), ("--no-color", False)]
        colourSupported =
          liftM2 (&&) (hSupportsANSIColor stdout)
            (return (setSGRCode [] /= "")) -- Check for Windows terminal not supporting ANSI
      in fromMaybe <$> io colourSupported <*> colourFlag

    cfg_show_uses_of_axioms <-
      let interpret xss ax = axiom_name ax `elem` xss || "all" `elem` xss in
      inGroup "Proof presentation" $
      interpret <$>
      concat <$>
      manyFlags "show-uses-of"
        ["Show which instances of the given axioms were needed (none by default).",
         "Separate multiple axiom names with commas.",
         "Use --show-uses-of all to show uses of all axioms."]
        (splitOn "," <$> arg "<axioms>" "expected a list of axiom names" Just)

    cfg_show_peaks <-
      inGroup "Proof presentation" $
      bool "show-peaks"
        ["Show peak terms in a proof (off by default)."]
        False
    cfg_eliminate_existentials_coding <-
      inGroup "Proof presentation" $
      bool "eliminate-existentials-coding"
        ["Eliminate $equals from proofs (on by default)."]
        True
    cfg_show_subterms <-
      inGroup "Proof presentation" $
      bool "show-subterms"
        ["Show which subterm is rewritten at each step (off by default)."]
        False

    return Proof.Config{..}

  let cfg_eliminate_axioms = [] -- filled in later

  cfg_random_mode <-
    expert $
    inGroup "Completion heuristics" $
    bool "random-mode"
      ["Use random testing to find suitable CPs (doesn't work yet!) (off by default)."]
      False
  cfg_random_mode_goal_directed <-
    expert $
    inGroup "Completion heuristics" $
    bool "random-mode-goal-directed"
      ["Use goal-direction in --random-mode (off by default)."]
      False
  cfg_random_mode_simple <-
    expert $
    inGroup "Completion heuristics" $
    bool "random-mode-simple"
      ["Use simple version of --random-mode (off by default)."]
      False
  cfg_random_mode_best_of <-
    inGroup "Completion heuristics" $
    defaultFlag "random-mode-best-of" "Generate this many critical pairs at a time and pick the best one" cfg_random_mode_best_of argNum
  cfg_always_complete <-
    inGroup "Input and clausifier options" $
    bool "complete"
      ["Don't stop until the rewrite system is confluent"]
      False
  cfg_multi_goal <-
    inGroup "Input and clausifier options" $
    bool "multi-goal"
      ["With several negated conjectures: print SOLVEDGOAL for each goal as it is proved, stop when all are (or at the limits)"]
      False
  cfg_hint_skel_cost <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "hint-skel-cost" "Size of hint skeletons" cfg_hint_skel_cost argNum
  cfg_hint_skel_factor <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "hint-skel-factor" "Size factor of hint skeletons" cfg_hint_skel_factor argNum
  cfg_eqhint_factor <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "eqhint-factor" "Score factor for critical pairs matching an equation hint" cfg_eqhint_factor argNum
  cfg_eqhint_weight <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "eqhint-weight" "Score added to critical pairs matching an equation hint" cfg_eqhint_weight argNum
  cfg_eqhint_normalise <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "eqhint-normalise"
      ["Keep equation hints normalised by the oriented rules (on by default)."]
      True
  cfg_eqhint_fullnorm <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "eqhint-fullnorm"
      ["Also match equation hints after normalising critical pairs with all rules (off by default)."]
      False
  cfg_eqhint_consider <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "eqhint-consider"
      ["Match equation hints against the rule a critical pair would become, if its symbols match a hint (on by default)."]
      True
  cfg_eqhint_consider_open <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "eqhint-consider-open"
      ["Consider-emulation only for critical pairs with the fingerprint of a hint no rule has matched yet (off by default)."]
      False
  cfg_eqhint_generalise <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "eqhint-generalise" ["Also match critical pairs that generalise a hint (one subterm replaced by a variable)."] False
  cfg_eqhint_instances <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "eqhint-instances" ["Also match critical pairs that are instances of a hint (term index over the hints' sides; score factor --eqhint-instance-factor)."] False
  cfg_eqhint_subsume <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "eqhint-subsume" ["Prover9's hint matching: a critical pair or rule also matches a hint it subsumes (the hint is an instance of it), not only a variant of it."] False
  cfg_eqhint_instance_factor <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "eqhint-instance-factor" "Score factor of critical pairs that are instances of a hint (--eqhint-instances)" cfg_eqhint_instance_factor argNum
  cfg_cp_model_factor <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "cp-model-factor" "Score factor F ** q of each critical pair, q = the --rule-model probability that it is a proof rule (1 = off)" cfg_cp_model_factor argNum
  cfg_eqhint_watch <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "eqhint-watch" "ProofWatch: score factor of hints whose source proofs are not yet started; it moves to the hint's own factor as its best proof completes (0 = off)" cfg_eqhint_watch argNum
  cfg_eqhint_stall_cps <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "eqhint-stall-cps" "Give up after this many critical pairs considered without a new hint match (0 = never); with --abstract-time N, N per second" cfg_eqhint_stall_cps argNum
  cfg_max_cpu <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "max-cpu" "Real-CPU safety limit in seconds (0 = none); it stops the run like --max-time and prints CPULIMIT; for runs in abstract time" cfg_max_cpu argNum
  cfg_pg_threshold <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    flag "pg-threshold" ["Parental guidance: no critical pairs of a new rule with an active rule when sigmoid of the sum of their --rule-model raw scores is below this probability (off by default). Rules without a score (axioms, rules from interreduction) are always paired."] Nothing (Just <$> argNum)
  cfg_pg_log <-
    expert $
    inGroup "Debugging options" $
    bool "pg-log" ["Trace each new rule's id, parents and --rule-model raw score (PGR lines) and its critical pairs per partner (PGN) on stderr, and on success the proof's lemmas (PGPROOF). Scores every rule."] False
  cfg_overlap_index <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "overlap-index" ["Find overlap partners with a fingerprint index (default: true). The same critical pairs are made in the same order."] True
  cfg_interreduce_filter <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    bool "interreduce-filter" ["Interreduce an old rule only if a rule added since the last interreduction rewrites one of its subterms (default: true)."] True
  cfg_queue_cost <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "queue-cost" "With --abstract-time: renormalising the queue costs this many critical pairs per queued pair (0 = free), so its CPU budget binds" cfg_queue_cost argNum
  cfg_progress <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "progress" "Print a PROGRESS line (critical pairs, rules, CPU time, CPU of housekeeping tasks) every this many seconds, abstract with --abstract-time (0 = never)" cfg_progress argNum
  cfg_eqhint_stall <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "eqhint-stall" "Give up when no rule has matched a hint for this many rules (0 = never)" cfg_eqhint_stall argNum
  cfg_eqhint_requeue <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "eqhint-requeue" "Fraction of time for re-simplifying the queue after new rules match hints" cfg_eqhint_requeue argNum
  cfg_eqhint_debug <-
    expert $
    inGroup "Debugging options" $
    bool "eqhint-debug" ["Trace critical pairs that match equation hints (off by default)."] False
  cfg_log_given <-
    expert $
    inGroup "Output options" $
    bool "print-given" ["On success, print every rule that was added (after --print-hints output)."] False
  cfg_print_score <-
    expert $
    inGroup "Output options" $
    bool "print-score" ["Print score of each generated rule (off by default)."] False
  cfg_cp_config <- parseCPConfig

  return Config{..}
  where
    defaultFlag :: Show a => String -> String -> (Config Constant -> a) -> ArgParser a -> OptionParser a
    defaultFlag name desc field parser =
      flag name [desc ++ " (" ++ show def ++ " by default)."] def parser
      where
        def = field defaultConfig

parseCPConfig :: OptionParser CP.Config
parseCPConfig = do
  cfg_lhsweight <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "lhs-weight" "Weight given to LHS of critical pair" CP.cfg_lhsweight argNum
  cfg_rhsweight <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "rhs-weight" "Weight given to RHS of critical pair" CP.cfg_rhsweight argNum
  cfg_varweight <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "var-weight" "Weight given to variable symbols" CP.cfg_varweight argNum
  cfg_depthweight <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "depth-weight" "Weight given to critical pair depth" CP.cfg_depthweight argNum
  cfg_dupcost <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "dup-cost" "Cost of duplicate subterms" CP.cfg_dupcost argNum
  cfg_dupfactor <-
    expert $
    inGroup "Critical pair weighting heuristics" $
    defaultFlag "dup-factor" "Size factor of duplicate subterms" CP.cfg_dupfactor argNum
  return CP.Config{..}
  where
    defaultFlag name desc field parser =
      flag name [desc ++ " (" ++ show def ++ " by default)."] def parser
      where
        def = field CP.defaultConfig

parsePrecedence :: OptionParser [String]
parsePrecedence =
  expert $
  inGroup "Term order options" $
  fmap (splitOn ",")
  (flag "precedence" ["List of functions in descending order of precedence."] [] (arg "<function>" "expected a function name" Just))

data Constant =
  Minimal |
  Skolem Int |
  Hint Int Float |
  Constant {
    con_prec    :: {-# UNPACK #-} !Precedence,
    con_id      :: {-# UNPACK #-} !Int,
    con_name    :: !String,
    con_arity   :: {-# UNPACK #-} !Int,
    con_label   :: !(Maybe String),
    con_size    :: !Integer,
    con_weight  :: !Integer,
    con_fweight :: {-# UNPACK #-} !Float,
    con_bonus   :: !Bool }
  deriving (Eq, Ord, Generic, Hashable, Binary)

data Precedence = Precedence !Bool !Bool !Bool !(Maybe Int) !Int
  deriving (Eq, Ord, Generic, Hashable, Binary)

instance KBO.Sized Constant where
  size Minimal = 1
  size Skolem{} = 1
  size Hint{} = 1
  size Constant{..} = con_size
instance KBO.ArgWeighted Constant where
  argWeight Minimal = 1
  argWeight Skolem{} = 1
  argWeight Hint{} = 1
  argWeight Constant{..} = con_weight

instance Weighted Constant where
  weight Minimal = 1
  weight (Skolem _) = 1
  weight (Hint _ x) = x
  weight Constant{..} = con_fweight

instance Pretty Constant where
  pPrint Minimal = text "?"
  pPrint (Skolem n) = text ("sk" ++ show n)
  pPrint (Hint n _) = text ("hint" ++ show n)
  pPrint Constant{..} = text (removePostfix con_name)
    where
      removePostfix ('_':x:xs) | con_arity == 1 = x:xs
      removePostfix xs = xs

instance PrettyTerm Constant where
  termStyle Minimal = uncurried
  termStyle Skolem{} = uncurried
  termStyle Hint{} = uncurried
  termStyle Constant{..}
    | con_label == Just "type_tag" = invisible
    | "_" `isPrefixOf` con_name && con_arity == 1 = postfix
    | any isAlphaNum con_name = uncurried
    | otherwise =
      case con_arity of
        1 -> prefix
        2 -> infixStyle 5
        _ -> uncurried

instance Minimal Constant where
  minimal = Sym Minimal
  skolem = Sym . Skolem

#ifdef USE_LPO
instance Ordered Constant where
  lessEq t u = LPO.lessEq t u
  lessIn model t u = LPO.lessIn model t u
  lessEqSkolem t u = LPO.lessEqSkolem t u
#else
instance Ordered Constant where
  lessEq t u = KBO.lessEq t u
  lessIn model t u = KBO.lessIn model t u
  lessEqSkolem t u = KBO.lessEqSkolem t u
#endif

instance EqualsBonus Constant where
  hasEqualsBonus Minimal = False
  hasEqualsBonus Skolem{} = False
  hasEqualsBonus Hint{} = False
  hasEqualsBonus c = con_bonus c

  isEquals Constant{..} = con_label == Just "equals" && con_arity == 2
  isEquals _ = False
  isTrue Constant{..} = con_label == Just "true" && con_arity == 0
  isTrue _ = False
  isFalse Constant{..} = con_label == Just "false" && con_arity == 0
  isFalse _ = False

data TweeContext =
  TweeContext {
    ctx_var     :: Jukebox.Variable,
    ctx_minimal :: Jukebox.Function,
    ctx_true    :: Jukebox.Function,
    ctx_false   :: Jukebox.Function,
    ctx_equals  :: Jukebox.Function,
    ctx_type    :: Type,
    ctx_funs    :: Map Int Jukebox.Function,
    ctx_ids     :: Map Jukebox.Function Int,
    -- Symbols of a state loaded with --load-state, by name and arity. The
    -- current problem reuses them, so that the saved rules, the new axioms
    -- and the hints share one signature (precedence and ids depend on the
    -- problem text, which changes when lemmas are added).
    ctx_saved   :: Map (String, Int) Constant }

-- Convert back and forth between Twee and Jukebox.
tweeConstant :: MainFlags -> HornFlags -> TweeContext -> Precedence -> Jukebox.Function -> Constant
tweeConstant MainFlags{..} flags TweeContext{..} prec fun
  | fun == ctx_minimal = Minimal
  | Just c <- Map.lookup (base (name fun), Jukebox.arity fun) ctx_saved = c
  | otherwise =
    Constant {
      con_prec = prec,
      con_id = Map.findWithDefault (error (show (fun, ctx_ids))) fun ctx_ids,
      con_name = base (name fun),
      con_label = Jukebox.label (name fun),
      con_arity = Jukebox.arity fun,
      con_size = if flags_kbo_weight0 && Jukebox.arity fun >= 2 then 0 else if flags_kbo_weight0_unary && isInv then 0 else 1,
      con_weight = 1,
      con_fweight = flags_funweight,
      con_bonus = bonus fun }
  where
    bonus fun =
      (isIfeq fun && encoding flags /= Asymmetric2) ||
      (Jukebox.label (name fun) == Just "equals" && Jukebox.arity fun == 2)
    isInv =
      case prec of
        Precedence _ x _ _ _ -> x

isType :: Jukebox.Function -> Bool
isType fun =
  hasLabel "type_tag" (name fun) && Jukebox.arity fun == 1

isIfeq :: Jukebox.Function -> Bool
isIfeq fun =
  hasLabel "ifeq" (name fun)

jukeboxFunction :: TweeContext -> Constant -> Jukebox.Function
jukeboxFunction TweeContext{..} Constant{..} =
  case Map.lookup con_id ctx_funs of
    Just f | base (name f) == con_name -> f
    _ -> -- a symbol of a loaded state, whose id is from the saved run
      head ([ f | f <- Map.elems ctx_funs, base (name f) == con_name, Jukebox.arity f == con_arity ] ++
            [error ("jukeboxFunction: " ++ con_name)])
jukeboxFunction TweeContext{..} Minimal = ctx_minimal

-- A raw parsed hint term.
data HTerm = HVar String | HApp String [HTerm]

hVars :: HTerm -> [String]
hVars (HVar x) = [x]
hVars (HApp _ ts) = concatMap hVars ts

parseHTerm :: String -> Maybe (HTerm, String)
parseHTerm s0 =
  case span (\c -> isAlphaNum c || c == '_') (dropWhile isSpace s0) of
    ([], _) -> Nothing
    (nm@(c:_), rest)
      | isUpper c -> Just (HVar nm, rest)
      | otherwise ->
        case dropWhile isSpace rest of
          '(':rest' -> do
            (args, rest'') <- parseArgs rest'
            return (HApp nm args, rest'')
          _ -> Just (HApp nm [], rest)
  where
    parseArgs s = do
      (t, r) <- parseHTerm s
      case dropWhile isSpace r of
        ',':r' -> do
          (ts, r'') <- parseArgs r'
          return (t:ts, r'')
        ')':r' -> return ([t], r')
        _ -> Nothing

tweeTerm :: MainFlags -> HornFlags -> TweeContext -> (Jukebox.Variable -> Int) -> (Jukebox.Function -> Precedence) -> Jukebox.Term -> Term Constant
tweeTerm flags horn ctx varNum prec t = build (tm t)
  where
    tm (Jukebox.Var x) =
      var (V (varNum x))
    tm (f :@: ts) =
      app (Sym (tweeConstant flags horn ctx (prec f) f)) (map tm ts)

jukeboxTerm :: TweeContext -> Term Constant -> Jukebox.Term
jukeboxTerm TweeContext{..} (Var (V x)) =
  Jukebox.Var (Unique (fromIntegral x) (intern "X") Nothing defaultRenamer ::: ctx_type)
jukeboxTerm ctx@TweeContext{..} (App (Sym f) t) =
  jukeboxFunction ctx f :@: map (jukeboxTerm ctx) ts
  where
    ts = unpack t

makeContext :: [Jukebox.Term] -> Problem Clause -> TweeContext
makeContext hints prob = run (hints, prob) $ \(_, prob) -> do
  let
    ty =
      case types' prob of
        []   -> indType
        [ty] -> ty

  var     <- newSymbol "X" ty
  minimal <- newFunction (withLabel "minimal" (name "constant")) [] ty
  true    <- newFunction (withLabel "true" (name "true")) [] ty
  false   <- newFunction (withLabel "false" (name "false")) [] ty
  equals  <- newFunction (withLabel "equals" (name "equals")) [ty, ty] ty

  -- (e61l) the listened goals' own symbols (isListened) are numbered after all others, so the other symbols keep the
  -- numbers they have without the listened goals (and the search of the run's own goal stays the same)
  let mainFuns = usort $ [minimal, true, false, equals] ++
                   Jukebox.functions (hints, [ inp | inp <- prob, not (isQuietGoal (tag inp)) ])
      mainSet = Set.fromList mainFuns
      allFuns = mainFuns ++ filter (`Set.notMember` mainSet) (usort (Jukebox.functions prob))

  return TweeContext {
    ctx_var = var,
    ctx_minimal = minimal,
    ctx_true = true,
    ctx_false = false,
    ctx_equals = equals,
    ctx_type = ty,
    ctx_funs = Map.fromList (zip [0..] allFuns),
    ctx_ids = Map.fromList (zip allFuns [0..]),
    ctx_saved = Map.empty }

-- | (e61l) A listened goal (listen_*, Twee.isListened) or the credit rerun's goal (lgoal_*: climb.py renames a proved
-- listened goal to rerun the same search as a real goal): left out of the precedence count, numbered after all other
-- symbols and not flattened, so the problem's other goal searches exactly as without it
isQuietGoal :: String -> Bool
isQuietGoal t = isListened t || "lgoal_" `isPrefixOf` t

flattenGoals :: Int -> Bool -> Bool -> Bool -> Int -> [Jukebox.Term] -> Problem Clause -> Problem Clause
flattenGoals backwardsGoal flattenNonGround flattenAll full depthMod hints prob =
  run (hints, prob) $ \(_, prob) -> do
    let ts = filter depthOk $ usort $ extraTerms prob
    cs <- mapM define ts
    return (prob ++ cs)
  where
    extraTerms prob = concatMap (input prob) prob
    -- (e61l) a listened goal is not flattened: its definitions would be new axioms, and change the search
    input _ inp | isQuietGoal (tag inp) = []
    input prob Input{what = Clause (Bind _ [Neg (x Jukebox.:=: y)])} =
      concatMap term (backwards backwardsGoal prob x) ++
      concatMap term (backwards backwardsGoal prob y)
    input _ Input{what = Clause (Bind _ [Pos (x Jukebox.:=: y)])}
      | flattenAll = term x ++ term y
    input _ _ = []

    term t@(_f :@: ts) =
      [ t
      | ground t || flattenNonGround,
        not (all isVar ts) || usort ts /= sort ts ] ++
      if full then concatMap term ts else []
    term _ = []

    isVar (Jukebox.Var _) = True
    isVar _ = False

    depthOk t = depthMod == 1 || depth t `mod` depthMod == 0
    depth (_f :@: ts) = 1 + maximum (0:map depth ts)
    depth _ = 1

    define (f :@: ts) = do
      name <- newName f
      let vs  = Jukebox.vars ts
          g = name ::: FunType (map typ vs) (typ f)
          c = clause [Pos (g :@: map Jukebox.Var vs Jukebox.:=: f :@: ts)]
      return Input{ident = Nothing, tag = "flattening", kind = Jukebox.Ax Definition,
                   what = c, source = Unknown }

    backwards 0 _ t = [t]
    backwards n cs t =
      t:
      [ v
      | Input{what = Clause (Bind _ [Pos (x0 Jukebox.:=: y0)])} <- cs,
        (x, y) <- [(x0, y0), (y0, x0)],
        (s, k) <- contexts t,
        sub <- maybeToList (Jukebox.match x s),
        let u = k (Jukebox.subst sub y),
        ground u,
        v <- backwards (n-1) cs u ]

hintGoals :: Problem Clause -> Problem Clause
hintGoals prob =
  prob ++ map define extraTerms
  where
    extraTerms = usort (concatMap input prob)
    input Input{what = Clause (Bind _ [Neg (x Jukebox.:=: y)])} =
      term x ++ term y
    input _ = []

    term t@(_f :@: ts) = t:concatMap term ts
    term _ = []

    define t =
      Input{ident = Nothing, tag = "flattening", kind = Jukebox.Ax Definition, what = c, source = Unknown}
      where
        c = clause [Pos (Tru (hint :@: [t]))]
        hint = name "$hint" ::: FunType [Jukebox.typ t] O

addDistributivityHeuristic :: [Jukebox.Term] -> Problem Clause -> Problem Clause
addDistributivityHeuristic hints prob =
  run (hints, prob) $ \(_, prob) -> do
    cs <- mapM add prob
    return (prob ++ catMaybes cs)

  where
    add Input{what = Clause (Bind _ [Pos (t Jukebox.:=: u)])} =
      case checkDistributivity t u `mplus` checkDistributivity u t of
        Just (f, g, ty) -> do
          name <- newName (base f ++ "_" ++ base g)
          x <- Jukebox.Var <$> newSymbol "X" ty
          y <- Jukebox.Var <$> newSymbol "Y" ty
          z <- Jukebox.Var <$> newSymbol "Z" ty
          Just <$> define name (g :@: [f :@: [x, y], z])
        _ -> return Nothing
    add _ = return Nothing

    checkDistributivity
      (f1 :@: [Jukebox.Var x1, g1 :@: [Jukebox.Var y1, Jukebox.Var z1]])
      (g2 :@: [f2 :@: [Jukebox.Var x2, Jukebox.Var y2],
               f3 :@: [Jukebox.Var x3, Jukebox.Var z2]])
      | f1 == f2 && f2 == f3 && g1 == g2 &&
        x1 == x2 && x2 == x3 && y1 == y2 && z1 == z2 =
        Just (f1, g1, Jukebox.typ x1)
      
    checkDistributivity
      (f1 :@: [g1 :@: [Jukebox.Var x1, Jukebox.Var y1], Jukebox.Var z1])
      (g2 :@: [f2 :@: [Jukebox.Var x2, Jukebox.Var z2],
       f3 :@: [Jukebox.Var y2, Jukebox.Var z3]])
      | f1 == f2 && f2 == f3 && g1 == g2 &&
        x1 == x2 && y1 == y2 && z1 == z2 && z2 == z3 =
        Just (f1, g1, Jukebox.typ x1)
    checkDistributivity _ _ = Nothing

    define name t = do
      let vs  = Jukebox.vars t
          g = name ::: FunType (map typ vs) (typ t)
          c = clause [Pos (g :@: map Jukebox.Var vs Jukebox.:=: t)]
      return Input{ident = Nothing, tag = "distributivity_heuristic", kind = Jukebox.Ax Definition,
                   what = c, source = Unknown }

-- Encode existentials so that all goals are ground.
addNarrowing :: Bool -> TweeContext -> Problem Clause -> Problem Clause
addNarrowing alwaysNarrow TweeContext{..} prob =
  unchanged ++ equalityClauses
  where
    prob' = [inp { ident = Just (variant "addNarrowing" [i :: Int]) } | (i, inp) <- zip [0..] prob]

    (unchanged, nonGroundGoals) = partitionEithers (map f prob')
      where
        f inp@Input{what = Clause (Bind _ [Neg (x Jukebox.:=: y)])}
          | not (ground x) || not (ground y) || alwaysNarrow =
            Right (inp, (x, y))
        f inp = Left inp

    equalityClauses
      | null nonGroundGoals = []
      | otherwise =
        -- Turn a != b & c != d & ...
        -- into eq(a,b)=false & eq(c,d)=false & eq(X,X)=true & true!=false (esa)
        -- and then extract the individual components (thm)
        let
          equalityLiterals =
            -- true != false
            ("true_equals_false", Neg ((ctx_true :@:) [] Jukebox.:=: (ctx_false :@: []))):
            -- eq(X,X)=true
            ("reflexivity", Pos (ctx_equals :@: [Jukebox.Var ctx_var, Jukebox.Var ctx_var] Jukebox.:=: (ctx_true :@: []))):
            -- [eq(a,b)=false, eq(c,d)=false, ...]
            [ (tag, Pos (ctx_equals :@: [x, y] Jukebox.:=: (ctx_false :@: [])))
            | (Input{tag = tag}, (x, y)) <- nonGroundGoals ]

          -- Equisatisfiable to the input clauses
          justification =
            Input {
              ident = Just (name "addNarrowing2"),
              tag  = "new_negated_conjecture",
              kind = Jukebox.Ax NegatedConjecture,
              what =
                let form = And (map (Literal . snd) equalityLiterals) in
                ForAll (Bind (Set.fromList (vars form)) form),
              source =
                inference "encode_existential" "esa"
                  (map (fmap toForm . fst) nonGroundGoals) }

          input tag form i =
            Input {
              ident = Just (variant "addNarrowing3" [i :: Int]),
              tag = tag,
              kind = Jukebox.Ax NegatedConjecture,
              what = clause [form],
              source =
                inference "split_conjunct" "thm" [justification] }

        in [input tag form i | ((tag, form), i) <- zip equalityLiterals [0..]]

data PreEquation =
  PreEquation {
    pre_name :: String,
    pre_form :: Input Form,
    pre_eqn  :: (Jukebox.Term, Jukebox.Term) }

-- Split the problem into axioms and ground goals.
identifyProblem ::
  TweeContext -> Problem Clause -> Either (Input Clause) ([PreEquation], [PreEquation])
identifyProblem TweeContext{..} prob =
  fmap partitionEithers (mapM identify prob)

  where
    pre inp x =
      PreEquation {
        pre_name = tag inp,
        pre_form = fmap toForm inp,
        pre_eqn = x }

    identify inp@Input{what = Clause (Bind _ [Pos (t Jukebox.:=: u)])} =
      return $ Left (pre inp (t, u))
    identify inp@Input{what = Clause (Bind _ [Neg (t Jukebox.:=: u)])}
      | ground t && ground u =
        return $ Right (pre inp (t, u))
    identify inp@Input{what = Clause (Bind _ [])} =
      -- The empty clause can appear after clausification if
      -- the conjecture was trivial
      return $ Left (pre inp (Jukebox.Var ctx_var, ctx_minimal :@: []))
    identify inp = Left inp

runTwee :: GlobalFlags -> TSTPFlags -> HornFlags -> [String] -> Config Constant -> MainFlags -> (IO () -> IO ()) -> [Jukebox.Term] -> Problem Clause -> IO Answer
runTwee globals (TSTPFlags tstp) horn precedence config0 flags@MainFlags{..} later hints obligs = {-# SCC runTwee #-} do
  -- A state to resume is decoded first: the problem must reuse its symbols.
  savedState <-
    case flags_load_state of
      Nothing -> return Nothing
      Just file -> Just . decode <$> BS.readFile file
  let
    savedSyms :: Map (String, Int) Constant
    savedSyms =
      case savedState of
        Nothing -> Map.empty
        Just st -> Map.fromList
          [ ((con_name c, con_arity c), c)
          | Sym c@Constant{} <- funs (map axiom_eqn (st_axioms st)) ++ funs (map goal_eqn (st_goals st)) ]
  let
    -- Encode whatever needs encoding in the problem
    obligs1
      | flags_flatten_goals_lightly = flattenGoals flags_flatten_backwards_goal flags_flatten_nonground False False flags_flatten_every hints obligs
      | flags_flatten_all = flattenGoals flags_flatten_backwards_goal flags_flatten_nonground True True flags_flatten_every hints obligs
      | flags_flatten_goals = flattenGoals flags_flatten_backwards_goal flags_flatten_nonground False True flags_flatten_every hints obligs
      | otherwise = obligs
    obligs2
      | flags_distributivity_heuristic = addDistributivityHeuristic hints obligs1
      | otherwise = obligs1
    lowercaseSkolem x
      | hasLabel "skolem" x =
        withRenamer x $ \s i ->
          case defaultRenamer s i of
            Renaming xss xs ->
              Renaming (map (map toLower) xss) (map toLower xs)
      | otherwise = x
    (hintsAll', prettyObligs) = prettyNames (mapName lowercaseSkolem (hints, obligs2))
    isEqHint (h :@: [_, _]) = base (name h) == "$hinteq"
    isEqHint _ = False
    eqHintFlags = map isEqHint hints
    hints' = [ h | (h, False) <- zip hintsAll' eqHintFlags ]
    eqHints' = [ (t, u) | (_ :@: [t, u], True) <- zip hintsAll' eqHintFlags ]
    ctx = (makeContext hintsAll' prettyObligs) { ctx_saved = savedSyms }
    prob = addNarrowing flags_equals_transformation ctx prettyObligs

  (unsortedAxioms0, goals0) <-
    case identifyProblem ctx prob of
      Left inp -> do
        mapM_ (hPutStrLn stderr) [
          "The problem contains the following clause, which is not a unit equality:",
          indent (show (pPrintClauses [inp])),
          "Twee only handles unit equality problems."]
        exitWith (ExitFailure 1)
      Right x -> return x

  let
    -- Work out a precedence for function symbols
    prec c =
      Precedence
        (isType c)
#ifdef USE_LPO
        ((hasLabel "equals" c && Jukebox.arity c == 2) || isIfeq c)
#else
        (Just c == maxUnary)
#endif
        (isJust (elemIndex (base c) precedence))
        (fmap negate (elemIndex (base c) precedence))
        (maybeNegate (Map.findWithDefault 0 c funOccs))
    maybeNegate = if flags_flip_ordering then negate else id
    -- (e61l) symbol occurrences without the listened goals (isListened): otherwise their terms would change the
    -- precedence, and with it the whole search of the run's own goal
    funOccs = funsOcc [ inp | inp <- prob, not (isQuietGoal (tag inp)) ]
#ifndef USE_LPO
    maxUnary =
      case filter (\(f, _) -> arity f == 1 && not (isType f)) (Map.toList funOccs) of
        [] -> Nothing
        xs -> Just (fst (maximumBy (comparing snd) xs))
#endif

    -- Translate everything to Twee.
    toTerm var t = tweeTerm flags horn ctx var prec t
    varNums :: Jukebox.Symbolic a => a -> Jukebox.Variable -> Int
    varNums t = \x -> Map.findWithDefault undefined x ids
      where
        xs = usort (vars t)
        ids = Map.fromList (zip xs [0..])
    toEquation (t, u) =
      toTerm var t :=: toTerm var u
      where
        var = varNums (t, u)
    equationVars (t, u) =
      Map.fromList [(V n, base (name x)) | x <- vars (t, u), let n = var x]
      where
        var = varNums (t, u)

    axiomCompare ax1 ax2
      | isEquality ax1' && not (isEquality ax2') = GT
      | isEquality ax2' && not (isEquality ax1') = LT
      | ax1' `simplerThan` ax2' = LT
      | ax2' `simplerThan` ax1' = GT
      | otherwise = EQ
      where
        ax1' = toEquation (pre_eqn ax1)
        ax2' = toEquation (pre_eqn ax2)
        isEquality ax = isJust (decodeEquality (eqn_lhs ax)) || isJust (decodeEquality (eqn_rhs ax))
    axioms0 = sortBy axiomCompare unsortedAxioms0

    goals =
      [ goal n pre_name (toEquation pre_eqn)
      | (n, PreEquation{..}) <- zip [1..] goals0 ]
    axioms =
      [ Axiom n pre_name (Just (equationVars pre_eqn)) (toEquation pre_eqn)
      | (n, PreEquation{..}) <- zip [1..] axioms0 ]
    -- Hypotheses of a conditional conjecture: positive unit clauses from the
    -- negated conjecture. They hold only for the skolem constants.
    hyps =
      [ axiom
      | (axiom, PreEquation{..}) <- zip axioms axioms0,
        Input{kind = Jukebox.Ax NegatedConjecture} <- [pre_form] ]
    defs =
      [ axiom
      | (axiom, PreEquation{..}) <- zip axioms axioms0,
        isDefinition pre_form ]
    isDefinition Input{source = Unknown} = True
    isDefinition inp = tag inp `elem` flags_eliminate

  -- Compute CP scoring heuristic
  let
    {-
    goalNests = nests (map goal_eqn goals)
    goalOccs = occs (map goal_eqn goals)
    score depth hints eqn
      | flags_goal_heuristic =
        scoreCP cpConfig depth hints eqn *
        product
          [ pos (IntMap.findWithDefault 0 f eqnNests - IntMap.findWithDefault 0 f goalNests) *
            pos (IntMap.findWithDefault 0 f eqnOccs - IntMap.findWithDefault 0 f goalOccs)
          | f <- IntMap.keys eqnNests ] -- skip constants
      | otherwise = 
        scoreCP cpConfig depth hints eqn
      where
        eqnNests = nests eqn
        eqnOccs = occs eqn

        pos :: Int -> Float
        pos n = if n <= 0 then 1 else fromIntegral n+1
    -}
    config1 = config0 { cfg_eliminate_axioms = if flags_flatten_regeneralise then defs else [] }

  ruleModel <-
    case flags_rule_model of
      Nothing -> return Nothing
      Just mfile -> do
        forest <-
          if ".bin" `isSuffixOf` mfile then parseForestBin <$> BS.readFile mfile
          else parseForest <$> readFile mfile
        vstr <- maybe (return "") readFile flags_rule_vocab
        gstr <- maybe (return "") readFile flags_rule_goal
        let
          vocab = Map.fromList [ (k, read c) | l <- lines vstr, (c, '\t':k) <- [break (== '\t') l] ]
          gls = [ (a, b) | l <- lines gstr, (a, '\t':b) <- [break (== '\t') l] ]
          gcols = [ (read a, read b) | (a, b) <- gls, a /= "K" ]
          gkeys = Set.fromList [ b | ("K", b) <- gls ]
          p = flags_rule_threshold
          conName Constant{..} = con_name
          conName Minimal = "?"
          conName (Skolem _) = "?"
          conName (Hint _ _) = "?"
        return $! length forest `seq` Map.size vocab `seq` Just $ mkRuleModel RuleModel {
          rm_forest = forest, rm_vocab = vocab, rm_goal = gcols, rm_gkeys = gkeys,
          rm_name = conName, rm_threshold = log (p / (1 - p)), rm_penalty = flags_rule_penalty, rm_defer_max = flags_rule_defer_max,
          rm_debug = flags_rule_debug,
          rm_parents = any ("p:" `isPrefixOf`) (Map.keys vocab),
          rm_hvocab_c = IntMap.empty, rm_hvocab_p = IntMap.empty,
          rm_hgoal_v = IntSet.empty, rm_hgoal_h = IntSet.empty, rm_hgoal_c = IntSet.empty }
  pgModel <-
    case flags_pg_model of
      Nothing -> return Nothing
      Just mfile -> do
        forest <- parseForestBin <$> BS.readFile mfile
        if flags_pg_enigma > 0 then
          return $! length forest `seq` Just (case splitPGModelE flags_pg_enigma forest of
                                                Just (fr, fa) -> PGEnigmaAdd fr fa flags_pg_enigma
                                                Nothing -> PGEnigma forest flags_pg_enigma)
        else case splitPGModel forest of
          Just (fr, fa) -> return $! length fr `seq` length fa `seq` Just (PGAdditive fr fa)
          Nothing -> return $! length forest `seq` Just (PGFull forest)
  let
    config = config1 { cfg_rule_model = ruleModel, cfg_pg_model = pgModel }

  let
    readHintFile Nothing = return []
    readHintFile (Just file) = do
        str <- readFile file
        let
          funMap = Map.fromList [ (base (name f), f) | f <- reverse (Map.elems (ctx_funs ctx)) ]
          conv vm (HVar x) = Just (var (V (vm Map.! x)))
          conv vm (HApp f ts) = do
            jf <- Map.lookup f funMap
            Control.Monad.guard (Jukebox.arity jf == length ts)
            us <- mapM (conv vm) ts
            return (app (Sym (tweeConstant flags horn ctx (prec jf) jf)) us)
          splitTabs str = case break (== '\t') str of
            (x, '\t':rest) -> x : splitTabs rest
            (x, _) -> [x]
          splitCommas str = case break (== ',') str of
            (x, ',':rest) -> x : splitCommas rest
            (x, _) -> [x]
          parseLine l =
            case splitTabs l of
              (a:b:rest) -> do
                let w = case rest of
                          (ws:_) | [(x, _)] <- reads ws -> Just (x :: Float)
                          _ -> Nothing
                    gs = case rest of
                           (_:g:_) -> [ x | c <- splitCommas g, [(x, "")] <- [reads c] ] :: [Int]
                           _ -> []
                (t, ra) <- parseHTerm a
                (u, rb) <- parseHTerm b
                Control.Monad.guard (all isSpace ra && all isSpace rb)
                let vm = Map.fromList (zip (usort (hVars t ++ hVars u)) [0..])
                t' <- conv vm t
                u' <- conv vm u
                return (build t' :=: build u', w, gs)
              _ -> Nothing
          hs = mapMaybe parseLine (lines str)
        return $! length hs `seq` hs
  fileHints <- readHintFile flags_hints_file
  trackHints <- readHintFile flags_track_hints
  let
    withHints0 = foldl' (addHint config) (initialState config) [toTerm (varNums h) h | h <- hints']
    withHints1 = (if cfg_eqhint_subsume config then addEqHintSubIndex else id) $
      (if cfg_eqhint_instances config then addEqHintInstanceIndex else id) $
      (if cfg_eqhint_generalise config then addEqHintGeneralisations else id) $
      finishEqHintGroups $
      foldl' addEqHintFull withHints0 ([ (toEquation h, Nothing, []) | h <- eqHints' ] ++ fileHints)
    -- Goal constants for hint matching: flattening constants and skolems.
    nullaryFuns t = [ f | App f Nil <- Twee.Base.subterms t ]
    flatDefs =
      [ (symId f, d)
      | ax <- defs, (c, d) <- [(eqn_lhs (axiom_eqn ax), eqn_rhs (axiom_eqn ax))],
        App f Nil <- [c] ]
    flatSyms = IntSet.fromList (map fst flatDefs)
    axiomSyms = IntSet.fromList
      [ symId f | ax <- axioms, ax `notElem` defs, t <- terms (axiom_eqn ax), App f _ <- Twee.Base.subterms t ]
    skolemSyms = IntSet.fromList
      [ symId f
      | t <- concatMap (terms . goal_eqn) goals ++ map snd flatDefs,
        f <- nullaryFuns t,
        not (symId f `IntSet.member` axiomSyms), not (symId f `IntSet.member` flatSyms) ]
    terms (t :=: u) = [t, u]
    goalConsts =
      IntMap.fromList ([ (f, Just d) | (f, d) <- flatDefs ] ++ [ (f, Nothing) | f <- IntSet.toList skolemSyms ])
    withHints = foldl' addTrackedHint (setEqHintGoalConsts withHints1 goalConsts) [ e | (e, _, _) <- trackHints ]
    withGoals = foldl' (addGoal config) withHints goals
    withAxioms = foldl' (addAxiom config) withGoals axioms
    withBackwardsGoal = foldn rewriteGoalsBackwards withAxioms flags_backwards_goal

  -- Set up tracing.
  sayTrace <-
    case flags_trace of
      Nothing -> return $ \_ -> return ()
      Just (file, mod) -> do
        h <- openFile file WriteMode
        hSetBuffering h LineBuffering
        let put msg = hPutStrLn h msg
        put $ ":- module(" ++ mod ++ ", [step/1, lemma/1, axiom/1, goal/1])."
        put ":- discontiguous(step/1)."
        put ":- discontiguous(lemma/1)."
        put ":- discontiguous(axiom/1)."
        put ":- discontiguous(goal/1)."
        put ":- style_check(-singleton)."
        return $ \msg -> hPutStrLn h msg
  
  let
    say msg = unless (quiet globals) (putStrLn msg)
    line = say ""
    output = Output {
      output_message = \msg -> do
        say (prettyShow msg)
        sayTrace (show (traceMsg msg))
        case msg of
          HintMatched n active | flags_print_hint_matchers && n < trackBase ->
            let t :=: u = unorient (active_rule active) in
            putStrLn $ "HINTMATCHER " ++ show n ++ " " ++
              concat (lines (showProblem
                [Input Nothing "lemma" (Jukebox.Ax Jukebox.Axiom) Unknown $
                   toForm $ clause [Pos (jukeboxTerm ctx t Jukebox.:=: jukeboxTerm ctx u)]]))
          _ -> return () }

    traceMsg (NewActive _ active) =
      step "add" [traceActive active]
    traceMsg (NewEquation eqn) =
      step "hard" [traceEqn eqn]
    traceMsg (DeleteActive active) =
      step "delete" [traceActive active]
    traceMsg SimplifyQueue =
      step "simplify_queue" []
    traceMsg Interreduce =
      step "interreduce" []
    traceMsg (Status n) =
      step "status" [pPrint n]
    traceMsg (HintMatched n active) =
      step "hint" [pPrint n, pPrint (active_id active)]
    traceMsg _ =
      step "other" []

    traceActive Active{active_top = Nothing, ..} =
      traceApp "rule" [pPrint active_id, traceEqn (unorient active_rule)]
    traceActive Active{active_top = Just top, ..} =
      traceApp "rule" [pPrint active_id, traceEqn (unorient active_rule), traceEqn lemma1, traceEqn lemma2]
      where
        (lemma1, lemma2) =
          find (steps (derivation active_proof))
        find (s1:s2:_)
          | eqn_rhs (equation (certify s1)) == top && eqn_lhs (equation (certify s2)) == top =
            (lemmaOf s1, lemmaOf s2)
        find (_:xs) = find xs
        lemmaOf s =
          case (usedLemmas s, usedAxioms s) of
            ([p], []) -> equation p
            ([], [ax]) -> axiom_eqn ax

    traceEqn (t :=: u) =
      pPrintPrec prettyNormal 6 t <+> text "=" <+> pPrintPrec prettyNormal 6 u
    traceApp f xs =
      pPrintTerm uncurried prettyNormal 0 (text f) xs

    step :: String -> [Doc] -> Doc
    step f xs = traceApp "step" [traceApp f xs] <#> text "."

  say "Here is the input problem:"
  forM_ axioms $ \Axiom{..} ->
    say $ show $ nest 2 $
      describeEquation "Axiom"
        (show axiom_number) (Just axiom_name) axiom_vars axiom_eqn
  forM_ goals $ \Goal{..} ->
    say $ show $ nest 2 $
      describeEquation "Goal"
        (show goal_number) (Just goal_name) Nothing goal_eqn
  line

  startState <-
    case flags_load_state of
      Nothing -> return withBackwardsGoal
      Just _ -> do
        let loaded0 = rebuildOverlapIndex (fromJust savedState)
        -- Axioms of the problem that the saved run did not have (e.g.
        -- lemmas proven since) are added to the resumed state.
        -- An axiom is known if the saved run has the same equation (in the
        -- saved signature, which the problem now shares). Names are not
        -- enough: kNN lemmas are numbered by rank, and states saved before
        -- the shared signature hold copies in a foreign one.
        let cpu = fmap (\t -> fromIntegral t / 1e12 :: Double) getCPUTime
        c0 <- cpu
        c1 <- st_next_active loaded0 `seq` Queue.size (st_queue loaded0) `seq` cpu
        let known = map axiom_eqn (st_axioms loaded0)
            newAxioms = [ ax | ax <- axioms, axiom_eqn ax `notElem` known ]
            -- The saved hint tables must not be used: they are keyed by
            -- symbol ids of the saved run, which are assigned afresh when the
            -- state is re-interned. (Stale goal-constant ids made the new
            -- axioms' critical pairs expand a constant into a definition
            -- containing itself, and a resumed run grew to 100 GB.) So the
            -- hints of this run go in before the new axioms are added.
            ehNew = st_eqhints withHints
            base0 = loaded0 { st_eqhints = ehNew }
            base1 | Map.null (eh_map ehNew) = base0
                  | otherwise = normaliseEqHints base0
            loaded = foldl' (addAxiom config) base1 newAxioms
        unless (null newAxioms) $
          say $ "Resumed with " ++ show (length newAxioms) ++ " new axioms"
        c2 <- st_next_active loaded `seq` Queue.size (st_queue loaded) `seq` cpu
        let eh = (st_eqhints loaded) { eh_last_match = fromIntegral (st_next_active loaded) }
            st1 = markResumedHints loaded { st_eqhints = eh, st_cur_passive = Nothing }
            st1' | Map.null (eh_map eh) = st1
                 | otherwise = normaliseEqHints st1
        c3 <- IntMap.size (eh_live (st_eqhints st1')) `seq` IntSet.size (eh_matched (st_eqhints st1')) `seq` cpu
        let st2 | Map.null (eh_map eh) || not flags_resume_requeue = st1'
                | otherwise = simplifyQueue config st1'
        c4 <- st_next_active st2 `seq` Queue.size (st_queue st2) `seq` cpu
        putStrLn $ "RESUMETIME load=" ++ show (c1 - c0) ++ " axioms=" ++ show (c2 - c1) ++
          " hints=" ++ show (c3 - c2) ++ " queue=" ++ show (c4 - c3) ++ " passive=" ++ show (Queue.size (st_queue st2))
        return $! st2
  state <-
    case flags_stitch of
      Nothing -> do
        complete output config startState
      Just stitch -> do
        let
          (timeout, final_timeout) =
            case cfg_max_time config of
              Just time -> (time / 5, Just (time * 4 / 5))
              Nothing -> (30, Nothing)
        intermediate <- complete output config{cfg_max_time = Just timeout} withBackwardsGoal
        let
          score rule =
            (KBO.size (lhs rule), lhs rule,
             KBO.size (rhs rule), rhs rule)
          actives =
            sortBy (comparing (score . active_rule)) $
            IntMap.elems (st_active_set intermediate)
          pres = present (cfg_proof_presentation config){cfg_all_lemmas = True} (map active_proof actives) []
          proofStr = show (pPrintPresentation (cfg_proof_presentation config){cfg_use_colour = False} pres)
        line
        say "Running Stitch..."
        hintsStrs <- lines <$> readProcess stitch [] proofStr
        let toTerm' t = toTerm (varNums t) t
        let parseTerm str = toTerm' (Snippet.giveProblem prob (Snippet.form (TPTP.term TPTP.NoQuantification Map.empty)) str)
        let hints = map parseTerm hintsStrs
        mapM_ (say . show . pPrint) hints
        let config' = config{cfg_max_time = final_timeout}
        complete output config' $
          interreduce config' $
          simplifyQueue config' $
          foldl' (addHint config') intermediate hints

  line

  cpuEnd <- getCPUTime
  -- (not when the goal is proved: nothing resumes a solved state, and on AIM goals the dump
  -- took 20-30% of a short run's time and 4x its peak memory, REPORT 2au)
  case flags_dump_state of
    Just dumpStateFile | not (solved state) ->
      BS.writeFile dumpStateFile (encode state)
    _ -> return ()

  when (cfg_max_cpu config > 0 && fromIntegral cpuEnd / 1e12 >= cfg_max_cpu config) $ putStrLn "CPULIMIT"
  putStrLn $ "WORK considered=" ++ show (st_considered state) ++ " rules=" ++ show (fromIntegral (st_next_active state) :: Int)
  let EqHints{..} = st_eqhints state
  -- First matches of hints: critical pairs considered and rule number.
  when (eh_next > 0) $
    putStrLn $ "HINTLOG " ++ unwords [ show c ++ ":" ++ show r | (c, r) <- reverse eh_log ]
  when (eh_next > 0 || eh_ntracked > 0) $
    putStrLn $ "HINTSTATS hints=" ++ show eh_next ++ " live=" ++ show (IntMap.size eh_live) ++
      " joined=" ++ show eh_joined ++ " matched=" ++ show (IntSet.size (fst (IntSet.split trackBase eh_matched))) ++
      " tracked=" ++ show eh_ntracked ++ " trackmatched=" ++ show (IntSet.size (snd (IntSet.split (trackBase-1) eh_matched))) ++
      " forms=" ++ show (Map.size eh_map) ++ " rules=" ++ show (st_next_active state) ++
      " lastmatch=" ++ show eh_last_match ++ " maxgap=" ++ show eh_max_gap ++
      " deferred=" ++ show (st_ndeferred state)

  when (solved state && cfg_pg_log config) $
    forM_ (allLemmas (map (derivation . pg_proof) (solutions state))) $ \p ->
      putStrLn ("PGPROOF " ++ pgCanon (equation p))

  when (not (solved state) && flags_print_goal_nf > 0) $ do
    let showT t =
          showProblem
            [Input Nothing "nf" (Jukebox.Ax Jukebox.Axiom) Unknown $
               toForm $ clause [Pos (jukeboxTerm ctx t Jukebox.:=: jukeboxTerm ctx t)]]
        pick m = take flags_print_goal_nf (sortBy (comparing (\t -> (KBO.size t, t))) (Map.keys m))
    forM_ (st_goals state) $ \g -> do
      forM_ (pick (goal_lhs g)) $ \t -> putStrLn ("GOALNF L " ++ showT t)
      forM_ (pick (goal_rhs g)) $ \t -> putStrLn ("GOALNF R " ++ showT t)
  when (solved state && flags_print_hints) $ do
    let
      sols = map (eliminateDefinitionsFromGoal defs) (solutions state)
      lems = allLemmas (map (derivation . pg_proof) sols)
      -- A lemma that depends (transitively) on a hypothesis is only true for
      -- the skolems, so it must not be generalised into a hint. allLemmas
      -- lists dependencies first; unknown lemmas count as dependent.
      hypNums = Set.fromList (map axiom_number hyps)
      usesHyp m d =
        any ((`Set.member` hypNums) . axiom_number) (usedAxioms d) ||
        any (\q -> Map.findWithDefault True q m) (usedLemmas d)
      hypDep = foldl' (\m p -> Map.insert p (usesHyp m (derivation p)) m) Map.empty lems
      (hypLems, fwdLems) = partition (\p -> Map.findWithDefault True p hypDep) lems
      lemmaEqns = map equation fwdLems
      (hypGoals, fwdGoals) = partition (usesHyp hypDep . derivation . pg_proof) sols
      goalEqns = [ equation (pg_proof g) | g <- fwdGoals ]
      hypEqns = map equation hypLems ++ [ equation (pg_proof g) | g <- hypGoals ]
      showEqn (t :=: u) =
        showProblem
          [Input Nothing "hint" (Jukebox.Ax Jukebox.Axiom) Unknown $
             toForm $ clause [Pos (jukeboxTerm ctx t Jukebox.:=: jukeboxTerm ctx u)]]
    putStrLn "HINTS-BEGIN"
    forM_ lemmaEqns $ \eqn -> putStrLn (showEqn eqn)
    putStrLn "HINTS-GOAL"
    forM_ goalEqns $ \eqn -> putStrLn (showEqn eqn)
    putStrLn "HINTS-AUX"
    forM_ fwdLems $ \p -> do
      let ts = stepTerms (derivation p)
          n = length ts
          k = snd (maximum [ (KBO.size t, i) | (i, t) <- zip [0..] ts ])
          pairs = [ (ts !! i, ts !! j) | i <- [0..k-1], j <- [k+1..n-1], (i, j) /= (0, n-1) ]
      forM_ (take 30 pairs) $ \(t, u) -> putStrLn (showEqn (t :=: u))
    -- Lemmas and goals that use a hypothesis: for labelling only, never
    -- generalised.
    putStrLn "HINTS-HYP"
    forM_ hypEqns $ \eqn -> putStrLn (showEqn eqn)
    -- Lemmas that depend (transitively) on an input axiom named assume_* (an
    -- extra, possibly false assumption of a proof sketch), each after a line
    -- naming those assumptions; dependencies first.
    let isAsm ax = "assume_" `isPrefixOf` axiom_name ax
        asmOf m d = Set.unions (Set.fromList [ axiom_name ax | ax <- usedAxioms d, isAsm ax ] :
                                [ Map.findWithDefault Set.empty q m | q <- usedLemmas d ])
        asmDep = foldl' (\m p -> Map.insert p (asmOf m (derivation p)) m) Map.empty lems
    putStrLn "HINTS-ASSUMED"
    forM_ fwdLems $ \p -> do
      let as = Map.findWithDefault Set.empty p asmDep
      unless (Set.null as) $ do
        putStrLn ("% assumes " ++ unwords (Set.toList as))
        putStrLn (showEqn (equation p))
    putStrLn "HINTS-END"
    -- the input axioms (and lemmas given as axioms) the proof uses, by name
    putStrLn $ "USEDAXIOMS " ++ unwords (Set.toList (Set.fromList
      [ axiom_name ax | d <- map derivation lems ++ map (derivation . pg_proof) sols, ax <- usedAxioms d ]))
    when (cfg_log_given config) $ do
      putStrLn "GIVEN-BEGIN"
      forM_ (reverse (st_given state)) $ \(eqn, p1, p2) -> do
        putStrLn ("% parents " ++ show p1 ++ " " ++ show p2)
        putStrLn (showEqn (fromMaybe eqn (expandGoalConsts (st_eqhints state) eqn)))
      putStrLn "GIVEN-END"

  when (not (solved state) && flags_print_given_unsolved && cfg_log_given config) $ do
    let showEqnU (t :=: u) =
          showProblem
            [Input Nothing "hint" (Jukebox.Ax Jukebox.Axiom) Unknown $
               toForm $ clause [Pos (jukeboxTerm ctx t Jukebox.:=: jukeboxTerm ctx u)]]
    putStrLn "GIVEN-BEGIN"
    forM_ (reverse (st_given state)) $ \(eqn, p1, p2) -> do
      putStrLn ("% parents " ++ show p1 ++ " " ++ show p2)
      putStrLn (showEqnU (fromMaybe eqn (expandGoalConsts (st_eqhints state) eqn)))
    putStrLn "GIVEN-END"

  when (solved state && flags_proof) $ later $ do
    let
      cfg_present
        | tstp && flags_formal_proof =
          (cfg_proof_presentation config){cfg_all_lemmas = True}
        | otherwise =
          cfg_proof_presentation config
      score rule =
        (KBO.size (lhs rule), lhs rule,
         KBO.size (rhs rule), rhs rule)
      actives =
        sortBy (comparing (score . active_rule)) $
        IntMap.elems (st_active_set state)
      lemmas = if flags_proof_all_rules then map active_proof actives else []
      pres = present cfg_present lemmas $ map (eliminateDefinitionsFromGoal defs) $ solutions state

    case flags_dump_proof of
      Nothing -> return ()
      Just dumpProofFile ->
        BS.writeFile dumpProofFile (encode pres)

    sayTrace ""
    forM_ (pres_axioms pres) $ \p ->
      sayTrace $ show $
        traceApp "axiom" [traceEqn (axiom_eqn p)] <#> text "."
    forM_ (pres_lemmas pres) $ \p ->
      sayTrace $ show $
        traceApp "lemma" [traceEqn (equation p)] <#> text "."
    forM_ (pres_goals pres) $ \p ->
      sayTrace $ show $
        traceApp "goal" [traceEqn (pg_goal_hint p)] <#> text "."

    when (tstp && not flags_formal_proof) $ do
      putStrLn "% SZS output start Proof"
      let
        axiomForms =
          Map.fromList
            (zip (map axiom_number axioms) (map pre_form axioms0))
        goalForms =
          Map.fromList
            (zip (map goal_number goals) (map pre_form goals0))

        findSource forms n =
          case Map.lookup n forms of
            Nothing -> []
            Just inp -> go inp
           where
            go Input{source = Unknown} = []
            go Input{source = Inference _ _ _ inps} = concatMap (go . inputValue) inps
            go inp@Input{source = FromFile _ _ _} = [inp]

      when flags_explain_encoding $ do
        putStrLn "Take the following subset of the input axioms:"
        mapM_ putStrLn $ map ("  " ++) $ lines $ showProblem $
          usortBy (comparing show) $
            (pres_axioms pres >>= findSource axiomForms . axiom_number) ++
            (pres_goals pres >>= findSource goalForms . pg_number)

        putStrLn ""
        putStrLn "Now clausify the problem and encode Horn clauses using encoding 3 of"
        putStrLn "http://www.cse.chalmers.se/~nicsma/papers/horn.pdf."
        putStrLn "We repeatedly replace C & s=t => u=v by the two clauses:"
        putStrLn "  fresh(y, y, x1...xn) = u"
        putStrLn "  C => fresh(s, t, x1...xn) = v"
        putStrLn "where fresh is a fresh function symbol and x1..xn are the free"
        putStrLn "variables of u and v."
        putStrLn "A predicate p(X) is encoded as p(X)=true (this is sound, because the"
        putStrLn "input problem has no model of domain size 1)."
        putStrLn ""
        putStrLn "The encoding turns the above axioms into the following unit equations and goals:"
        putStrLn ""
      print $ pPrintPresentation (cfg_proof_presentation config) pres
      putStrLn "% SZS output end Proof"
      putStrLn ""
  
    when (tstp && flags_formal_proof) $ do
      forM_ (pres_goals pres) $ \ProvedGoal{..} ->
        unless (pg_witness_hint == emptySubst) $ do
          let varName x = fromJust (Map.lookup x (fromJust pg_vars))
          let answer = intercalate ", " [varName x ++ "->" ++ prettyShow t | (x, t) <- substToList pg_witness_hint]
          putStrLn $ "% SZS answers Tuple [[" ++ answer ++ "]|_] for " ++ pg_name
      putStrLn "% SZS output start CNFRefutation"
      print $ pPrintProof $
        presentToJukebox ctx (curry toEquation)
          (zip (map axiom_number axioms) (map pre_form axioms0))
          (zip (map goal_number goals) (map pre_form goals0))
          pres
      putStrLn "% SZS output end CNFRefutation"
      putStrLn ""

    unless tstp $ do
      putStrLn "The conjecture is true! Here is a proof."
      putStrLn ""
      print $ pPrintPresentation (cfg_proof_presentation config) pres
      putStrLn ""

  when (not (quiet globals) && not (solved state)) $ later $ do
    let
      state' = interreduce config state
      score rule =
        (KBO.size (lhs rule), lhs rule,
         KBO.size (rhs rule), rhs rule)
      actives =
        sortBy (comparing (score . active_rule)) $
        IntMap.elems (st_active_set state')

    when (tstp && configIsComplete config) $ do
      putStrLn "% SZS output start Saturation"
      print $ pPrintProof $
        map pre_form axioms0 ++
        map pre_form goals0 ++
        [ Input Nothing "rule" (Jukebox.Ax Jukebox.Axiom) Unknown $
            toForm $ clause
              [Pos (jukeboxTerm ctx (lhs rule) Jukebox.:=: jukeboxTerm ctx (rhs rule))]
        | rule <- rules state ]
      putStrLn "% SZS output end Saturation"
      putStrLn ""

    if configIsComplete config then do
      putStrLn "Ran out of critical pairs. This means the conjecture is not true."
    else do
      putStrLn "Gave up on reaching the given resource limit."
    putStrLn "Here is the final rewrite system:"
    forM_ actives $ \active ->
      putStrLn ("  " ++ prettyShow (canonicalise (active_rule active)))
    putStrLn ""
    
    when flags_proof_on_saturation $ do
      let pres = present (cfg_proof_presentation config) (map active_proof actives) []
      print $ pPrintPresentation (cfg_proof_presentation config) pres

  return $
    if solved state then Unsat Unsatisfiable Nothing
    else if configIsComplete config && not (dropNonHorn horn) && not flags_give_up_on_saturation then Sat Satisfiable Nothing
    else NoAnswer GaveUp

-- Transform a proof presentation into a Jukebox proof.
presentToJukebox ::
  TweeContext ->
  (Jukebox.Term -> Jukebox.Term -> Equation Constant) ->
  -- Axioms, indexed by axiom number.
  [(Int, Input Form)] ->
  -- N.B. the formula here proves the negated goal.
  [(Int, Input Form)] ->
  Presentation Constant ->
  Problem Form
presentToJukebox ctx toEquation axioms goals Presentation{..} =
  [ Input {
      ident = Nothing,
      tag = pg_name,
      kind = Jukebox.Ax Jukebox.Axiom,
      what = false,
      source =
        inference "resolution" "thm"
          [-- A proof of t != u
           existentialHack pg_goal_hint (fromJust (lookup pg_number goals)),
           -- A proof of t = u
           fromJust (Map.lookup pg_number goal_proofs)] }
  | ProvedGoal{..} <- pres_goals ]

  where
    axiom_proofs =
      Map.fromList
        [ (axiom_number, (fromJust (lookup axiom_number axioms)) { ident = Just (ident axiom_number) })
        | Axiom{..} <- pres_axioms ]
      where
        ident i = variant "axiom" [i]

    lemma_proofs =
      Map.fromList [(p, (tstp p) { ident = Just (ident i) }) | (i, p) <- zip [0..] pres_lemmas]
      where
        ident i = variant "lemma" [i :: Int]

    goal_proofs =
      Map.fromList [(pg_number, tstp pg_proof) | ProvedGoal{..} <- pres_goals]

    tstp :: Proof Constant -> Input Form
    tstp = deriv . derivation

    deriv :: Derivation Constant -> Input Form
    deriv p =
      Input {
        ident = Nothing,
        tag = "step",
        kind = Jukebox.Ax Jukebox.Axiom,
        what = jukeboxEquation (equation (certify p)),
        source =
          inference name "thm" sources }
      where
        (name, sources) = unpack p

    unpack :: Derivation Constant -> (String, [Input Form])
    unpack (Refl _) = ("reflexivity", [])
    unpack (Symm p) = ("symmetry", [deriv p])
    unpack (Trans p q) = ("transitivity", [deriv p, deriv q])
    unpack (Cong _ ps) = ("congruence", [deriv p | p <- ps, let t :=: u = equation (certify p), t /= u])
    unpack (UseAxiom Axiom{..} _) =
      ("substitution", [fromJust (Map.lookup axiom_number axiom_proofs)])
    unpack (UseLemma lemma _) =
      ("substitution", [fromJust (Map.lookup lemma lemma_proofs)])

    jukeboxEquation :: Equation Constant -> Form
    jukeboxEquation (t :=: u) =
      toForm $ clause [Pos (jukeboxTerm ctx t Jukebox.:=: jukeboxTerm ctx u)]

    -- An ugly hack: since Twee.Proof decodes $true = $false into a
    -- proof of the existentially quantified goal, we need to do the
    -- same decoding at the Jukebox level.
    existentialHack eqn input =
      case find input of
        [] -> error $ "bug in TSTP output: can't fix up decoded existential"
        (inp:_) -> inp
        where
          -- Check if this looks like the correct clause;
          -- if not, try its ancestors.
          find inp | ok inp = [inp]
          find Input{source = Inference _ _ _ inps} =
            concatMap (find . inputValue) inps
          find _ = []

          ok inp =
            case toClause (what inp) of
              Nothing -> False
              Just (Clause (Bind _ [Neg (t' Jukebox.:=: u')])) ->
                let
                  eqn' = toEquation t' u'
                  ts = buildList [eqn_lhs eqn, eqn_rhs eqn]
                  us = buildList [eqn_lhs eqn', eqn_rhs eqn']
                in
                  isJust (matchList ts us) && isJust (matchList us ts)

main = do
  hSetBuffering stdout LineBuffering
  stampM (intern "twee") . join . parseCommandLineWithExtraArgs
    ["--no-conjunctive-conjectures", "--no-split"]
#ifdef VERSION_twee
    "Twee, the wonderful equation engine" . version ("twee version " ++ VERSION_twee) $
#else
    "Twee, the wonderful equation engine" . version "twee development version" $
#endif
      globalFlags *> parseMainFlags *>
      -- hack: get --quiet and --no-proof options to appear before --tstp
      forAllFilesBox <*>
        (readProblemBox =>>=
         expert clausifyBox =>>=
         forAllConjecturesBox <*>
           (combine <$>
             expert hornToUnitBox <*>
             parseConfig <*>
             parseMainFlags <*>
             (toFormulasBox =>>=
              expert (toFof <$> clausifyBox <*> pure (tags True)) =>>=
              expert clausifyBox =>>= expert oneConjectureBox) <*>
             (runTwee <$> globalFlags <*> tstpFlags <*> expert hornFlags <*> parsePrecedence)))
  profile
  where
    getHint Input{what = Clause (Bind _ [Pos (Tru (hint :@: [t]))])}
      | base (name hint) == "$hint" = Left t
    getHint Input{what = Clause (Bind _ [Pos (Tru t@(hint :@: [_, _]))])}
      | base (name hint) == "$hinteq" = Left t
    getHint c = Right c
    combine horn config main encode prove later prob0 = do
      let prob1 = if flags_hint_goals main then hintGoals prob0 else prob0
      let (hints, nonHints) = partitionEithers (map getHint prob1)
      res <- horn nonHints
      case res of
        Left ans -> return ans
        Right prob -> do
          let
            isUnitEquality [Pos (_ Jukebox.:=: _)] = True
            isUnitEquality [Neg (_ Jukebox.:=: _)] = True
            isUnitEquality _ = False
            isUnit = all isUnitEquality (map (toLiterals . what) prob1)
            main' = if isUnit then main{flags_explain_encoding = False} else main{flags_formal_proof = False}
          encode prob >>= prove config main' later hints
