# lexical analyzer (scanner) for the mini-language.
# usage: python3 scanner.py <program file> [tokens file]
# writes <name>_PIF.txt, <name>_ST.txt and <name>_errors.txt in the output folder.

import os
import re
import sys

from symbol_table import SymbolTable

IDENTIFIER_RE = re.compile(r'[A-Za-z][A-Za-z0-9_]*')
NUMBER_RE = re.compile(r'0|[1-9][0-9]*')
STRING_RE = re.compile(r'"[A-Za-z0-9 :,.!?_\-]*"')
WHITESPACE_RE = re.compile(r'\s+')
WORD_RE = re.compile(r'[^\s"]+')


def read_tokens(file_name):
    # reads the tokens file: each line is "<token> <code>"
    codes = {}
    with open(file_name) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                codes[parts[0]] = int(parts[1])
    return codes


def word_error(word):
    # gives a reason for a word that is not a valid token
    if re.fullmatch(r'0[0-9]+', word):
        return "number cannot start with 0"
    if re.match(r'[0-9]+[A-Za-z_]', word):
        return "identifier cannot start with a digit"
    if re.match(r'[A-Za-z0-9_]+$', word):
        return "identifier cannot start with _"
    return "invalid character(s)"


def scan(program_file, tokens_file):
    codes = read_tokens(tokens_file)
    st = SymbolTable()
    pif = []     # list of (token, code, ST position or -1)
    errors = []

    with open(program_file) as f:
        lines = f.readlines()

    for line_no, line in enumerate(lines, start=1):
        line = line.rstrip("\n")
        i = 0
        while i < len(line):
            m = WHITESPACE_RE.match(line, i)
            if m:
                i = m.end()
                continue

            # string constant
            if line[i] == '"':
                m = STRING_RE.match(line, i)
                if m:
                    text = m.group()
                    pos = st.add(text)
                    pif.append(("const", codes["constant"], pos))
                    i = m.end()
                else:
                    end = line.find('"', i + 1)
                    if end == -1:
                        errors.append((line_no, i + 1, line[i:], "string is not closed"))
                        i = len(line)
                    else:
                        errors.append((line_no, i + 1, line[i:end + 1],
                                       "invalid character in string"))
                        i = end + 1
                continue

            # anything else is a word up to the next space or quote
            m = WORD_RE.match(line, i)
            word = m.group()
            if word in codes and word not in ("identifier", "constant"):
                pif.append((word, codes[word], -1))
            elif IDENTIFIER_RE.fullmatch(word):
                pos = st.add(word)
                pif.append(("id", codes["identifier"], pos))
            elif NUMBER_RE.fullmatch(word):
                pos = st.add(word)
                pif.append(("const", codes["constant"], pos))
            else:
                errors.append((line_no, i + 1, word, word_error(word)))
            i = m.end()

    return pif, st, errors


def main():
    if len(sys.argv) < 2:
        print("usage: python3 scanner.py <program file> [tokens file]")
        return
    program_file = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    tokens_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "tokens.txt")

    pif, st, errors = scan(program_file, tokens_file)

    out_dir = os.path.join(here, "output")
    os.makedirs(out_dir, exist_ok=True)
    name = os.path.splitext(os.path.basename(program_file))[0]

    with open(os.path.join(out_dir, name + "_PIF.txt"), "w") as f:
        f.write("Program Internal Form\n")
        f.write("token".ljust(16) + "code".ljust(6) + "ST position\n")
        for token, code, pos in pif:
            if pos == -1:
                pos_text = "-1"
            else:
                pos_text = "(" + str(pos[0]) + ", " + str(pos[1]) + ")"
            f.write(token.ljust(16) + str(code).ljust(6) + pos_text + "\n")

    st.write(os.path.join(out_dir, name + "_ST.txt"))

    with open(os.path.join(out_dir, name + "_errors.txt"), "w") as f:
        if not errors:
            f.write("Lexically correct\n")
        for line_no, col, text, reason in errors:
            f.write("Lexical error at line " + str(line_no) + ", column " + str(col) +
                    ": " + text + " (" + reason + ")\n")

    if not errors:
        print(program_file + ": lexically correct")
    else:
        print(program_file + ": " + str(len(errors)) + " lexical error(s)")
        for line_no, col, text, reason in errors:
            print("  line " + str(line_no) + ", column " + str(col) + ": " +
                  text + " (" + reason + ")")


if __name__ == "__main__":
    main()
