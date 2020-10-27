import openpyxl
import re

file_ip_plan = 'project_files\\Tele2_IP_plan_v3.03.xlsx'
base_srv_types = ['pre', 'psm', 'pic', 'apic']
ext_srv_types = ['epsm', 'rb', 'log', 'rs']

wb = openpyxl.load_workbook(file_ip_plan, True)


def get_sheets_list(region):
    ws_list = list(filter(lambda i: re.search('^'+region, i), wb.sheetnames))
    return ws_list


def rows_to_dict(sheet):
    rows = []
    ws = wb[sheet]
    for row in ws.iter_rows():
        rows.append({
            'hostname': row[0].value,
            'vm': row[1].value,
            'vlan': row[3].value,
            'ip': row[5].value,
            'site': row[6].value
        })
    return rows


def filter_host_only(src):
    res = src['vlan'] == 'Host_Mgmt'
    return res


def filter_vm_only(src):
    res = src['vlan'] == 'vm_Mgmt'
    return res


def filter_by_vlan(vlan, src_list):
    filtered_rows = list(filter(lambda i: i['vlan'] == vlan, src_list))
    return filtered_rows


def check_psm(src):
    res = False
    if src['vm'] is not None:
        res = re.search('^psm', src['vm'])
    return res


def check_pre(src):
    res = False
    if src['vm'] is not None:
        res = re.search('^pre', src['vm'])
    return res


def get_psm_vip(srv, s_list):
    psm_vip = {}
    for s in s_list:
        if re.search(srv + ".*\(VRRP VIP\)", s['vm']):
            vlan = re.search('\D*', s['vlan']).group(0)
            psm_vip[vlan] = s['ip']
    return psm_vip


def get_sw_list(sheet, dom_num):
    wsid = wb.sheetnames.index('IP-plan')
    net = wb.defined_names.get(sheet.lower(), wsid).attr_text
    ws = wb[str(net[1:net.find('!') - 1])]
    rng = net[net.find('!') + 1:]
    sw_list = []
    for row in ws[rng]:
        if row[0].value == 'OOB_Mgmt':
            sw_list.append({'swname': f'{sheet[:3].upper()}-TMS-1-{dom_num}', 'ip': row[6].value, 'site': 'Site1'})
            sw_list.append({'swname': f'{sheet[:3].upper()}-TMS-2-{dom_num}', 'ip': row[9].value, 'site': 'Site2'})
    return sw_list