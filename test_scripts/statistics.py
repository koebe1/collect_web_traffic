import os.path
import json

# Format of the parsed document
#
# +1
# ||adobedtm.com^$3p,domain=~adobe.com
# --
# www.spiegel.de
# 3
# script
# https://assets.adobedtm.com/cc10f7b4369d/cb3b620b1166/af1da404b6f7/RC862020349d4e4d60bfa847eb35924fc7-source.min.js

scripts = os.path.dirname(os.path.abspath(__file__))
dataset = os.path.dirname(scripts)
dependencies = os.path.join(dataset, 'dependencies')

folder = os.getenv('directory')

json_file = os.path.join(dataset, "captured", folder, "output.json")
uBlockLog = os.path.join(dataset, "captured", folder,  "uBlockLog.txt")

with open(uBlockLog, 'r') as f:
    content = f.read().splitlines()


# extracts url from uBlockLog.txt and writes urls to blocked_URLs_uBlock.txt
def extractURL():
    total_blocked_urls_uBlock = 0
    blocked_urls_ublock = []

    # get index of the blocked sign "--" -> Url is always 4 entrys after "--"
    index = []
    for i, j in enumerate(content):
        if j == '--':
            index.append(i)

    for i in index:
        blocked_urls_ublock.append(content[i+4])
        total_blocked_urls_uBlock += 1

    return total_blocked_urls_uBlock, blocked_urls_ublock


u = extractURL()


# amount of blocked URLS by uBlock
total_blocked_urls_ublock = u[0]

# blocked URLS by uBlock
blocked_urls_ublock = u[1]


def compareToEasyPrivacy():
    total_blocked_urls_easyprivacy = 0
    total_blocked_both = 0
    blocked_both = []
    blocked_urls_easyprivacy = []

    with open(json_file, 'r+') as file:
        # Transforms json input to python objects
        data = json.load(file)

    for packet in data:
        # check in packets labeled as tracker by easyprivacy
        if "true" in packet["tracker"]:
            # count blocked urls by easyprivacy
            total_blocked_urls_easyprivacy += 1
            blocked_urls_easyprivacy.append(packet["http2.header.value.url"])

            if packet["http2.header.value.url"] in blocked_urls_ublock:
                total_blocked_both += 1
                blocked_both.append(packet["http2.header.value.url"])

    return total_blocked_urls_easyprivacy, total_blocked_both, blocked_both, blocked_urls_easyprivacy


d = compareToEasyPrivacy()

total_blocked_urls_easyprivacy = d[0]
total_blocked_both = d[1]
blocked_both = d[2]
blocked_urls_easyprivacy = d[3]

# print(total_blocked_urls_easyprivacy)
# print(total_blocked_both)
# # print(blocked_both)


def writeStatistic():
    f = open(os.path.join(dataset, "captured", folder, "statistics.txt"), "w+")
    f.write("NUMBER URLS BLOCKED BY:" + '\n' '\n' '\n'
            "EasyPrivacy: " + str(total_blocked_urls_easyprivacy) + '\n' '\n'
            "uBlock: " + str(total_blocked_urls_ublock) + '\n' '\n'
            "Overlap:" + str(total_blocked_both) + '\n' '\n' '\n' '\n' '\n'
            "URLS BLOCKED:" + '\n' '\n' '\n'
            "Both:" + '\n' '\n')

    for row in blocked_both:
        f.write('  ' + row + '\n' '\n')

    f.write('\n' '\n' "EasyPrivacy:" + '\n' '\n')

    for row in blocked_urls_easyprivacy:
        f.write('  ' + row + '\n' '\n')

    f.write('\n' '\n' "uBlock:" + '\n' '\n')

    for row in blocked_urls_ublock:
        f.write('  ' + row + '\n' '\n')

    d = open(os.path.join(dataset, "captured",
             folder, "blocked_ublock.txt"), "w+")

    for row in blocked_urls_ublock:
        d.write(row + '\n' '\n')

    h = open(os.path.join(dataset, "captured",
             folder, "blocked_both.txt"), "w+")

    for row in blocked_both:
        h.write(row + '\n' '\n')


writeStatistic()
print("finsihed!")
