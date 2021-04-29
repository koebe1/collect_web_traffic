from __future__ import print_function
import json
import re
from adblockparser import AdblockRules
import os.path
import os
import operator

# Format of the parsed ublock log
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


# define file path of the file you want to update
file = os.path.join(dataset, "captured", folder, "output.json")


def addHeaderValues():
    with open(file, 'r+') as jsonFile:
        # Transforms json input to python objects
        data = json.load(jsonFile)

        # loop through packets
        for packet in data:
            # packet["tracker"] = "false"
            # if http2 layer exists keep looking deeper in the packet
            if "http2" in packet['_source']['layers']:
                if "http2.stream" in packet['_source']['layers']['http2']:
                    if "http2.header" in packet['_source']['layers']['http2']['http2.stream']:
                        http2 = packet['_source']['layers']['http2']
                        header = http2['http2.stream']['http2.header']

                        # if there is a http2.header
                        if 'http2.header.value' in header[0]:
                            # check if url starts with http or https -> if there is a url in the header.value

                            if 'http' in header[2]["http2.header.value"]:
                                try:
                                    packet["http2.header.value.url"] = header[2]["http2.header.value"] + \
                                        "://" + header[1]['http2.header.value'] + \
                                        header[3]['http2.header.value']
                                except IndexError:
                                    pass

        # rewind json so the file gets updated not appended
        jsonFile.seek(0)
        # write to file
        json.dump(data, jsonFile, indent=4)


addHeaderValues()

uBlockLog = os.path.join(dataset, "captured", folder,  "uBlockLog.txt")

with open(uBlockLog, 'r') as f:
    content = f.read().splitlines()

# extracts url from uBlockLog.txt and writes urls to blocked_URLs_uBlock.txt


def extractUrlUblock():
    total_blocked_urls_ublock = 0
    blocked_urls_ublock = []

    # get index of the blocked sign "--" -> Url is always 4 entrys after "--"
    index = []
    for i, j in enumerate(content):
        if j == '--':
            index.append(i)

    for i in index:
        blocked_urls_ublock.append(content[i+4])
        total_blocked_urls_ublock += 1

    return total_blocked_urls_ublock, blocked_urls_ublock


u = extractUrlUblock()

# amount of blocked URLS by uBlock
total_blocked_urls_ublock = u[0]

# blocked URLS by uBlock
blocked_urls_ublock = u[1]


def label():
    with open(file, 'r+') as jsonFile:
        # Transforms json input to python objects
        data = json.load(jsonFile)

        # loop through packets
        for packet in data:
            packet["tracker"] = "false"

            # check for url entry
            if "http2.header.value.url" in packet:
                headerUrl = packet["http2.header.value.url"]

                # check if url blocked by ublock is in http2.header.value.url
                if headerUrl in blocked_urls_ublock:
                    packet["tracker"] = "true"

            # if "http" in packet['_source']['layers']:
            #     if headerUrl in packet['_source']['layers']['http']['http.response_for.uri']:
            #         packet["tracker"] = "true"

        # rewind json so the file gets updated not appended
        jsonFile.seek(0)
        # write to file
        json.dump(data, jsonFile, indent=4)


label()


def get_urls_programm():
    blocked_urls_program = []
    total_blocked_program = 0

    with open(file, 'r+') as jsonFile:
        # Transforms json input to python objects
        data = json.load(jsonFile)

        # loop through packets
    for packet in data:

        if "true" in packet["tracker"]:
            total_blocked_program += 1
            blocked_urls_program.append(packet["http2.header.value.url"])

    return total_blocked_program, blocked_urls_program


g = get_urls_programm()
total_blocked_program = g[0]
blocked_urls_program = g[1]


def compareToUblock():
    total_missed_by_program = 0
    missed = []

    # get elements missed by the program -> sometimes url in header value gets cut -> check for substring from header value/ urls programm in urls ublock
    missed = [x for x in blocked_urls_ublock if not any(
        b in x for b in blocked_urls_program)]

    total_missed_by_program = len(missed)

    return total_missed_by_program, missed


d = compareToUblock()

total_missed_by_program = d[0]
missed = d[1]


def writeStatistic():
    f = open(os.path.join(dataset, "captured", folder, "statistics.txt"), "w+")
    f.write("NUMBER URLS BLOCKED BY:" + '\n' '\n' '\n'
            "Program: " + str(total_blocked_program) +
            " length array: " + str(len(blocked_urls_program)) + '\n' '\n'
            "uBlock: " + str(total_blocked_urls_ublock) +
            " length array: " + str(len(blocked_urls_ublock)) + '\n' '\n'
            "Missed: " + str(total_missed_by_program) +
            " length array: " +
            str(len(missed)) + '\n' '\n' '\n')

    f.write('\n' '\n' "Missed URLs:" + '\n' '\n')

    for row in missed:
        f.write(row + '\n' '\n')

    d = open(os.path.join(dataset, "captured",
             folder, "blocked_ublock.txt"), "w+")

    for row in blocked_urls_ublock:
        d.write(row + '\n' '\n')

    h = open(os.path.join(dataset, "captured",
             folder, "blocked_program.txt"), "w+")

    for row in blocked_urls_program:
        h.write(row + '\n' '\n')


writeStatistic()
print("finsihed!")
