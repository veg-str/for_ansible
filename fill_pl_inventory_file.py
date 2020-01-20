import os, openpyxl

ip_plan_dir = 'c:\\Users\\ve.gusarin\\Seafile\\Tele2-2018-TMS\\07. Design\\'
ip_plan = 'Tele2_IP_plan_v036.xlsx'
inventory_dir = 'c:\\temp\\inventory\\'

mr = ['SPB', 'MOS', 'ROS', 'NIN', 'EKT', 'NSK']
pl_keys = ['hostname', 'ansible_host', 'prov_ip']

os.chdir(inventory_dir)

# Open Excel file in read-only mode
wb = openpyxl.load_workbook(ip_plan_dir + ip_plan, True)


def pl_list(region, site):
    ws = wb[region]
    srv_list = []
    for row in ws.iter_rows():
        if row[3].value == 'vm-Mgmt' and row[6].value == site:
            srv_list.append({pl_keys[0]: row[1].value, pl_keys[1]: row[5].value})
    for srv in srv_list:
        for row in ws.iter_rows():
            if row[1].value == srv[pl_keys[0]] and row[3].value != 'vm-Mgmt':
                srv[row[3].value] = row[5].value
    return srv_list


def pre_list(srv_list):
    pre = []
    for srv in srv_list:
        if 'pre' in srv[pl_keys[0]]:
            pre.append(srv)
    return pre


def pic_list(srv_list):
    pic = []
    for srv in srv_list:
        if 'pic' in srv[pl_keys[0]]:
            pic.append(srv)
    return pic


def psm_list(srv_list):
    psm = []
    for srv in srv_list:
        if 'psm' in srv[pl_keys[0]] and 'epsm' not in srv[pl_keys[0]]:
            psm.append(srv)
    return psm


def pl_groups(region):
    groups = []
    groups.append({'name': '[pl_' + region.lower() + '1:children]',
                   'members': ['pl_' + region.lower() + '1_pre', 'pl_' + region.lower() + '1_pic',
                               'pl_' + region.lower() + '1_psm']})
    groups.append({'name': '[pl_' + region.lower() + '2:children]',
                   'members': ['pl_' + region.lower() + '2_pre', 'pl_' + region.lower() + '2_pic',
                               'pl_' + region.lower() + '2_psm']})
    groups.append({'name': '[pl_' + region.lower() + '_pre:children]',
                   'members': ['pl_' + region.lower() + '1_pre', 'pl_' + region.lower() + '2_pre']})
    groups.append({'name': '[pl_' + region.lower() + '_pic:children]',
                   'members': ['pl_' + region.lower() + '1_pic', 'pl_' + region.lower() + '2_pic']})
    groups.append({'name': '[pl_' + region.lower() + '_psm:children]',
                   'members': ['pl_' + region.lower() + '1_psm', 'pl_' + region.lower() + '2_psm']})
    groups.append({'name': '[pl_' + region.lower() + ':children]',
                   'members': ['pl_' + region.lower() + '1', 'pl_' + region.lower() + '2']})
    return groups


def global_groups():
    global_gr = []
    pre = []
    pic = []
    psm = []
    for region in mr:
        pre.append('pl_' + region.lower() + '_pre')
        pic.append('pl_' + region.lower() + '_pic')
        psm.append('pl_' + region.lower() + '_psm')
    global_gr.append({'name': '[pl_pre:children]', 'members': pre})
    global_gr.append({'name': '[pl_pic:children]', 'members': pic})
    global_gr.append({'name': '[pl_psm:children]', 'members': psm})
    return global_gr


# Create file with PacketLogic VMs
inventory_file = 'packetlogick'
with open(inventory_file, 'w', newline='\n') as f:
    f.write('# List os PacketLogic VMs\n\n')
    for item in mr:
        print('Collecting data about VM in ' + item)
        site = pl_list(item, 'Site1')
        f.write('# ' + item + '\n')
        f.write('[pl_' + item.lower() + '1_pre]\n')
        for vm in pre_list(site):
            for key in vm.keys():
                if key == 'hostname':
                    f.write(vm[key][:-13] + ' ')
                elif key == 'ansible_host':
                    f.write('ansible_host=' + vm[key] + ' ')
                else:
                    f.write(key.lower() + '_ip=' + vm[key] + ' ')
            f.write('\n')
        f.write('\n')
        f.write('[pl_' + item.lower() + '1_pic]\n')
        for vm in pic_list(site):
            for key in vm.keys():
                if key == 'hostname':
                    f.write(vm[key][:-13] + ' ')
                elif key == 'ansible_host':
                    f.write('ansible_host=' + vm[key] + ' ')
            f.write('\n')
        f.write('\n')
        f.write('[pl_' + item.lower() + '1_psm]\n')
        for vm in psm_list(site):
            for key in vm.keys():
                if key == 'hostname':
                    f.write(vm[key][:-13] + ' ')
                elif key == 'ansible_host':
                    f.write('ansible_host=' + vm[key] + ' ')
            f.write('\n')
        f.write('\n')
        site = pl_list(item, 'Site2')
        f.write('[pl_' + item.lower() + '2_pre]\n')
        for vm in pre_list(site):
            for key in vm.keys():
                if key == 'hostname':
                    f.write(vm[key][:-13] + ' ')
                elif key == 'ansible_host':
                    f.write('ansible_host=' + vm[key] + ' ')
                else:
                    f.write(key.lower() + '_ip=' + vm[key] + ' ')
            f.write('\n')
        f.write('\n')
        f.write('[pl_' + item.lower() + '2_pic]\n')
        for vm in pic_list(site):
            for key in vm.keys():
                if key == 'hostname':
                    f.write(vm[key][:-13] + ' ')
                elif key == 'ansible_host':
                    f.write('ansible_host=' + vm[key] + ' ')
            f.write('\n')
        f.write('\n')
        f.write('[pl_' + item.lower() + '2_psm]\n')
        for vm in psm_list(site):
            for key in vm.keys():
                if key == 'hostname':
                    f.write(vm[key][:-13] + ' ')
                elif key == 'ansible_host':
                    f.write('ansible_host=' + vm[key] + ' ')
            f.write('\n')
        f.write('\n')
        print('Creating regional groups for ' + item)
        for group in pl_groups(item):
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