import openpyxl, re

ip_plan = 'project_files\\Tele2_IP_plan_v2.01.xlsx'
inventory_file = 'c:\\temp\\inventory\\packetlogick'

mr = ['EKT']
#mr = ['SPB', 'MOS', 'ROS', 'NIN', 'EKT', 'NSK']
base_srv_types = ['pre', 'psm', 'pic', 'apic']
ext_srv_types = ['epsm', 'rb', 'log', 'rs']

wb = openpyxl.load_workbook(ip_plan, True)


def site_groups(region, site):
    members = []
    for srv_type in base_srv_types:
        members.append('pl_' + region.lower() + site + '_' + srv_type)
    groups = {'name': '[pl_' + region.lower() + site + ':children]', 'members': members}
    return groups


def mr_groups(region, srv_type):
    members = []
    for i in ['1', '2']:
        members.append('pl_' + region.lower() + i + '_' + srv_type)
    group = {'name':'[pl_' + region.lower() + '_' + srv_type + ':children]', 'members': members}
    return group


def global_group(srv_type):
    members = []
    for region in mr:
        members.append('pl_' + region.lower() + '_' + srv_type)
    group = {'name': '[pl_' + srv_type + ':children]', 'members': members}
    return group


def pre_prov_ip(srv):
    prov_ip = ''
    for row in srv_list:
        if row['hostname'] == srv and row['vlan'] == 'Provisioning':
            prov_ip = row['ip']
    return prov_ip


def pic_dadafeed_ip(srv):
    df_ip = ''
    for row in srv_list:
        if row['hostname'] == srv and row['vlan'] == 'DataFeed':
            df_ip = row['ip']
    return df_ip


def rows_to_dict(region):
    kvm_list = []
    ws = wb[region]
    for row in ws.iter_rows():
        if str(row[1].value)[:-20] in base_srv_types:
            kvm_list.append({'hostname': row[1].value, 'vlan': row[3].value, 'ip': row[5].value, 'site': row[6].value})
    return kvm_list


with open(inventory_file, 'w', newline='\n') as f:
    f.write('# List of PacketLogic VMs\n\n')
    for region in mr:
        srv_list = rows_to_dict(region)
        print('Collecting data about VM in ' + region)
        f.write('# ' + region + '\n')
        for i in ['1','2']:
            for srv_type in base_srv_types:
                f.write('[pl_' + region.lower() + i + '_' + srv_type + ']\n')
                for row in srv_list:
                    if row['vlan'] == 'vm_Mgmt' and row['site'][-1] == i and re.search("^" + srv_type, row['hostname']):
                        f.write(row['hostname'][:-13] + ' ansible_host=' + row['ip']) # + '\n')
                        if srv_type == 'pre':
                            f.write(' provisioning_ip=' + pre_prov_ip(row['hostname']) + '\n')
                        elif srv_type in ['pic', 'apic']:
                            f.write(' datafeed_ip=' + pic_dadafeed_ip(row['hostname']) + '\n')
                        else:
                            f.write('\n')
                f.write('\n')
            group = site_groups(region, i)
            f.write(group['name'] + '\n')
            for member in group['members']:
                f.write(member + '\n')
            f.write('\n')
        for srv_type in base_srv_types:
            group = mr_groups(region, srv_type)
            f.write(group['name'] + '\n')
            for member in group['members']:
                f.write(member + '\n')
            f.write('\n')
    f.write('\n# Global groups\n\n')
    for srv_type in base_srv_types:
        group = global_group(srv_type)
        f.write(group['name'] + '\n')
        for member in group['members']:
            f.write(member + '\n')
        f.write('\n')
    print('Done')