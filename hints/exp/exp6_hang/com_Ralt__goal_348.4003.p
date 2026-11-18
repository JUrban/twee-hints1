
% The LADR formulas contain function or predicate symbols
% that are not legal TPTP symbols, and we have replaced those
% symbols with new symbols.  Here is the list of the unaccepted
% symbols and the corresponding replacements.
%
%   (arity 2)        *    m
%   (arity 2)        \    ld
%   (arity 3)        R    r
%   (arity 3)        L    l
%   (arity 2)        T    t
%   (arity 2)        /    rd
%   (arity 2)        K    k
%   (arity 0)        1    e

cnf(sos,axiom,m(e,A) = A).
cnf(sos,axiom,m(A,e) = A).
cnf(sos,axiom,ld(A,m(A,B)) = B).
cnf(sos,axiom,m(A,ld(A,B)) = B).
cnf(sos,axiom,rd(m(A,B),B) = A).
cnf(sos,axiom,m(rd(A,B),B) = A).
cnf(sos,axiom,a(A,B,C) = ld(m(A,m(B,C)),m(m(A,B),C))).
cnf(sos,axiom,k(A,B) = ld(m(B,A),m(A,B))).
cnf(sos,axiom,l(A,B,C) = ld(m(C,B),m(C,m(B,A)))).
cnf(sos,axiom,r(A,B,C) = rd(m(m(A,B),C),m(B,C))).
cnf(sos,axiom,t(A,B) = ld(B,m(A,B))).
cnf(sos,axiom,t(t(A,B),C) = t(t(A,C),B)).
cnf(sos,axiom,l(t(A,B),C,D) = t(l(A,C,D),B)).
cnf(sos,axiom,r(t(A,B),C,D) = t(r(A,C,D),B)).
cnf(sos,axiom,r(l(A,B,C),D,E) = l(r(A,D,E),B,C)).
cnf(sos,axiom,l(l(A,B,C),D,E) = l(l(A,D,E),B,C)).
cnf(sos,axiom,r(r(A,B,C),D,E) = r(r(A,D,E),B,C)).
cnf(sos,axiom,m(A,B) = m(B,A)).
cnf(sos,axiom,m(m(A,B),B) = m(A,m(B,B))).
fof(goals,conjecture,! [X0,X1,X2] : m(X2,rd(rd(X1,X0),rd(X2,X0))) = X1).
fof(lemma_goal_346,axiom,! [X0] : ! [X1] : ! [X2] : ! [X3] : ! [X4] : ! [X5] : a(X0,X1,ld(m(ld(X2,ld(ld(X3,e),X2)),X4),X5)) = a(X0,X1,ld(m(X4,l(X3,ld(X3,e),m(X3,X2))),X5))).
fof(lemma_goal_329,axiom,! [X0] : ! [X1] : ! [X2] : ! [X3] : m(m(X0,l(ld(X0,e),X1,X2)),m(e,ld(X0,X3))) = ld(ld(l(ld(X0,e),X1,X2),e),X3)).
fof(lemma_goal_328,axiom,! [X0] : ! [X1] : ! [X2] : ! [X3] : l(X0,ld(l(X1,X2,X3),X1),ld(X1,l(X1,X2,X3))) = l(X0,ld(l(X1,X2,X3),X1),ld(X1,e))).
fof(lemma_goal_327,axiom,! [X0] : ! [X1] : ! [X2] : ! [X3] : l(l(X0,X1,X2),ld(l(X0,X1,X2),e),m(l(X0,X1,X2),X3)) = l(l(X0,ld(X0,e),m(X0,X3)),X1,X2)).
fof(lemma_goal_326,axiom,! [X0] : ! [X1] : ! [X2] : ! [X3] : m(m(X0,ld(l(X1,X2,X3),X1)),ld(X1,l(X1,X2,X3))) = l(X0,ld(l(X1,X2,X3),X1),ld(X1,e))).
fof(lemma_goal_325,axiom,! [X0] : ! [X1] : ! [X2] : ! [X3] : a(X0,ld(l(X1,X2,X3),e),m(ld(X1,e),l(X1,X2,X3))) = ld(m(X0,ld(X1,e)),m(X0,ld(X1,e)))).
fof(lemma_knn_0_com_Ralt__goal_147,axiom,! [X0] : ! [X1] : ! [X2] : ld(m(X0,ld(X1,X2)),m(X0,ld(ld(X2,X1),ld(X1,X2)))) = l(ld(ld(X2,X1),e),ld(X1,X2),X0)).
fof(lemma_knn_1_com_Ralt__goal_322,axiom,! [X0] : ! [X1] : ! [X2] : ! [X3] : l(ld(ld(X0,X1),e),X2,ld(X1,X0)) = ld(m(X3,ld(X1,X0)),m(X3,ld(ld(X0,X1),ld(X1,X0))))).
fof(lemma_knn_2_nil4_19K__goal_290,axiom,! [X0] : ! [X1] : ! [X2] : ! [X3] : m(ld(X0,X1),rd(m(X2,ld(ld(X0,X1),ld(X0,X3))),X2)) = ld(X0,m(X1,rd(m(X2,ld(X1,X3)),X2)))).
fof(lemma_knn_3_com_Ralt__goal_128,axiom,! [X0] : ! [X1] : ld(ld(ld(X0,X1),e),ld(X1,X0)) = m(ld(X0,X1),ld(X1,X0))).
fof(lemma_knn_4_Ka1_eq_Ka2__goal_54,axiom,! [X0,X1,X2] : (ld(X1,X2) = ld(m(X0,ld(X0,X1)),X2))).
fof(lemma_knn_5_aK2_eq_aK3_1243b__goal_11,axiom,! [X0] : ! [X1] : ! [X2] : ld(m(X0,ld(X0,X1)),X2) = ld(X1,X2)).
fof(lemma_knn_6_Ka1_eq_Ka2__goal_4,axiom,! [X0] : ! [X1] : ld(m(X0,ld(X0,e)),X1) = X1).
fof(lemma_knn_7_Kproperties_1__goal_37,axiom,! [X0,X1] : (ld(m(X0,ld(X0,e)),X1) = X1)).
fof(lemma_knn_8_aK2_eq_aK3_1243b__goal_27,axiom,! [X0,X1] : (X1 = ld(m(X0,ld(X0,e)),X1))).
fof(lemma_knn_9_com_Ralt__goal_81,axiom,! [X0] : ! [X1] : ! [X2] : l(ld(X0,X1),X0,ld(X1,X2)) = ld(m(X0,ld(X1,X2)),X2)).
fof(lemma_knn_10_com_Ralt__goal_34,axiom,! [X0] : ! [X1] : ld(ld(ld(X0,X1),X0),X1) = m(ld(X0,X1),ld(X0,X1))).
fof(lemma_knn_11_com_Ralt__goal_5,axiom,! [X0] : ! [X1] : l(X0,ld(X0,e),X1) = ld(m(X1,ld(X0,e)),X1)).
fof(lemma_knn_12_aK2_eq_aK3_1243b__goal_325,axiom,! [X0] : ! [X1] : t(ld(X0,X1),m(ld(X0,X1),ld(X1,X0))) = ld(X0,X1)).
fof(lemma_knn_13_com_Ralt__goal_260,axiom,! [X0] : ! [X1] : ld(ld(X0,X1),ld(ld(ld(X0,X1),e),X0)) = m(X0,m(ld(X0,X1),ld(X1,X0)))).
fof(lemma_knn_14_TLRproperties_2__goal_265,axiom,! [X0] : ! [X1] : ld(m(ld(X0,X1),ld(X1,X0)),ld(X1,X0)) = ld(ld(X0,X1),e)).
fof(lemma_knn_15_com_Ralt__goal_200,axiom,! [X0] : ! [X1] : ! [X2] : ld(m(X0,m(ld(X0,X1),ld(X1,X2))),X2) = a(X0,ld(X0,X1),ld(X1,X2))).
fof(lemma_knn_16_Kproperties_1__goal_241,axiom,! [X0] : ! [X1] : m(rd(e,ld(X0,X1)),m(ld(X1,X0),ld(X0,X1))) = ld(X1,X0)).
fof(lemma_knn_17_aK2_eq_aK3_1243b__goal_294,axiom,! [X0] : ! [X1] : rd(ld(X0,X1),ld(ld(X1,X0),e)) = m(ld(X1,X0),ld(X0,X1))).
fof(lemma_knn_18_nil4_19K__goal_259,axiom,! [X0] : ! [X1] : ld(rd(e,ld(X0,X1)),ld(X1,X0)) = m(ld(X1,X0),ld(X0,X1))).
fof(lemma_knn_19_aKperms_1__goal_247,axiom,! [X0] : ! [X1] : m(l(ld(X0,X1),ld(X1,X0),ld(X0,X1)),ld(X1,X0)) = m(ld(X1,X0),ld(X0,X1))).
fof(lemma_knn_20_TLRproperties_2__goal_136,axiom,! [X0] : ! [X1] : ! [X2] : ld(r(X0,ld(X0,X1),ld(X1,X2)),X2) = m(ld(X0,X1),ld(X1,X2))).
fof(lemma_knn_21_nil3_2K__goal_177,axiom,! [X0] : ! [X1] : ! [X2] : ld(X0,l(m(X0,ld(X1,X2)),ld(X0,e),X1)) = m(ld(X0,e),ld(m(X1,ld(X0,e)),X2))).
fof(lemma_knn_22_aa_instances_4__goal_265,axiom,! [X0] : ! [X1] : k(ld(m(ld(X0,X1),ld(X1,X0)),ld(X0,X1)),m(ld(X0,X1),ld(X1,X0))) = ld(X1,m(X0,ld(X0,X1)))).
fof(lemma_knn_23_com_Ralt__goal_187,axiom,! [X0] : ! [X1] : ! [X2] : ld(l(ld(X0,e),m(X0,ld(m(X0,X1),X1)),X2),m(X2,ld(m(X0,X1),X1))) = m(X2,ld(ld(X0,e),ld(m(X0,X1),X1)))).
fof(lemma_knn_24_Ka_eq_aK3__goal_310,axiom,! [X0] : ! [X1] : k(ld(m(ld(X0,X1),ld(X1,X0)),ld(X0,X1)),m(ld(X0,X1),ld(X1,X0))) = e).
fof(lemma_knn_25_Ka_eq_aK3__goal_330,axiom,! [X0] : ! [X1] : ld(ld(X0,e),ld(m(X1,X0),X1)) = m(X0,ld(m(X1,X0),X1))).
fof(lemma_knn_26_aK2_eq_aK3_1243b__goal_79,axiom,! [X0] : ! [X1] : l(t(X0,ld(X0,e)),ld(X0,e),X1) = ld(m(X1,ld(X0,e)),X1)).
fof(lemma_knn_27_aK2rev__goal_290,axiom,! [X0] : ! [X1] : ld(m(X0,ld(m(X1,X0),X1)),X0) = rd(e,ld(m(X1,X0),X1))).
fof(lemma_knn_28_com_Ralt__goal_185,axiom,! [X0] : ! [X1] : m(ld(X0,m(X0,X1)),ld(m(X0,X1),X0)) = ld(ld(X1,e),ld(m(X1,X0),X0))).
fof(lemma_knn_29_Ka1_eq_Ka2__goal_157,axiom,! [X0] : ! [X1] : rd(m(ld(X0,X1),ld(X1,X0)),ld(X0,X1)) = l(rd(e,ld(X0,X1)),ld(X0,X1),X0)).
