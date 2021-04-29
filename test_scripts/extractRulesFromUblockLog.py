import os
import os.path

folder = os.getenv('directory')
path = "/Users/bene/Desktop/dataset/captured/"
file = "uBlockLog.txt"

joinedPath = os.path.join(path, folder, file)

rules = []


def extractFilterRules():
    # Operators the rules of EasyPrivacy start with:
    ruleOperators = ("/", "||", "&", ".", "_", ":", "$", "@@")
    # open /Users/bene/Desktop/dataset/captured/&directory/uBlockLog.txt and loop through content
    with open(joinedPath, "r") as file:
        for line in file:
            # specify starting character of the filter rule
            if line.startswith(ruleOperators):
                # check if rules already exiists
                if line not in rules:
                    # remove newline character from each line and append it to rules
                    rules.append(line.rstrip("\n"))


extractFilterRules()
print(rules)
