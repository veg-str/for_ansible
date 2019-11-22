import os, openpyxl, yaml

ip_plan_dir = 'c:\\Users\\ve.gusarin\\Seafile\\Tele2-2018-TMS\\07. Design\\'
ip_plan = 'Tele2_IP_plan_v032.xlsx'
wb = openpyxl.load_workbook(ip_plan_dir + ip_plan, True)
inventory_dir = 'c:\\temp\\inventory\\'
vars_file = 'networks.yml'

mr = ['spb', 'mos', 'ros', 'nin', 'ekt', 'nsk']
vlans = ['Gx', 'Gy', 'Radius', 'RadiusFE', 'Resource', 'Provisioning', 'ClusterSync', 'OOB_Mgmt', 'Host_Mgmt', 'vm_Mgmt', 'DataFeed']
subnets = {'networks': ''}
reg = []

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
#                    subnet = {'name': row[0].value, 'subnet': row[5].value, 'prefix': row[3].value, 'gw': row[6].value}
#                    site.append(subnet)
            reg_dict = {region + str(i): site}
        else:
            site = {}
            for row in ws[rng]:
                if row[0].value in vlans:
                    site[row[0].value] = {'subnet': row[8].value, 'prefix': row[3].value, 'gw': row[9].value}
#                    subnet = {'name': row[0].value, 'subnet': row[8].value, 'prefix': row[3].value, 'gw': row[9].value}
#                    site.append(subnet)
            reg_dict = {region + str(i): site}
        reg.append(reg_dict)
    print(reg)
subnets['networks'] = reg
print(subnets)


with open(inventory_dir + vars_file, 'w') as f:
    f.write(yaml.dump(subnets))
#print(yaml.dump(subnets))