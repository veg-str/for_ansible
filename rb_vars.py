import openpyxl, yaml, re

ip_plan = 'project_files\\Tele2_IP_plan_v2.02.xlsx'
vars_dir = 'c:\\temp\\host_vars\\'

# Open Excel file in read-only mode
wb = openpyxl.load_workbook(ip_plan, True)

#mr = ['nin']
mr = ['spb', 'nin', 'ekt', 'nsk', 'ros', 'mos']

def get_rb_list(region):
    ws = wb[region.upper()]
    rb_list = []
    for row in ws.iter_rows():
        if re.search("^rb[0-9]+", str(row[1].value)):
            rb_list.append({'vm_name': row[1].value, 'vlan': row[3].value, 'ip': row[5].value})
    return rb_list


def get_rb_vars(rb, rb_list):
    vars = {}
    vars['vip'] = {}
    for item in rb_list:
        if item['vm_name'] == rb and item['vlan'] == 'Radius':
            vars['radius_ip'] = item['ip']
        elif item['vm_name'] == rb and item['vlan'] == 'RadiusFE':
            vars['radiusfe_ip'] = item['ip']
        elif re.search(rb[:8] + ' \(VRRP VIP\)', item['vm_name']) and item['vlan'] == 'Radius':
            vars['vip']['radius_vip'] = item['ip']
        elif re.search(rb[:8] + ' \(VRRP VIP\)', item['vm_name']) and item['vlan'] == 'RadiusFE':
            vars['vip']['radiusfe_vip'] = item['ip']
    return vars


for region in mr:
    rb_list = get_rb_list(region)
    for rb in rb_list:
        if rb['vlan'] == 'vm_Mgmt':
            rb_vars = get_rb_vars(rb['vm_name'], rb_list)
            with open(vars_dir + rb['vm_name'][:9] + '.yml', 'w', newline='\n') as file:
                documents = yaml.dump(rb_vars, file)
