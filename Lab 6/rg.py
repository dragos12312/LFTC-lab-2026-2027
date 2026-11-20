# regular grammar (right linear), reads it from a txt file

from fa import read_sections

EPSILON = "epsilon"


class RG:
    def __init__(self, nonterminals, terminals, start):
        self.nonterminals = list(nonterminals)
        self.terminals = list(terminals)
        self.start = start
        self.productions = {} # nonterminal -> list of right sides

    def add_production(self, left, right):
        rights = self.productions.setdefault(left, [])
        if tuple(right) not in rights:
            rights.append(tuple(right))

    @staticmethod
    def read(file_name):
        s = read_sections(file_name)
        rg = RG(s["nonterminals"][0].split(), s["terminals"][0].split(), s["start"][0].strip())
        for line in s.get("productions", []):
            left, arrow, rights = line.partition("->")
            if not arrow:
                raise ValueError("production without -> : " + line)
            for right in rights.split("|"):
                rg.add_production(left.strip(), right.split())
        error = rg.check_regular()
        if error:
            raise ValueError(file_name + " is not a regular grammar: " + error)
        return rg

    def check_regular(self):
        # productions must be A -> a, A -> aB or S -> epsilon
        # if S -> epsilon then S cant be on the right side
        # returns None if ok, else the reason why its not regular
        if self.start not in self.nonterminals:
            return "start symbol is not in N"
        has_epsilon = False
        for left, rights in self.productions.items():
            if left not in self.nonterminals:
                return "left side " + left + " is not a nonterminal"
            for right in rights:
                if right == (EPSILON,):
                    if left != self.start:
                        return left + " -> epsilon, only the start symbol may go to epsilon"
                    has_epsilon = True
                elif len(right) == 1:
                    if right[0] not in self.terminals:
                        return left + " -> " + right[0] + " must be a terminal"
                elif len(right) == 2:
                    if right[0] not in self.terminals or right[1] not in self.nonterminals:
                        return left + " -> " + " ".join(right) + " must be terminal nonterminal"
                else:
                    return left + " -> " + " ".join(right) + " is too long"
        if has_epsilon:
            for rights in self.productions.values():
                for right in rights:
                    if len(right) == 2 and right[1] == self.start:
                        return "S -> epsilon but S appears on a right side"
        return None

    def __str__(self):
        lines = []
        lines.append("G = (N, Sigma, P, S)")
        lines.append("N = {" + ", ".join(self.nonterminals) + "}")
        lines.append("Sigma = {" + ", ".join(self.terminals) + "}")
        lines.append("S = " + self.start)
        lines.append("P:")
        for left in self.nonterminals:
            if left in self.productions:
                rights = [" ".join(r) for r in self.productions[left]]
                lines.append(left + " -> " + " | ".join(rights))
        error = self.check_regular()
        lines.append("regular: " + ("yes" if error is None else "no (" + error + ")"))
        return "\n".join(lines)
