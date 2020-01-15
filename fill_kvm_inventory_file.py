import os, openpyxl, ipaddr, yaml

ip_plan_dir = 'c:\\Users\\ve.gusarin\\Seafile\\Tele2-2018-TMS\\07. Design\\'
ip_plan = 'Tele2_IP_plan_v035.xlsx'
inventory_dir = 'c:\\temp\\inventory\\'
# inventory_file = 't2_tms_inventory'
mr = ['SPB', 'MOS', 'ROS', 'NIN', 'EKT', 'NSK']
kvm_keys = ['hostname', 'ansible_host', 'vm_name']
srv_types = ['pre', 'psm', 'pic', 'epsm', 'rb', 'log']
epsm_host = 'kvm10.'

os.chdir(inventory_dir)

# Open Excel file in read-only mode
wb = openpyxl.load_workbook(ip_plan_dir + ip_plan, True)

print(wb.sheetnames)


def vm_names(region, srv):
    ws = wb[region]
    vm_name = ''
    excluded_vm_names = ['epsm', 'log', 'rb', 'rs']
    for row in ws.iter_rows():
        if srv == row[0].value and str(row[1].value)[:-20] not in excluded_vm_names and row[3].value == 'vm-Mgmt':
#        if srv == row[0].value and 'epsm' not in str(row[1].value) and 'log' not in str(row[1].value) and row[3].value == 'vm-Mgmt':
#        if srv == row[0].value and ('pre' or 'psm' or 'pic') in str(row[1].value) and row[3].value == 'vm-Mgmt':
            vm_name = str(row[1].value)[:-18]
    return vm_name


def kvm_list(region, site):
    ws = wb[region]
    srv_list = []
    for row in ws.iter_rows():
        if row[3].value == 'Host-Mgmt' and row[6].value == site:
            srv_list.append(
                {kvm_keys[0]: row[0].value, kvm_keys[1]: row[5].value, kvm_keys[2]: vm_names(region, row[0].value)})
    return srv_list


def pre_list(srv_list):
    pre_list = []
    for srv in srv_list:
        if 'pre' in srv[kvm_keys[2]]:
            pre_list.append(srv)
    return pre_list


def psm_list(srv_list):
    psm_list = []
    for srv in srv_list:
        if 'psm' in srv[kvm_keys[2]]:
            psm_list.append(srv)
    return psm_list


def pic_list(srv_list):
    pic_list = []
    for srv in srv_list:
        if 'pic' in srv[kvm_keys[2]]:
            pic_list.append(srv)
    return pic_list


def epsm_list(region, site):
    ws = wb[region]
    srv_list = []
    for row in ws.iter_rows():
        if row[3].value == 'vm-Mgmt' and 'epsm' in row[1].value and row[6].value == site:
            srv_list.append({str(row[1].value)[:-18]: row[5].value})
    return srv_list


def rb_list(region, site):
    ws = wb[region]
    srv_list = []
    for row in ws.iter_rows():
        if row[3].value == 'vm-Mgmt' and 'rb' in row[1].value and row[6].value == site:
            srv_list.append({str(row[1].value)[:-18]: row[5].value})
    return srv_list


#def kvm_bottom_groups(region):



def kvm_groups(region):
    groups = []
    groups.append({'name': '[kvm_' + region.lower() + '1:children]',
                   'members': ['kvm_' + region.lower() + '1_pre', 'kvm_' + region.lower() + '1_pic',
                               'kvm_' + region.lower() + '1_psm']})
    groups.append({'name': '[kvm_' + region.lower() + '2:children]',
                   'members': ['kvm_' + region.lower() + '2_pre', 'kvm_' + region.lower() + '2_pic',
                               'kvm_' + region.lower() + '2_psm']})
    groups.append({'name': '[kvm_' + region.lower() + '_pre:children]',
                   'members': ['kvm_' + region.lower() + '1_pre', 'kvm_' + region.lower() + '2_pre']})
    groups.append({'name': '[kvm_' + region.lower() + '_pic:children]',
                   'members': ['kvm_' + region.lower() + '1_pic', 'kvm_' + region.lower() + '2_pic']})
    groups.append({'name': '[kvm_' + region.lower() + '_psm:children]',
                   'members': ['kvm_' + region.lower() + '1_psm', 'kvm_' + region.lower() + '2_psm']})
    groups.append({'name': '[kvm_' + region.lower() + '_epsm:children]',
                   'members': ['kvm_' + region.lower() + '1_epsm', 'kvm_' + region.lower() + '2_epsm']})
    groups.append({'name': '[kvm_' + region.lower() + '_rb:children]',
                   'members': ['kvm_' + region.lower() + '1_rb', 'kvm_' + region.lower() + '2_rb']})
    groups.append({'name': '[kvm_' + region.lower() + ':children]',
                   'members': ['kvm_' + region.lower() + '1', 'kvm_' + region.lower() + '2']})
    return groups


def global_groups():
    global_gr = []
    pre = []
    pic = []
    psm = []
    epsm = []
    rb = []
    for region in mr:
        pre.append('kvm_' + region.lower() + '_pre')
        pic.append('kvm_' + region.lower() + '_pic')
        psm.append('kvm_' + region.lower() + '_psm')
        epsm.append('kvm_' + region.lower() + '_epsm')
        rb.append('kvm_' + region.lower() + '_rb')
#        log.append('kvm_' + region.lower() + '_log')
    global_gr.append({'name': '[pre:children]', 'members': pre})
    global_gr.append({'name': '[pic:children]', 'members': pic})
    global_gr.append({'name': '[psm:children]', 'members': psm})
    global_gr.append({'name': '[epsm:children]', 'members': epsm})
    global_gr.append({'name': '[rb:children]', 'members': rb})
#    global_gr.append({'name': '[log:children]', 'members': log})
    return global_gr

# Create file with KVMs
inventory_file = 'kvm'
with open(inventory_file, 'w', newline='\n') as f:
    f.write('# List os KVMs\n\n')
    for item in mr:
        print('Collecting data about KVM in ' + item)
        site = kvm_list(item, 'Site1')
        f.write('# ' + item + '\n')
        f.write('[kvm_' + item.lower() + '1_pre]\n')
        for kvm in pre_list(site):
            f.write(kvm[kvm_keys[0]][:-13] + ' ansible_host=' + kvm[kvm_keys[1]] + ' vm_name=' + kvm[kvm_keys[2]] + '\n')
        f.write('\n')
        f.write('[kvm_' + item.lower() + '1_pic]\n')
        for kvm in pic_list(site):
            f.write(kvm[kvm_keys[0]][:-13] + ' ansible_host=' + kvm[kvm_keys[1]] + ' vm_name=' + kvm[kvm_keys[2]] + '\n')
        f.write('\n')
        f.write('[kvm_' + item.lower() + '1_psm]\n')
        for kvm in psm_list(site):
            f.write(kvm[kvm_keys[0]][:-13] + ' ansible_host=' + kvm[kvm_keys[1]] + '\n')
        f.write('\n')
        f.write('[kvm_' + item.lower() + '1_rb]\n')
#        for kvm in rb_list(item, 'Site1'):
#            f.write(kvm[kvm_keys[0]][:-13] + '\n')
        f.write('\n')
        f.write('[kvm_' + item.lower() + '1_epsm]\n')
        f.write(epsm_host + item.lower() + '1\n\n')
        site = kvm_list(item, 'Site2')
        f.write('[kvm_' + item.lower() + '2_pre]\n')
        for kvm in pre_list(site):
            f.write(kvm[kvm_keys[0]][:-13] + ' ansible_host=' + kvm[kvm_keys[1]] + ' vm_name=' + kvm[kvm_keys[2]] + '\n')
        f.write('\n')
        f.write('[kvm_' + item.lower() + '2_pic]\n')
        for kvm in pic_list(site):
            f.write(kvm[kvm_keys[0]][:-13] + ' ansible_host=' + kvm[kvm_keys[1]] + ' vm_name=' + kvm[kvm_keys[2]] + '\n')
        f.write('\n')
        f.write('[kvm_' + item.lower() + '2_psm]\n')
        for kvm in psm_list(site):
            f.write(kvm[kvm_keys[0]][:-13] + ' ansible_host=' + kvm[kvm_keys[1]] + '\n')
        f.write('\n')
        f.write('[kvm_' + item.lower() + '2_rb]\n')
#        for kvm in rb_list(item, 'Site2'):
#            f.write(kvm[kvm_keys[0]][:-18] + '\n')
        f.write('\n')
        f.write('[kvm_' + item.lower() + '2_epsm]\n')
        f.write(epsm_host + item.lower() + '2\n\n')
        print('Creating regional groups for ' + item)
        for group in kvm_groups(item):
            f.write(group['name'] + '\n')
            for member in group['members']:
                f.write(member + '\n')
            f.write('\n')
    print('Creating global groups')
    f.write('# Global groups\n')
    for group in global_groups():
        f.write(group['name'] + '\n')
        for member in group['members']:
            f.write(member + '\n')
        f.write('\n')
