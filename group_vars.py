import openpyxl, yaml, re, ipaddress
from pprint import pprint

sig_int = 'project_files\\Tele2_TMS_Signal_integration_v3.4.xlsx'
vars_dir = 'c:\\temp\\group_vars\\'

# Open Excel file in read-only mode
wb = openpyxl.load_workbook(sig_int, True)

#mr = ['nin']
#mr = ['spb', 'nin', 'ekt', 'nsk', 'ros', 'mos']
mr = ['nin', 'ekt', 'nsk']


def get_sig_nets():
    signals = ['radius', 'gx', 'gy']
    sig_nets = {}
    for region in mr:
        sig_nets[region] = {}
        for i in 1,2:
            sig_nets[region][i] = {}
            for item in signals:
                dn = wb.defined_names[region + '_s' + str(i) + '_' + item].attr_text
                ws = wb[str(dn[0:dn.find('!')])]
                rng = dn[dn.find('!') + 1:]
                nets = []
                for row in ws[rng]:
                    if row[15].value != None:
                        nets.append(row[15].value.strip())
                sig_nets[region][i][item] = nets
    return sig_nets


def summarise_nets(range): # Summarise addresses into /24 subnets
    supernets = set()
    for ip in range:
        supernets.add(str(ipaddress.IPv4Network(ip).supernet(new_prefix=24)))
    supernets = list(set(supernets))
    return supernets


#with open(vars_dir + 'pre_static_routes.yml', 'w', newline='\n') as file:
#                documents = yaml.dump(get_pre_routes(), file)
#for region in mr:
#    print(get_pre_routes())
signal_networks = get_sig_nets()
for region in mr:
    for site in 1,2:
        keys = list(signal_networks[region][site].keys())
        for key in keys:
            nets = summarise_nets(signal_networks[region][site][key])
            signal_networks[region][site][key] = nets

for region in mr:
    with open(vars_dir + region + '_psm_static_routes.yml', 'w', newline='\n') as file:
        yaml.dump(signal_networks[region], file)