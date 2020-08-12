import openpyxl
import re

ip_plan = 'project_files\\Tele2_IP_plan_v2.04-draft.xlsx'
inventory_file = 'c:\\temp\\inventory\\other'

mr = ['MOS']
#mr = ['SPB', 'MOS', 'ROS', 'NIN', 'EKT', 'NSK']
base_srv_types = ['pre', 'psm', 'pic', 'apic']
ext_srv_types = ['epsm', 'rb', 'log', 'rs']

wb = openpyxl.load_workbook(ip_plan, True)


def get_sheets_list(region):
    ws_list = list(filter(lambda i: re.search('^'+region, i), wb.sheetnames))
    return ws_list


def rows_to_dict(sheet):
    rows = []
    ws = wb[sheet]
    for row in ws.iter_rows():
        if re.search("^\D{1,4}", str(row[1].value)).group(0) in ext_srv_types:
            rows.append({
                'hostname': row[1].value,
                'vlan': row[3].value,
                'ip': row[5].value,
                'site': row[6].value
                })
    return rows


def site_groups(region, site):
    members = []
    for srv_type in base_srv_types:
        members.append('kvm_' + region.lower() + site + '_' + srv_type)
    groups = {'name': '[kvm_' + region.lower() + site + ':children]', 'members': members}
    return groups


with open(inventory_file, 'w', newline='\n') as f:
    f.write('# List of VMs\n\n')
    for region in mr:
        print(f'Collecting data about VM in {region}')
        f.write(f'# {region}\n')
        sheet_list = get_sheets_list(region)
        mr_sites = set()
        for sheet in sheet_list:
            dom_num = sheet_list.index(sheet) + 1
            f.write(f'# Domain {dom_num}\n')
            srv_list = rows_to_dict(sheet)
            sites = sorted(set(map(lambda i: i['site'], srv_list)))
            for site in sites:
                for type in ext_srv_types:
                    f.write(f'[oth_{region.lower()}{site[-1]}_d{dom_num}_{type}]\n')
                    for row in srv_list:
                        if (row['vlan'] == 'vm_Mgmt' and
                                row['site'] == site and
                                re.search("^" + type, row['hostname'])):
                            f.write(f'{row["hostname"][:-13]} ansible_host={row["ip"]}\n')
                    f.write('\n')