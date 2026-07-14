% Mitschke, "Every distributive groupoid is trimedial".
% Twee's proof of this is much uglier than the paper's proof.

cnf(distributivity, axiom,
    X . (Y . Z) = (X . Y) . (X . Z)).
cnf(distributivity, axiom,
    (X . Y) . Z = (X . Z) . (Y . Z)).
fof(conjecture, conjecture,
    (a . b) . (c . a) = (a . c) . (b . a)). 

%fof(lemma6, conjecture, ![X, Y, Z]: ((X . Y) . (Z . X)) . ((X . Z) . (Y . X)) = (X . Y) . (Z . X)).

