import openpyxl, re

ip_plan = 'project_files\\Tele2_IP_plan_v040.xlsx'
inventory_file = 'c:\\temp\\inventory\\kvm'

mr = ['SPB', 'MOS', 'ROS', 'NIN', 'EKT', 'NSK']
base_srv_types = ['pre', 'psm', 'pic']
ext_srv_types = ['epsm', 'rb', 'log', 'rs']

wb = openpyxl.load_workbook(ip_plan, True)


def site_groups(region, site):
    members = []
    for srv_type in base_srv_types:
        members.append('kvm_' + region.lower() + site + '_' + srv_type)
    groups = {'name': '[kvm_' + region.lower() + site + ':children]', 'members': members}
    return groups


def mr_groups(region, srv_type):
    members = []
    for i in ['1', '2']:
        members.append('kvm_' + region.lower() + i + '_' + srv_type)
    group = {'name':'[kvm_' + region.lower() + '_' + srv_type + ':children]', 'members': members}
    return group


def global_group(srv_type):
    members = []
    for region in mr:
        members.append('kvm_' + region.lower() + '_' + srv_type)
    group = {'name': '[' + srv_type + ':children]', 'members': members}
    return group


def vm_names(srv):
    vm_name = []
    for row in srv_list:
        if row['hostname'] == srv and row['vlan'] == 'vm_Mgmt':
            vm_name.append(row['vm'][:-18])
    return vm_name


def rows_to_dict(region):
    kvm_list = []
    ws = wb[region]
    for row in ws.iter_rows():
        kvm_list.append({'hostname': row[0].value, 'vm': row[1].value,
                         'vlan': row[3].value, 'ip': row[5].value, 'site': row[6].value})
    return kvm_list


with open(inventory_file, 'w', newline='\n') as f:
    f.write('# List of KVMs\n\n')
    for region in mr:
        srv_list = rows_to_dict(region)
        print('Collecting data about KVM in ' + region)
        f.write('# ' + region + '\n')
        for i in ['1','2']:
            for srv_type in base_srv_types:
                f.write('[kvm_' + region.lower() + i + '_' + srv_type + ']\n')
                for row in srv_list:
                    vm = vm_names(row['hostname'])
                    if row['vlan'] == 'Host_Mgmt' and row['site'][-1] == i and re.search("^" + srv_type, vm[0]):
                        f.write(row['hostname'][:-13] + ' ansible_host=' + row['ip'] +
                                ' vm_name=' + vm[0] + ' vm_list="' + str(vm) + '"\n')
                f.write('\n')
            for srv_type in ext_srv_types:
                f.write('[kvm_' + region.lower() + i + '_' + srv_type + ']\n')
                for row in srv_list:
                    vm = vm_names(row['hostname'])
                    if row['vlan'] == 'Host_Mgmt' and row['site'][-1] == i and str(vm).find(srv_type) != -1:
                        f.write(row['hostname'][:-13] + '\n')
                f.write('\n')
            group = site_groups(region, i)
            f.write(group['name'] + '\n')
            for member in group['members']:
                f.write(member + '\n')
            f.write('\n')
        for srv_type in ext_srv_types:
            group = mr_groups(region, srv_type)
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
    for srv_type in ext_srv_types:
        group = global_group(srv_type)
        f.write(group['name'] + '\n')
        for member in group['members']:
            f.write(member + '\n')
        f.write('\n')
    for srv_type in base_srv_types:
        group = global_group(srv_type)
        f.write(group['name'] + '\n')
        for member in group['members']:
            f.write(member + '\n')
        f.write('\n')
    print('Done')
