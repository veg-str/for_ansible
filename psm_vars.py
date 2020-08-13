import openpyxl
import yaml
import re

ip_plan = 'project_files\\Tele2_IP_plan_v2.04-draft.xlsx'
vars_dir = 'c:\\temp\\host_vars\\'

# Open Excel file in read-only mode
wb = openpyxl.load_workbook(ip_plan, True)

mr = ['MOS']
#mr = ['SPB', 'MOS', 'ROS', 'NIN', 'EKT', 'NSK']
quorum = 1


def get_sheets_list(region):
    ws_list = list(filter(lambda i: re.search('^'+region, i), wb.sheetnames))
    return ws_list


def get_rb_vips(sheet):
    rb_vips = {}
    ws = wb[sheet.upper()]
    for row in ws.iter_rows():
        if re.search("^rb\d\d.*\(VRRP VIP\)", str(row[1].value)) and row[3].value == 'Radius':
            rb_vips[re.search("^rb\d{2}", str(row[1].value)).group(0) + '_vip'] = row[5].value
    return rb_vips


def get_prefix(sheet, vlan):
    prefix = ''
    net = wb.defined_names[mr + '_nets'].attr_text
    ws = wb[str(net[1:net.find('!') - 1])]
    rng = net[net.find('!') + 1:]
    for row in ws.iter_rows():
        if row[0].value == vlan:
            prefix = row[3].value
    return prefix


def get_psm_list(sheet):
    ws = wb[sheet.upper()]
    psm_rows = []
    for row in ws.iter_rows():
        if re.search("^psm[0-9]+", str(row[1].value)):
            psm_rows.append({
                'vm_name': row[1].value,
                'vlan': row[3].value,
                'ip': row[5].value
                })
    return psm_rows


def get_psm_vars(curr_srv, srv_list):
    global quorum
    ha = {}
    ha['cluster_id'] = int(re.search('\d{1,2}', curr_srv['vm_name']).group(0))
    ha['quorum'] = quorum
    ha['vip'] = {}
    vars = {}
    vars['cluster'] = {}
    vars['net'] = {}
    for srv in srv_list:
        if srv['vm_name'] == curr_srv['vm_name'] and srv['vlan'] != 'vm_Mgmt':
            vars['net'][re.search("^\D{1,20}", srv['vlan']).group(0).lower() + '_ip'] = srv['ip']
        elif srv['vm_name'] == curr_srv['vm_name'][:-14] + ' (VRRP VIP)':
            ha['vip'][re.search("^\D{1,20}", srv['vlan']).group(0).lower() + '_vip'] = srv['ip']
    vars['cluster']['ha'] = ha
    psm_vars = {curr_srv['vm_name'][:-13]: vars}
    return psm_vars


for region in mr:
    print(f'Collecting data about PSMs in {region}')
    sheet_list = get_sheets_list(region)
    for sheet in sheet_list:
        psm_list = get_psm_list(sheet)
        rb = get_rb_vips(sheet)
        for psm in list(filter(lambda i: not re.search('\(VRRP VIP\)', i['vm_name']), psm_list)):
            vars = get_psm_vars(psm, psm_list)
            var_file = f'{vars_dir}{psm["vm_name"][:10]}.yml'
            with open(var_file, 'w', newline='\n') as f:
                f.write(f'# Variables for {psm["vm_name"]}\n#\n')
                f.write('# High availability related vars\n#\n')
                f.write(yaml.dump(vars[psm['vm_name'][:-13]]['cluster']))
            with open(var_file, 'a', newline='\n') as f:
                f.write('#\n' + '# NICs related vars\n#\n')
                f.write(yaml.dump(vars[psm['vm_name'][:-13]]['net']))
            with open(var_file, 'a', newline='\n') as f:
                f.write('#\n' + '# Other vars\n#\n')
                f.write(yaml.dump(rb))
print('Done')