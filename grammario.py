from grammar import Grammar
from grammar import GrammarException


def exportGrammar(grammar, file):
    try:
        f = open(file, "w")
    except:
        print("Failed to export the grammar")
        return

    f.write(str(grammar))
    f.close()
    print("Exported the resulting grammar to", file)


def importGrammar(file):
    try:
        f = open(file, "r")
    except FileNotFoundError:
        print("Invalid file!")
        exit()

    try:
        grammar = Grammar(f.read())
    except GrammarException as error:
        print("Grammar has an invalid format!")
        print(error)
        f.close()
        exit()

    f.close()
    return grammar



