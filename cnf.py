from grammar import isTerminal
from grammar import optionToString
from grammar import stringToOption


# remove the nth matched element from a list
def omit(li, match, n):
    count = 0
    newList = []
    for i in li:
        if i != match or (i == match and count != n):
            newList.append(i)

        if i == match:
            count += 1

    return newList


# make a term optional in an option, creating 2^|optionalTerm| options
def makeOptional(grammar, optionalTerm, nonTerminal, option):
    finalSet = {}
    runningSet = {
        optionToString(option): True
    }

    count = option.count(optionalTerm)
    for i in range(0, count):
        nextSet = {}

        for cur in runningSet:
            for j in range(0, count - i):
                nextSet[optionToString(omit(stringToOption(cur), optionalTerm, j))] = True

        finalSet = finalSet | nextSet
        runningSet = nextSet

    finalList = []
    for str in finalSet:
        finalList.append(stringToOption(str))

    grammar.getRule(nonTerminal).extend(finalList)


def epsilonInternal(grammar, nonTerminal, rule):
    if nonTerminal == "_S0":
        rule.append([])
        return

    rule[:] = [x for x in rule if x != []]

    for nonTerminal1, rule1 in grammar.findRulesWithTerm(nonTerminal).items():
        for option in rule1[:]:
            if len(option) == 1 and option[0] == nonTerminal:
                epsilonInternal(grammar, nonTerminal1, rule1)
                continue

            for term in option:
                if term == nonTerminal:
                    makeOptional(grammar, nonTerminal, nonTerminal1, option)
                    break


# move epsilon up so only the starting rule has one
def epsilon(grammar):
    for nonTerminal, rule in grammar.findRulesWithTerm("").items():
        epsilonInternal(grammar, nonTerminal, rule)

    grammar.clearSelfReferencing()


def singletInternal(grammar):
    for nonTerminal in grammar.getNonTerminals():
        rule = grammar.getRule(nonTerminal)

        for i in range(len(rule) - 1, -1, -1):
            option = rule[i]

            if len(option) != 1 or isTerminal(option[0]):
                continue

            rule.extend(grammar.getRule(option[0]))
            rule.pop(i)

        grammar.clearSelfReferencingRule(nonTerminal)

    for rule in grammar.getRules().values():
        for option in rule:
            if len(option) == 1 and not isTerminal(option[0]):
                singletInternal(grammar)


# replace singlet nonterminals with all of their rules
def singlet(grammar):
    singletInternal(grammar)
    grammar.clearOrphanRules()


def overtermInternal(grammar, nonTerminal):
    rule = grammar.getRule(nonTerminal)

    for i in range(len(rule) - 1, -1, -1):
        option = rule[i]

        if len(option) <= 2:
            continue

        newOption = option[1:]
        newNonTerminal = grammar.findByRule([newOption])
        if not newNonTerminal:
            newNonTerminal = grammar.findUniqueName(nonTerminal)
            grammar.addOption(newNonTerminal, newOption)

        checkRule = rule.copy()
        checkRule[i] = option[0:1]
        checkRule[i].append(newNonTerminal)

        dupedNonTerminal = grammar.findByRule(checkRule)
        if dupedNonTerminal and dupedNonTerminal != nonTerminal:
            grammar.clearDuplicateRule(nonTerminal, dupedNonTerminal)
        else:
            rule[:] = checkRule

        overtermInternal(grammar, newNonTerminal)


# split up 3+ term options
def overterm(grammar):
    for nonTerminal in grammar.getNonTerminals()[:]:
        overtermInternal(grammar, nonTerminal)

    # because we are cleaning up extra dupes after the fact, this results in the numbers for uniques skipping
    grammar.clearDuplicates()


def mixedtermInternal(grammar, nonTerminal):
    rule = grammar.getRule(nonTerminal)

    for option in rule:
        if len(option) != 2:
            continue

        if isTerminal(option[0]):
            newRule = [option[0]]
            newNonTerminal = grammar.findByRule([newRule])
            if not newNonTerminal:
                newNonTerminal = grammar.findUniqueName(nonTerminal)
                grammar.addOption(newNonTerminal, newRule)

            option[0] = newNonTerminal

        if isTerminal(option[1]):
            newRule = [option[1]]
            newNonTerminal = grammar.findByRule([newRule])
            if not newNonTerminal:
                newNonTerminal = grammar.findUniqueName(nonTerminal)
                grammar.addOption(newNonTerminal, newRule)

            option[1] = newNonTerminal


# make sure all 2-term entries are non/non
def mixedterm(grammar):
    for nonTerminal in grammar.getNonTerminals():
        mixedtermInternal(grammar, nonTerminal)


def toCnf(grammar):
    print("\ninput:")
    print(grammar)
    print("\n------\n")

    newStart = grammar.findUniqueName("_S0")
    grammar.addOption(newStart, ["_S"])
    grammar.setStartRule(newStart)

    epsilon(grammar)
    singlet(grammar)
    overterm(grammar)
    mixedterm(grammar)

    print("output:")
    print(grammar)
    print("")