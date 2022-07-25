import json

domains = open("domains.lst", "r")
domains = domains.readlines()


#print(domains)
#array = []
#data = {
#  "domains": {
#    "proxies": [
#      {
#        "alias":"amazon_atv-ps-eu",
#        "domain":"atv-ps-eu.amazon.com",
#        "protocols": ["http", "https"],
#        "dnat": "false"
#      }
#    ]
#  }
#}



result = ('{\n')
result += ('  "domains": {\n')
result += ('    "proxies": [\n')
for domain in domains:
	domain = domain.strip()
        result += ('      {\n')
  	result += ('        "alias":"' + domain + '",\n')
	result += ('        "domain":"' + domain + '",\n')
	result += ('        "protocols": ["http", "https"],\n')
	result += ('        "dnat": true\n')
	result += ('      },\n')
result += ('      {\n')
result += ('        "alias":"placeholder.de",\n')
result += ('        "domain":"placeholder.de",\n')
result += ('        "protocols": ["http", "https"],\n')
result += ('        "dnat": true\n')
result += ('      }\n')

result += ('    ]\n')
result += ('  }\n')
result += ('}\n')






#result +=  ('"amazon": {')
#    "proxies": [
#      {
#        "alias":"amazon_atv-ps-eu",
#        "domain":"atv-ps-eu.amazon.com",
#        "protocols": ["http", "https"],
#        "dnat": true
#      },
#      {
#        "alias":"amazon_atv-ext-eu",
#        "domain":"atv-ext-eu.amazon.com",
#        "protocols": ["http", "https"],
#        "dnat": false
#      },
#      {
#        "alias":"amazon_atv-eu",
#        "domain":"atv-eu.amazon.com",
#        "protocols": ["http", "https"],
#        "dnat": true
 #     }
 #   ]
 # }
#}

#print (result)




#print(json_string)

# Directly from dictionary
#with open('json_data.json', 'w') as outfile:
#    json.dump(json_string, outfile)
# Using a JSON string
#with open('json_data.json', 'w') as outfile:
#    outfile.write(json_string)

#with open('proxies-us.json', 'w') as f:
#    json.dump(array, f, indent=2)
#    print("New json file is created from data.json file")



#newJson = json.dump(result,, indent=2, separators=(',', ': '))
#json.dump(json_data, result, separators=(',', ':'))
#with open('proxies-us.json', 'w') as json_file:
#	json_file.write(json_data)

#with open('proxies-us.json', 'w') as outfile:
#     json.dump(result, outfile, separators=(',', ':'))

#with open('proxies-us.json', 'w') as f:
#    f.write(result)


with open('proxies-us.json', 'w') as f:
    f.write(result)
    f.close()
