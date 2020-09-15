import re

from pprint import pprint



'''
# Get list of MSISDNs from file
msisdns = []
with open('d:/temp/msisdn_list_full', 'r') as f:
    for line in f:
        if re.search("\d{11}", line):
            msisdns.append(re.search("\d{11}", line).group(0))

# Split list into small parts (500 MSISND per list)
msisdn_full = []
while len(msisdns) != 0:
    tmp_list = []
    i = 0
    while i < 500 and len(msisdns) > 0:
        tmp_list.append(msisdns.pop(0))
        i = i + 1
    msisdn_full.append(tmp_list)

print(len(msisdn_full))
'''