from __future__ import print_function
import json


# define file path of the file you want to update
file = '/Users/bene/Desktop/dataset/captured/Google/output.json'
# define the content blocked by uBlock --> speciefies which strings to search for in http2.header.value
blockedContent = ["gtag/js", '/gen_204?', '/osd.js', 'googleadservices.com']

# specify folder you want to save the filtered json file
folder = '/Users/bene/Desktop/dataset/captured/create-dataset.com/'


# adds "tracker": "true" to packet with specified string (blocked) and overwrites the specified json
def label():
    with open(file, 'r+') as jsonFile:
        # Transforms json input to python objects
        data = json.load(jsonFile)

        # loop through packets
        for packet in data:
            packet["tracker"] = "false"
            # if http2 layer exists keep looking deeper in the packet
            if "http2" in packet['_source']['layers']:
                if "http2.stream" in packet['_source']['layers']['http2']:
                    if "http2.header" in packet['_source']['layers']['http2']['http2.stream']:
                        # loop through the http2.header array
                        for http2header in packet['_source']['layers']['http2']['http2.stream']['http2.header']:
                            # if array item is found in http2.header.value the label {"tracker" : "true"} gets added
                            for item in blockedContent:
                                if item in http2header["http2.header.value"]:
                                    packet["tracker"] = "true"

        # rewind json so the file gets updated not appended
        jsonFile.seek(0)
        # write to file
        json.dump(data, jsonFile, indent=4)


label()

# creates a new filtered json file in the specified folder. Json shows 'frame.nr', 'tracker', 'ip','tcp','udp'


def filter():
    with open(file, 'r+') as jsonFile:
        # Transforms json input to python dict
        data = json.load(jsonFile)

    filtered_list = []

    for packet in data:
        if('tcp' in packet['_source']['layers']):
            filtered_list.append({'frame.number': packet['_source']['layers']['frame']['frame.number'],
                                  'tracker': packet['tracker'],
                                  'ip': packet['_source']['layers']['ip'],
                                  'tcp': packet['_source']['layers']['tcp']})

        elif('udp' in packet['_source']['layers']):
            filtered_list.append({'frame.number': packet['_source']['layers']['frame']['frame.number'],
                                  'tracker': packet['tracker'],
                                  'ip': packet['_source']['layers']['ip'],
                                  'udp': packet['_source']['layers']['udp']})

        elif('ip' in packet['_source']['layers']):
            filtered_list.append({'frame.number': packet['_source']['layers']['frame']['frame.number'],
                                  'tracker': packet['tracker'],
                                  'ip': packet['_source']['layers']['ip']})

        else:
            filtered_list.append({'frame.number': packet['_source']['layers']['frame']['frame.number'],
                                  'tracker': packet['tracker']})

    with open(folder + 'filtered.json', 'w') as jsonFile:
        json.dump(filtered_list, jsonFile, indent=4)


# filter()
print("finished")
