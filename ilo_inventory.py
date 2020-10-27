from shared import ip_plan

inventory_file = 'c:/temp/inventory/ilo'

mr = ['SPB', 'MOS', 'NIN', 'EKT', 'NSK']


with open(inventory_file, 'w', newline='\n') as f:
    f.write('# List of KVMs\n\n')
    for region in mr:
        print(f'Collecting data about KVM in {region}')
        f.write(f'# {region}\n')
        sheet_list = ip_plan.get_sheets_list(region)
        mr_sites = set()
        for sheet in sheet_list:
            dom_num = sheet_list.index(sheet) + 1
            f.write(f'# Domain {dom_num}\n')
            ilo_list = ip_plan.filter_by_vlan('OOB_Mgmt', ip_plan.rows_to_dict(sheet))
            sites = sorted(set(map(lambda i: i['site'], ilo_list)))
            for site in sites:
                f.write(f'[ilo_{region.lower()}{site[-1]}_d{dom_num}]\n')
                for ilo in ilo_list:
                    if ilo['site'] == site:
                        f.write(f'ilo_{ilo["hostname"][:-13]} ansible_host={ilo["ip"]}\n')
                f.write('\n')
