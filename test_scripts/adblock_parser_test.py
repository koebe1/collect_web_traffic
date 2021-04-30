from urllib.parse import urlparse
from adblockparser import AdblockRules
import json
import re

# relative path to the uBlock log
ublock_log_file = "/Users/bene/Desktop/dataset/captured/top5/uBlockLog.txt"


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

        rule = content[index-1]

        # get option parameter for adblockparser from each blocked element
        domain = ""
        third_party = False
        stylesheet = False
        xmlhttprequest = False
        image = False
        script = False
        ping = False

        # uBlock uses some custom rules -> check for custom rules and change them to adblock format
        if '3p' in rule:
            rule = rule.replace("3p", "third-party")
            third_party = True

        if "image" in rule:
            image = True

        if "script" in rule:
            script = True

        if "ping" in rule:
            ping = True

        if "xmlhttprequest" in rule:
            xmlhttprequest = True

        if "stylesheet" in rule:
            stylesheet = True

        if "domain=" in rule:

            if "domain=~" not in rule:
                # extract domain content
                domain = rule.partition("domain=")[2]
                if "," in domain:
                    domain = domain.partition(",")[0]

        # build log dict with options
        obj = {
            "stripped_url": stripped_url,
            "rule": rule,
            "options": {
                "domain": domain,
                "third-party": third_party,
                "image": image,
                "script": script,
                "xmlhttprequest": xmlhttprequest,
                "stylesheet": stylesheet,
                "ping": ping
            }
        }

        # check options -> if False delete options || .copy() to dont change the iterated object while iterating
        for option in obj["options"].copy():
            if not obj["options"][option]:
                del obj["options"][option]

        # push it to the ublock_log list
        ublock_log_list.append(obj)

    return ublock_log_list


ublock_log_list = extract_urls_with_options()


output = "/Users/bene/Desktop/dataset/captured/top5/output.json"


def label():
    # # use easyprivacy to check rules contained by that list against urls
    # with open("/Users/bene/Desktop/dataset/dependencies/easyprivacy.txt", "rb") as f:
    #     raw_rules = f.read().decode("utf8").splitlines()
    #
    raw_rules = []

    # use rules from uBlockLog for big performance upgrade -> used rules should be exactly the same
    for entry in ublock_log_list:
        raw_rules.append(entry["rule"])

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

                # # CHECK RESPONSE URI AND DATA_FILE?
                # elif "http.response_for.uri" in http:
                #     http_response_for_uri = packet["_source"]["layers"]["http"]["http.response_for.uri"]

                #     # loop through new created ublock_log_list
                #     for blocked_element in ublock_log_list:
                #         # check if stripped_url is in http_response_for_uri
                #         if blocked_element["stripped_url"] in http_response_for_uri:

                #            # set options according to blocked_element in ublock_log_list
                #             options = blocked_element["options"]

                #             # check if url in http_request.full_uri should be blocked according to adblockparser
                #             if(rules.should_block(http_response_for_uri, options)):
                #                 packet["tracker"] = "true"

                # elif "http.file_data" in http:
                #     http_file_data = packet["_source"]["layers"]["http"]["http.file_data"]

                #     for blocked_element in ublock_log_list:
                #         # check if stripped_url is in http_response_for_uri
                #         if blocked_element["stripped_url"] in http_file_data:

                #             # set options according to blocked_element in ublock_log_list
                #             options = blocked_element["options"]

                #             # check if url in http_request.full_uri should be blocked according to adblockparser

                #             # NEED TO EXTRACT URL FROM http_file_data FIRST
                #             if(rules.should_block(HTTP-FILE-DATA, options)):
                #                 packet["tracker"] = "true"

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


# delete_video_content()


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
