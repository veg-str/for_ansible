import openpyxl, yaml

ip_plan = 'project_files\\Tele2_IP_plan_v036.xlsx'
vars_file = 'c:\\temp\\group_vars\\networks.yml'

wb = openpyxl.load_workbook(ip_plan, True)

mr = ['spb', 'mos', 'ros', 'nin', 'ekt', 'nsk']
vlans = ['Gx', 'Gy', 'Radius', 'RadiusFE', 'Resource', 'Provisioning', 'ClusterSync', 'OOB_Mgmt', 'Host_Mgmt', 'vm_Mgmt', 'DataFeed']
reg = {}
subnets = {}

with open(vars_file, 'w', newline='\n') as f:
    for region in mr:
        for i in (1, 2):
            print('# Subnets in region ' + region.upper() + ', Site' + str(i))
            net = wb.defined_names[region + '_nets'].attr_text
            ws = wb[str(net[1:net.find('!')-1])]
            rng = net[net.find('!')+1:]
            if i == 1:
                site = {}
                for row in ws[rng]:
                    if row[0].value in vlans:
                        site[row[0].value] = {'subnet': row[5].value, 'prefix': row[3].value, 'gw': row[6].value}
                reg[region + str(i)] = site
            else:
                site = {}
                for row in ws[rng]:
                    if row[0].value in vlans:
                        site[row[0].value] = {'subnet': row[8].value, 'prefix': row[3].value, 'gw': row[9].value}
                reg[region + str(i)] = site
    subnets['network'] = reg
    f.write(yaml.dump(subnets))
    print('Done')
