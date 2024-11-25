import re


def isTerminal(term):
    return term[:1] != "_"


def optionToString(option):
    return " ".join(option)


def stringToOption(string):
    return string.split(" ")


def ruleToString(rule):
    options = []
    for option in rule:
        options.append(optionToString(option))

    return " | ".join(options)


def _clearSelfReferencingOption(nonTerminal, option):
    if len(option) == 1 and option[0] == nonTerminal:
        return False

    return True


def _cleanOption(option, nonTerminals):
    for term in option:
        if not isTerminal(term) and not term in nonTerminals:
            return False

    option[:] = [x for x in option if x != ""]

    return True


def _ruleHasTerm(rule, check):
    for option in rule:
        for term in option:
            if term == check:
                return True

    return False


def _ruleHasEpsilonTerm(rule):
    for option in rule:
        if len(option) <= 0:
            return True

    return False


class GrammarException(Exception):
    pass


class Grammar:
    startRule = "_S"
    rules = {}


    def __init__(self, str):
        self.fromString(str)


    def __str__(self):
        stream = []

        stream.append(self.startRule)
        stream.append("->")

        optionStream = []
        for rule in self.rules[self.startRule]:
            optionStream.append(optionToString(rule))

        stream.append(" | ".join(optionStream))
        stream.append(";")

        for nonTerminal, rule in self.rules.items():
            if nonTerminal == self.startRule:
                continue

            stream.append(nonTerminal)
            stream.append("->")

            optionStream = []
            for rule in rule:
                optionStream.append(optionToString(rule))

            stream.append(" | ".join(optionStream))
            stream.append(";")

        return " ".join(stream).replace("; ", ";\n")


    # convert a string into a grammar object
    def fromString(self, str):
        stream = str.replace("\n", " ").split(" ")

        state = -1
        nonTerminal = ""
        option = []

        for elem in stream:
            if state == -1:
                self.startRule = elem
                state = 0

            if state == 0:
                if elem == "":
                    continue

                if isTerminal(elem):
                    raise GrammarException("Only nonterminals can have rules (nonterminals start with _):", elem)

                nonTerminal = elem
                state = 1
            elif state == 1:
                if elem != "->":
                    raise GrammarException("Nonterminal definition doesn't include a ->:", elem)

                state = 2
            elif state == 2:
                if elem == "|":
                    self.addOption(nonTerminal, option)
                    option = []
                    continue

                if elem == ";":
                    self.addOption(nonTerminal, option)
                    state = 0
                    option = []
                    continue

                option.append(elem)

        if state > 0:
            raise GrammarException("Nonterminal definition started but wasn't ended with ;")

        self.cleanup()


    # returns whether the inputted nonterminal has rules
    def hasNonTerminal(self, nonTerminal):
        return nonTerminal in self.rules


    # set the rule that should be the first
    def setStartRule(self, nonTerminal):
        if not self.hasNonTerminal(nonTerminal):
            return

        self.startRule = nonTerminal


    # get the first rule
    def getStartRule(self):
        return self.startRule


    # serves the purpose of adding a nonterminal ruleset AND its options
    def addOption(self, nonTerminal, option):
        if type(option) is not list:
            return

        if not self.hasNonTerminal(nonTerminal):
            self.rules[nonTerminal] = []

        self.rules[nonTerminal].append(option)


    # get the rule definition for a nonterminal
    def getRule(self, nonTerminal):
        return self.rules[nonTerminal]


    # get all rules
    def getRules(self):
        return self.rules


    # remove a nonterminal definition / rule
    def removeRule(self, nonTerminal):
        if self.hasNonTerminal(nonTerminal):
            self.rules.pop(nonTerminal)


    # remove a rule and replace all occurances of it with another
    def clearDuplicateRule(self, nonTerminal, dupedNonTerminal):
        if nonTerminal == dupedNonTerminal:
            return

        if self.startRule == nonTerminal:
            self.startRule = dupedNonTerminal

        self.removeRule(nonTerminal)

        for rule in self.getRules().values():
            for option in rule:
                for n in range(len(option)):
                    if option[n] == nonTerminal:
                        option[n] = dupedNonTerminal


    # ensure every rule is unique
    # this can be EXTREMELY intensive for cascaded duplication
    def clearDuplicates(self):
        checkedRules = {}
        changed = False
        for nonTerminal in self.getNonTerminals():
            ruleStr = ruleToString(self.getRule(nonTerminal))
            if ruleStr in checkedRules:
                changed = True
                self.clearDuplicateRule(nonTerminal, checkedRules[ruleStr])
            else:
                checkedRules[ruleStr] = nonTerminal

        if changed:
            self.clearDuplicates()


    # remove an option by index
    def removeOption(self, nonTerminal, index):
        if self.hasNonTerminal(nonTerminal):
            self.rules[nonTerminal].pop(index)

        if len(self.getRule(nonTerminal)) <= 0:
            self.removeRule(nonTerminal)


    # return a list of rules that contain a particular term
    def findRulesWithTerm(self, term):
        if term == "":
            rules = {}
            for nonTerminal, rule in self.rules.items():
                if _ruleHasEpsilonTerm(rule):
                    rules[nonTerminal] = rule

            return rules

        rules = {}
        for nonTerminal, rule in self.rules.items():
            if _ruleHasTerm(rule, term):
                rules[nonTerminal] = rule

        return rules


    # clear away rules that have no usage
    def clearOrphanRules(self):
        for nonTerminal in self.getNonTerminals():
            if self.startRule != nonTerminal and not self.findRulesWithTerm(nonTerminal):
                self.rules.pop(nonTerminal)


    # get all nonterminals
    def getNonTerminals(self):
        return list(self.rules.keys())


    # ensure a specific rule does not have any self referencing
    def clearSelfReferencingRule(self, nonTerminal):
        rule = self.getRule(nonTerminal)
        rule[:] = [x for x in rule if _clearSelfReferencingOption(nonTerminal, x)]


    # remove self-referencing options
    def clearSelfReferencing(self):
        for nonTerminal, rule in self.rules.items():
            rule[:] = [x for x in rule if _clearSelfReferencingOption(nonTerminal, x)]


    # find a nonterminal by its ruleset
    def findByRule(self, rule):
        for nonTerminal, rule1 in self.rules.items():
            if rule == rule1:
                return nonTerminal


    # get a unique nonterminal name
    def findUniqueName(self, nonTerminal):
        if not self.hasNonTerminal(nonTerminal):
            return nonTerminal

        count = 1
        nums = re.findall("[0-9]+$", nonTerminal)
        if len(nums) > 0:
            count = int(nums[0])

        text = re.sub("[0-9]+$", "", nonTerminal)

        while True:
            unique = text + str(count)
            if not self.hasNonTerminal(unique):
                return unique

            count = count + 1


    # all nonterminals must have at least 1 rule
    # rules cannot reference their own nonterminal on its own
    # no duplicate options
    # no empty string (epsilon is an empty option)
    # no options with invalid/undefined nonterminals
    def cleanup(self):
        nonTerminals = {}

        for nonTerminal in self.getNonTerminals():
            if len(self.rules[nonTerminal]) <= 0:
                self.removeRule(nonTerminal)
                continue

            nonTerminals[nonTerminal] = True

        self.clearSelfReferencing()

        for nonTerminal, rule in self.rules.items():
            rule[:] = [x for x in rule if _cleanOption(x, nonTerminals)]

        for rule in self.rules.values():
            knownOptions = {}

            for i in range(len(rule) - 1, -1, -1):
                optionStr = optionToString(rule[i])
                if optionStr in knownOptions:
                    rule.pop(i)
                    continue

                knownOptions[optionStr] = True