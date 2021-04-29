from urllib.parse import urlparse
from adblockparser import AdblockRules
import json
import pprint


# relative path to the uBlock log
ublock_log_file = "/Users/bene/Desktop/dataset/captured/bild.de/uBlockLog.txt"


# extracts url from uBlockLog.txt and writes urls to blocked_URLs_uBlock.txt

def extract_urls_with_options():
    with open(ublock_log_file, "r") as log:
        content = log.read().splitlines()

    ublock_log_list = []

    index_list = []

    # get indexes of blocked signs "--" in uBlockLog.txt -> indicates blocked element
    for i, j in enumerate(content):
        if j == "--":
            index_list.append(i)

    for index in index_list:

        # strip url https://example.com/home?width=10 to example.com
        stripped_url = urlparse(content[index+4]).netloc

        # get option parameter for adblockparser from each blocked element
        domain = content[index+1]
        temp = content[index+3]
        third_party = ""

        if temp == "xhr":
            temp = "xmlhttprequest"
        if content[index+2] == "3":
            third_party = True
        elif content[index+2] == "1":
            third_party = False
        elif content[index+2] == "3,1":
            third_party = True

        # build log dict with options
        obj = {
            "stripped_url": stripped_url,
            "options": {
                "domain": domain,
                "third-party": third_party,
                temp: True
            }

        }
        # push it to the ublock_log list
        ublock_log_list.append(obj)

    return ublock_log_list


ublock_log_list = extract_urls_with_options()


output = "/Users/bene/Desktop/dataset/captured/bild.de/output.json"


def label():
    # use easyprivacy to check rules contained by that list against urls
    with open("/Users/bene/Desktop/dataset/dependencies/easyprivacy.txt", "rb") as f:
        raw_rules = f.read().decode("utf8").splitlines()

    rules = AdblockRules(raw_rules)
    options = {}

    #  open json file
    with open(output, "r+") as json_file:
        # Transforms json input to python objects
        data = json.load(json_file)

        #  loop through packets
        for packet in data:

            packet["tracker"] = "false"
            layers = packet["_source"]["layers"]

            # check for every stripped url in http2.header.value.url
            if "http2.header.value.url" in packet:
                # loop through new created ublock_log_list
                for blocked_element in ublock_log_list:

                    # check if stripped_url is in http2.header.value.url
                    if blocked_element["stripped_url"] in packet["http2.header.value.url"]:

                        # set options according to blocked_element in ublock_log_list
                        options = blocked_element["options"]

                        # check if url in http2.header.value.url should be blocked according to adblockparser
                        if(rules.should_block(packet["http2.header.value.url"], options)):
                            packet["tracker"] = "true"

            # check for every stripped url in http.request.full_uri
            if "http" in layers:
                http = packet["_source"]["layers"]["http"]

                if "http.request.full_uri" in http:
                    http_request_full_uri = packet["_source"]["layers"]["http"]["http.request.full_uri"]

                    # loop through new created ublock_log_list
                    for blocked_element in ublock_log_list:
                        # check if stripped_url is in http_request_full_uri
                        if blocked_element["stripped_url"] in http_request_full_uri:
                            # set options according to blocked_element in ublock_log_list
                            options = blocked_element["options"]

                            # check if url in http_request.full_uri should be blocked according to adblockparser
                            if(rules.should_block(http_request_full_uri, options)):
                                packet["tracker"] = "true"

                # CHECK RESPONSE URI AND DATA_FILE?
                # elif "http.response_for.uri" in http:
                #     http_response_for_uri = packet["_source"]["layers"]["http"]["http.response_for.uri"]

                #     for url in stripped_urls:
                #         if url in http_response_for_uri:

                #             packet["tracker"] = "true"

                # elif "http.file_data" in http:
                #     http_file_data = packet["_source"]["layers"]["http"]["http.file_data"]

                #     for url in stripped_urls:
                #         if url in http_file_data:

                #             packet["tracker"] = "true"

        json_file.seek(0)
        # write to file
        json.dump(data, json_file, indent=4)


label()


# NOT USED METHODS


# def delete_video_content():
#     with open(output, "r+") as json_file:
#         # Transforms json input to python objects
#         data = json.load(json_file)

#         for packet in data:
#             layers = packet["_source"]["layers"]

#             # delete video content
#             if "mp2t" in layers:
#                 layers.pop("mp2t", None)

#         json_file.seek(0)
#         # write to file
#         json.dump(data, json_file, indent=4)


# def extractUrlUblock():
#     with open(ublock_log_file, "r") as log:
#         content = log.read().splitlines()

#     total_blocked_urls_ublock = 0
#     blocked_urls_ublock = []

#     # get index of the blocked signs "--" -> Url is always 4 entrys after "--"
#     index_list = []
#     for i, j in enumerate(content):
#         if j == "--":
#             index_list.append(i)

#     for index in index_list:
#         blocked_urls_ublock.append(content[index+4])
#         total_blocked_urls_ublock += 1

#     return total_blocked_urls_ublock, blocked_urls_ublock


# strip url https://example.com/home?width=10 to example.com
# def strip_url():
#     stripped_urls = []

#     for url in blocked_urls_ublock:
#         # strip url
#         parsed = urlparse(url)
#         stripped_urls.append(parsed.netloc)
#     return stripped_urls
