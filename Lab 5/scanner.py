# scanner for the mini language, lab 5 version
# identifiers and constants are checked with the fa from lab 4 now, no regex anymore
# identifiers use identifier_fa.txt directly
# constants use constant_rg.txt, the rg gets turned into a fa first (rg_to_fa)
# usage: py -3.12 scanner.py <program file> [tokens file]
# writes <name>_PIF.txt, <name>_ST.txt and <name>_errors.txt in the output folder

import os
import sys

from fa import FA, read_classes
from rg import RG
from transform import rg_to_fa
from symbol_table import SymbolTable

HERE = os.path.dirname(os.path.abspath(__file__))


def load_fa(file_name):
    # if the file is a grammar we make the fa from it, else its already a fa
    with open(file_name) as f:
        is_rg = "productions:" in f.read()
    if is_rg:
        return rg_to_fa(RG.read(file_name))
    return FA.read(file_name)


CLASSES = read_classes(os.path.join(HERE, "classes.txt"))
IDENTIFIER_FA = load_fa(os.path.join(HERE, "identifier_fa.txt"))
CONSTANT_FA = load_fa(os.path.join(HERE, "constant_rg.txt"))


def is_identifier(word):
    return IDENTIFIER_FA.accepts(word, CLASSES)


def is_constant(word):
    return CONSTANT_FA.accepts(word, CLASSES)


def read_tokens(file_name):
    # reads the tokens file, each line is token code
    codes = {}
    with open(file_name) as f:
        for line in f:
            parts = line.split()
            if len(parts) == 2:
                codes[parts[0]] = int(parts[1])
    return codes


def word_error(word):
    # gives a reason for a word that the fa didnt accept
    digits = CLASSES["digit"]
    id_chars = CLASSES["letter"] | digits | CLASSES["underscore"]
    if len(word) > 1 and word[0] == "0" and all(c in digits for c in word):
        return "number cannot start with 0"
    if all(c in id_chars for c in word):
        if word[0] in digits:
            return "identifier cannot start with a digit"
        if word[0] == "_":
            return "identifier cannot start with _"
    return "invalid character(s)"


def scan(program_file, tokens_file):
    codes = read_tokens(tokens_file)
    st = SymbolTable()
    pif = [] # (token, code, st position or -1)
    errors = []

    with open(program_file) as f:
        lines = f.readlines()

    for line_no, line in enumerate(lines, start=1):
        line = line.rstrip("\n")
        i = 0
        while i < len(line):
            if line[i].isspace():
                i += 1
                continue

            # string constant, we take everything up to the next quote and give it to the fa
            if line[i] == '"':
                end = line.find('"', i + 1)
                if end == -1:
                    errors.append((line_no, i + 1, line[i:], "string is not closed"))
                    i = len(line)
                    continue
                text = line[i:end + 1]
                if is_constant(text):
                    pos = st.add(text)
                    pif.append(("const", codes["constant"], pos))
                else:
                    errors.append((line_no, i + 1, text, "invalid character in string"))
                i = end + 1
                continue

            # anything else is a word until the next space or quote
            j = i
            while j < len(line) and not line[j].isspace() and line[j] != '"':
                j += 1
            word = line[i:j]
            if word in codes and word not in ("identifier", "constant"):
                pif.append((word, codes[word], -1))
            elif is_identifier(word):
                pos = st.add(word)
                pif.append(("id", codes["identifier"], pos))
            elif is_constant(word):
                pos = st.add(word)
                pif.append(("const", codes["constant"], pos))
            else:
                errors.append((line_no, i + 1, word, word_error(word)))
            i = j

    return pif, st, errors


def main():
    if len(sys.argv) < 2:
        print("usage: py -3.12 scanner.py <program file> [tokens file]")
        return
    program_file = sys.argv[1]
    tokens_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "tokens.txt")

    pif, st, errors = scan(program_file, tokens_file)

    out_dir = os.path.join(HERE, "output")
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
