# lab 6 parser for the mini language, made with yacc (we use ply, its yacc for python)
# how it goes:
# 1. the lab 5 scanner reads the program and makes the PIF and ST (same files as before)
# 2. the PIF is given to yacc token by token, so the scanner is the lexer here
# 3. yacc parses with the grammar from grammar.txt (LALR)
# 4. we write the string of productions used, in rightmost derivation order
# usage: py -3.12 parser.py <program file> [grammar file]

import os
import sys

from ply import yacc
from scanner import scan, write_outputs, read_tokens

HERE = os.path.dirname(os.path.abspath(__file__))


def read_grammar(file_name):
    # gives a list of (lhs, rhs list), epsilon becomes an empty rhs
    productions = []
    with open(file_name) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            lhs, rhs = line.split("->")
            rhs = rhs.split()
            if rhs == ["epsilon"]:
                rhs = []
            productions.append((lhs.strip(), rhs))
    return productions


def production_text(prod):
    lhs, rhs = prod
    return lhs + " -> " + (" ".join(rhs) if rhs else "epsilon")


class Token:
    # yacc only needs these 4 fields from a token
    def __init__(self, type, value, lineno, lexpos):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.lexpos = lexpos

    def __repr__(self):
        return self.type


class PifLexer:
    # gives yacc the tokens from the PIF one by one
    # id and const become identifier and constant, the rest is the reserved word itself
    def __init__(self, pif, st):
        self.pif = pif
        self.st = st
        self.i = 0

    def token(self):
        if self.i >= len(self.pif):
            return None
        tok, code, pos, line = self.pif[self.i]
        if code == 0:
            kind, value = "identifier", self.st.get(pos)
        elif code == 1:
            kind, value = "constant", self.st.get(pos)
        else:
            kind, value = tok, tok
        t = Token(kind, value, line, self.i)
        self.i += 1
        return t


class GrammarRules:
    # ply wants the grammar as p_ functions with the rule in the docstring
    # so we make one function per production from grammar.txt
    # every function just remembers its production number when yacc reduces with it

    def __init__(self, productions, terminals):
        self.tokens = terminals
        self.start = productions[0][0]
        self.used = []
        self.error = None
        for nr, (lhs, rhs) in enumerate(productions, start=1):
            func = self.make_rule(nr)
            func.__doc__ = lhs + " : " + " ".join(rhs)
            # the name has the number in it so ply keeps the same order as the file
            setattr(self, "p_%03d" % nr, func)

    def make_rule(self, nr):
        def rule(p):
            self.used.append(nr)
        return rule

    def p_error(self, tok):
        if tok is None:
            self.error = "syntax error: the program ended too early (something is not closed)"
        else:
            self.error = ("syntax error at line " + str(tok.lineno) + ": unexpected " +
                          tok.type + " (" + str(tok.value) + ")")
        # we stop at the first error, its easier to read
        raise SyntaxError(self.error)


def build_parser(grammar_file, tokens_file):
    productions = read_grammar(grammar_file)
    codes = read_tokens(tokens_file)
    terminals = ["identifier", "constant"] + [w for w in codes if w not in ("identifier", "constant")]
    # only keep terminals that are in the grammar, so ply doesnt complain about unused ones
    in_grammar = {s for _, rhs in productions for s in rhs}
    terminals = [t for t in terminals if t in in_grammar]
    rules = GrammarRules(productions, terminals)
    parser = yacc.yacc(module=rules, start=rules.start, write_tables=False, debug=False,
                       errorlog=yacc.NullLogger())
    return parser, rules, productions


def main():
    if len(sys.argv) < 2:
        print("usage: py -3.12 parser.py <program file> [grammar file]")
        return
    program_file = sys.argv[1]
    grammar_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "grammar.txt")
    tokens_file = os.path.join(HERE, "tokens.txt")

    # scanning first, same as lab 5
    pif, st, lex_errors = scan(program_file, tokens_file)
    out_dir, name = write_outputs(program_file, pif, st, lex_errors)
    out_file = os.path.join(out_dir, name + "_productions.txt")

    if lex_errors:
        print(program_file + ": " + str(len(lex_errors)) + " lexical error(s), not parsing it")
        for line_no, col, text, reason in lex_errors:
            print("  line " + str(line_no) + ", column " + str(col) + ": " + text + " (" + reason + ")")
        with open(out_file, "w") as f:
            f.write("not parsed, the program has lexical errors (see " + name + "_errors.txt)\n")
        return

    parser, rules, productions = build_parser(grammar_file, tokens_file)

    try:
        parser.parse(lexer=PifLexer(pif, st))
    except SyntaxError:
        print(program_file + ": " + rules.error)
        with open(out_file, "w") as f:
            f.write(rules.error + "\n")
        return

    # yacc goes bottom up so the reductions come out as a rightmost derivation backwards
    # so we just reverse them to get the derivation from program down to the tokens
    derivation = list(reversed(rules.used))

    with open(out_file, "w") as f:
        f.write("program is syntactically correct\n")
        f.write("string of productions (rightmost derivation, " + str(len(derivation)) + " steps):\n")
        f.write(" ".join(str(nr) for nr in derivation) + "\n\n")
        f.write("the productions in order:\n")
        for step, nr in enumerate(derivation, start=1):
            f.write(str(step) + ". (" + str(nr) + ") " + production_text(productions[nr - 1]) + "\n")

    print(program_file + ": syntactically correct, " + str(len(derivation)) + " productions used")
    print("string of productions: " + " ".join(str(nr) for nr in derivation))
    print("written to " + out_file)


if __name__ == "__main__":
    main()
