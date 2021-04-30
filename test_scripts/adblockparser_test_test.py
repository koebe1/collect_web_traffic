from adblockparser import AdblockRules

raw_rules = ['||googletagservices.com^*/osd.js$3p']

rules = AdblockRules(raw_rules)
options = {"script": True, "third-party": True,
           "domain": "googletagservices.com"}

if(rules.should_block("https://www.googletagservices.com/activeview/js/current/osd.js?cb=%2Fr20100101", options)):
    print(True)
else:
    print(False)
