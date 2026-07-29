%------------------------------------------------------------------------------
% File     : ROB001-1 : TPTP v9.3.0. Released v1.0.0.
% Domain   : Robbins Algebra
% Problem  : Is every Robbins algebra Boolean?
% Version  : [Win90] (equality) axioms.
% English  :

% Refs     : [HMT71] Henkin et al. (1971), Cylindrical Algebras
%          : [Win90] Winker (1990), Robbins Algebra: Conditions that make a
% Source   : [TPTP]
% Names    :

% Status   : Unsatisfiable
% Rating   : 1.00 v2.0.0
% Syntax   : Number of clauses     :    4 (   4 unt;   0 nHn;   1 RR)
%            Number of literals    :    4 (   4 equ;   1 neg)
%            Maximal clause size   :    1 (   1 avg)
%            Maximal term depth    :    6 (   2 avg)
%            Number of predicates  :    1 (   0 usr;   0 prp; 2-2 aty)
%            Number of functors    :    4 (   4 usr;   2 con; 0-2 aty)
%            Number of variables   :    7 (   0 sgn)
% SPC      : CNF_UNS_RFO_PEQ_UEQ

% Comments : Commutativity, associativity, and Huntington's axiom axiomatize 
%            Boolean algebra.
%------------------------------------------------------------------------------
%----Include axioms for Robbins algebra
include('Axioms/ROB001-0.ax').
%------------------------------------------------------------------------------
cnf(prove_huntingtons_axiom,negated_conjecture,
    add(negate(add(a,negate(b))),negate(add(negate(a),negate(b)))) != b ).

%----Definition of g
cnf(sos04,axiom,(
    $hint(negate(add(A,negate(A)))) )).

%----Definition of h
cnf(sos05,axiom,(
    h(A) = add(A,add(A,add(A,negate(add(A,negate(A)))))))).
