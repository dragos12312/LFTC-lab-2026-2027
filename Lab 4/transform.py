# fa to rg and rg to fa

from fa import FA
from rg import RG, EPSILON


def new_name(name, used):
    # puts ' at the end until the name is free
    while name in used:
        name += "'"
    return name


def fa_to_rg(fa):
    # states become nonterminals, start is q0
    # delta(p, a) = q gives p -> a q
    # and if q is final also p -> a
    # if q0 is final we add S -> epsilon
    start = fa.initial
    nonterminals = list(fa.states)
    initial_is_target = any(fa.initial in targets for targets in fa.transitions.values())
    if fa.initial in fa.finals and initial_is_target:
        # cant have S -> epsilon if S is on a right side
        # so we make a new start with the same productions as q0 plus epsilon
        start = new_name(fa.initial, nonterminals)
        nonterminals.insert(0, start)

    rg = RG(nonterminals, fa.alphabet, start)
    for (source, symbol), targets in fa.transitions.items():
        for target in targets:
            rg.add_production(source, [symbol, target])
            if target in fa.finals:
                rg.add_production(source, [symbol])
    if start != fa.initial:
        for right in rg.productions.get(fa.initial, []):
            rg.add_production(start, right)
    if fa.initial in fa.finals:
        rg.add_production(start, [EPSILON])
    return rg


def rg_to_fa(rg):
    # nonterminals become states plus a new final state K, start is S
    # A -> a B gives B in delta(A, a)
    # A -> a gives K in delta(A, a)
    # S is final too if S -> epsilon
    final = new_name("K", rg.nonterminals)
    fa = FA(rg.nonterminals + [final], rg.terminals, rg.start, [final])
    for left in rg.nonterminals:
        for right in rg.productions.get(left, []):
            if right == (EPSILON,):
                fa.finals.insert(0, left)
            elif len(right) == 1:
                fa.add_transition(left, right[0], final)
            else:
                fa.add_transition(left, right[0], right[1])
    return fa
