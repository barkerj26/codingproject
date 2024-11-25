from cnf import toCnf
from grammario import importGrammar, exportGrammar
import sys


if __name__ != "__main__":
    exit()

if len(sys.argv) < 2:
    print("Please input a file!")
    exit()

grammar = importGrammar(sys.argv[1])

toCnf(grammar)

if len(sys.argv) > 2:
    exportGrammar(grammar, sys.argv[2])