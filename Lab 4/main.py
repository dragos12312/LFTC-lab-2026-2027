# lab 4 - fa and rg for identifiers and constants
# run it with no arguments for the demo (saves the results in output)
# or main.py fa file / main.py rg file to see the transformation of one file
# or main.py check file word to see if a word is accepted

import os
import sys

from fa import FA, read_classes
from rg import RG
from transform import fa_to_rg, rg_to_fa

HERE = os.path.dirname(os.path.abspath(__file__))

TEST_WORDS = {
    "identifier": ["x", "total_sum", "a1b2", "Var_", "RECRUIT",
                   "1abc", "_x", "x-y", "my var", ""],
    "constant": ["0", "7", "120", '"hello world"', '""', '"Score: 10!"',
                 "007", "-5", '"open', '"bad#"', ""],
}


def show(word):
    return "epsilon (empty word)" if word == "" else word


def is_rg_file(file_name):
    with open(file_name) as f:
        return "productions:" in f.read()


def demo(name, classes):
    fa = FA.read(os.path.join(HERE, name + "_fa.txt"))
    rg = RG.read(os.path.join(HERE, name + "_rg.txt"))
    rg_from_fa = fa_to_rg(fa)
    fa_from_rg = rg_to_fa(rg)
    fa_back = rg_to_fa(rg_from_fa)

    out = []
    out.append("---- " + name + "s ----")
    out.append("")
    out.append("1. fa from " + name + "_fa.txt")
    out.append(str(fa))
    out.append("")
    out.append("2. rg made from this fa (fa -> rg)")
    out.append(str(rg_from_fa))
    out.append("")
    out.append("3. rg from " + name + "_rg.txt")
    out.append(str(rg))
    out.append("")
    out.append("4. fa made from this rg (rg -> fa)")
    out.append(str(fa_from_rg))
    out.append("")
    out.append("5. checking some words")
    out.append("A = fa from the file, B = fa made from the rg file, C = fa -> rg -> fa")
    out.append("word".ljust(24) + "A".ljust(10) + "B".ljust(10) + "C".ljust(10))
    all_same = True
    for word in TEST_WORDS[name]:
        results = [fa.accepts(word, classes), fa_from_rg.accepts(word, classes),
                   fa_back.accepts(word, classes)]
        if len(set(results)) > 1:
            all_same = False
        out.append(show(word).ljust(24) +
                   "".join(("accepted" if r else "rejected").ljust(10) for r in results))
    out.append("all 3 give the same answer: " + ("yes" if all_same else "no"))
    out.append("")
    return "\n".join(out)


def main():
    classes = read_classes(os.path.join(HERE, "classes.txt"))
    args = sys.argv[1:]

    if not args:
        out_dir = os.path.join(HERE, "output")
        os.makedirs(out_dir, exist_ok=True)
        for name in ("identifier", "constant"):
            text = demo(name, classes)
            with open(os.path.join(out_dir, name + "_results.txt"), "w") as f:
                f.write(text + "\n")
            print(text)
        print("saved in the output folder")
    elif args[0] == "fa" and len(args) == 2:
        fa = FA.read(args[1])
        print("fa:")
        print(fa)
        print("\nrg made from the fa:")
        print(fa_to_rg(fa))
    elif args[0] == "rg" and len(args) == 2:
        rg = RG.read(args[1])
        print("rg:")
        print(rg)
        print("\nfa made from the rg:")
        print(rg_to_fa(rg))
    elif args[0] == "check" and len(args) == 3:
        if is_rg_file(args[1]):
            fa = rg_to_fa(RG.read(args[1]))
        else:
            fa = FA.read(args[1])
        word = args[2]
        print(show(word) + ": " + ("accepted" if fa.accepts(word, classes) else "rejected"))
    else:
        print("usage: python3 main.py [fa <FA file> | rg <RG file> | check <file> <word>]")


if __name__ == "__main__":
    main()
