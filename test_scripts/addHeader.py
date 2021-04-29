import json


file = "/Users/bene/Desktop/dataset/captured/Google_test/create-dataset.com:google_tracker_labeled.json"


def addHeader():
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
                        header = packet['_source']['layers']['http2']['http2.stream']['http2.header']

                        entry = {"http2.header.value.total": ""}
                        header.insert(0, entry)

                        # loop through the http2.header array
                        for header in packet['_source']['layers']['http2']['http2.stream']['http2.header']:
                            if 'http2.header.value' in header:
                                packet['_source']['layers']['http2']['http2.stream']['http2.header'][0]["http2.header.value.total"] = packet['_source'][
                                    'layers']['http2']['http2.stream']['http2.header'][0]["http2.header.value.total"] + header['http2.header.value']

        # rewind json so the file gets updated not appended
        jsonFile.seek(0)
        # write to file
        json.dump(data, jsonFile, indent=4)

# extract URL from http2.header.value


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
                                packet["http2.header.value.url"] = header[2]["http2.header.value"] + \
                                    "://" + header[1]['http2.header.value'] + \
                                    header[3]['http2.header.value']

        # rewind json so the file gets updated not appended
        jsonFile.seek(0)
        # write to file
        json.dump(data, jsonFile, indent=4)


# addHeader()
extractURL()
