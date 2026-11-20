lab 6 - what i did and how to run it

the task was parsing with yacc or antlr. i used ply, its yacc for python, so everything stays in python like the other labs and you dont need flex, bison or java.
ply is already copied in the ply folder (only yacc.py and __init__.py, ply 3.11), so no pip install needed.

files:
parser.py - the new part, the parser. runs the scanner, gives the PIF to yacc, writes the string of productions
grammar.txt - the grammar, one production per line, the parser reads it from here (input grammar)
documentation.txt - the grammar doc (deliverable 1)
scanner.py - lab 5 scanner, only small changes: the PIF also remembers the line of each token and the file writing is in its own function so the parser can use it
fa.py, rg.py, transform.py, classes.txt, identifier_fa.txt, constant_rg.txt - from lab 4/5, the scanner needs them
symbol_table.py, symbol_table.c - the symbol table from lab 3 (gets compiled with gcc the first time)
tokens.txt - token codes, same as before
ply/ - the yacc library
p1.txt, p2.txt - correct programs
p_err.txt - has lexical errors, so it stops after scanning
p_syntax_err.txt - lexically ok but has a syntax error
output/ - what you get after running all 4

how to run (open cmd in the L6 folder):
py -3.12 parser.py p1.txt
py -3.12 parser.py p2.txt
py -3.12 parser.py p_err.txt
py -3.12 parser.py p_syntax_err.txt

it prints if the program is correct and the string of productions, and writes in output/:
p1_PIF.txt, p1_ST.txt, p1_errors.txt - same as lab 5
p1_productions.txt - the string of productions (numbers) and then every step with the production written out

the numbers are the production numbers from grammar.txt / documentation.txt (first line is 1).
the order is a rightmost derivation, yacc goes bottom up so we take the reductions and reverse them. if the teacher asks, thats the explanation.

you can also give another grammar file: py -3.12 parser.py p1.txt grammar.txt

if you want to show it catching an error live, delete a APOCALYPSE from p1.txt and run it, it says the program ended too early.
