from __future__ import print_function
import json
import re
from adblockparser import AdblockRules
import os.path
import os


scripts = os.path.dirname(os.path.abspath(__file__))
dataset = os.path.dirname(scripts)
dependencies = os.path.join(dataset, 'dependencies')

folder = os.getenv('directory')


# define file path of the file you want to update
file = os.path.join(dataset, "captured", folder, "output.json")

easyprivacy = os.path.join(dependencies, 'easyprivacy.txt')

# specify file path of the easyprivacy txt file

with open(easyprivacy, 'rb') as f:
    raw_rules = f.read().decode('utf8').splitlines()


rules = AdblockRules(raw_rules)

options = {"script": True, "image": True,
           'third-party': True, "domain": "create-dataset.com"}


def extractURL():
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


def label_EasyPrivacy():
    with open(file, 'r+') as jsonFile:
        # Transforms json input to python objects
        data = json.load(jsonFile)

        # loop through packets
        for packet in data:
            packet["tracker"] = "false"

            # check for url entry
            if "http2.header.value.url" in packet:
                url = packet["http2.header.value.url"]

                if(rules.should_block(url, options)):
                    packet["tracker"] = "true"

        # rewind json so the file gets updated not appended
        jsonFile.seek(0)
        # write to file
        json.dump(data, jsonFile, indent=4)


extractURL()
label_EasyPrivacy()
