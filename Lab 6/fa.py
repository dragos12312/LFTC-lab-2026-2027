# finite automaton, reads it from a txt file

def read_classes(file_name):
    # reads classes.txt, every line is name = chars
    classes = {}
    with open(file_name) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, chars = line.split("=", 1)
            result = set()
            for part in chars.split():
                if part == "space":
                    result.add(" ")
                elif len(part) == 3 and part[1] == "-":
                    for code in range(ord(part[0]), ord(part[2]) + 1):
                        result.add(chr(code))
                else:
                    result.update(part)
            classes[name.strip()] = result
    return classes


def matches(char, symbol, classes):
    # symbol can be a class (like letter) or just one char
    if symbol in classes:
        return char in classes[symbol]
    return char == symbol


def read_sections(file_name):
    # reads lines like key: values, if nothing is after the : then the next lines go there
    sections = {}
    current = None
    with open(file_name) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, rest = line.partition(":")
            if sep and " " not in key and ("->" not in key):
                current = key.strip()
                sections[current] = []
                if rest.strip():
                    sections[current].append(rest.strip())
            elif current is not None:
                sections[current].append(line)
    return sections


class FA:
    def __init__(self, states, alphabet, initial, finals):
        self.states = list(states)
        self.alphabet = list(alphabet)
        self.initial = initial
        self.finals = list(finals)
        self.transitions = {} # (state, symbol) -> list of states

    def add_transition(self, source, symbol, target):
        targets = self.transitions.setdefault((source, symbol), [])
        if target not in targets:
            targets.append(target)

    @staticmethod
    def read(file_name):
        s = read_sections(file_name)
        fa = FA(s["states"][0].split(), s["alphabet"][0].split(),
                s["initial"][0].strip(), s["final"][0].split() if s.get("final") else [])
        for line in s.get("transitions", []):
            source, symbol, target = line.split()
            if source not in fa.states or target not in fa.states:
                raise ValueError("unknown state in transition: " + line)
            if symbol not in fa.alphabet:
                raise ValueError("unknown symbol in transition: " + line)
            fa.add_transition(source, symbol, target)
        if fa.initial not in fa.states:
            raise ValueError("initial state is not in Q")
        for state in fa.finals:
            if state not in fa.states:
                raise ValueError("final state is not in Q: " + state)
        return fa

    def is_deterministic(self):
        # dfa if every (state, symbol) goes to max one state
        return all(len(targets) == 1 for targets in self.transitions.values())

    def accepts(self, word, classes):
        # keeps all the states we can be in, so it works for nfa too
        current = {self.initial}
        for char in word:
            following = set()
            for state in current:
                for symbol in self.alphabet:
                    if matches(char, symbol, classes):
                        following.update(self.transitions.get((state, symbol), []))
            current = following
            if not current:
                return False
        return any(state in self.finals for state in current)

    def __str__(self):
        lines = []
        lines.append("M = (Q, Sigma, delta, q0, F)")
        lines.append("Q = {" + ", ".join(self.states) + "}")
        lines.append("Sigma = {" + ", ".join(self.alphabet) + "}")
        lines.append("q0 = " + self.initial)
        lines.append("F = {" + ", ".join(self.finals) + "}")
        lines.append("delta:")
        for (source, symbol), targets in self.transitions.items():
            lines.append("delta(" + source + ", " + symbol + ") = " +
                         ("{" + ", ".join(targets) + "}" if len(targets) > 1 else targets[0]))
        lines.append("")
        lines.append("transition table (-> is initial, * is final):")
        width = max([len(x) for x in self.alphabet + self.states] + [5]) + 2
        cells = {}
        for state in self.states:
            for symbol in self.alphabet:
                targets = self.transitions.get((state, symbol), [])
                if not targets:
                    cells[(state, symbol)] = "-"
                elif len(targets) == 1:
                    cells[(state, symbol)] = targets[0]
                else:
                    cells[(state, symbol)] = "{" + ",".join(targets) + "}"
        width = max([width] + [len(c) + 2 for c in cells.values()])
        lines.append("".ljust(width + 3) + "".join(sym.ljust(width) for sym in self.alphabet))
        for state in self.states:
            mark = ("->" if state == self.initial else "  ") + ("*" if state in self.finals else " ")
            lines.append(mark + state.ljust(width) +
                         "".join(cells[(state, sym)].ljust(width) for sym in self.alphabet))
        lines.append("deterministic: " + ("yes" if self.is_deterministic() else "no"))
        return "\n".join(lines)
