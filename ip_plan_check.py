import openpyxl, ipaddress

ip_plan = 'project_files\\Tele2_IP_plan_v038.xlsx'
mr = ['ekt']
#mr = ['spb', 'mos', 'ros', 'nin', 'ekt', 'nsk']
vlans = ['Gx', 'Gy', 'Radius', 'RadiusFE', 'Resource', 'Provisioning', 'ClusterSync', 'OOB_Mgmt', 'Host_Mgmt', 'vm_Mgmt', 'DataFeed']
check_results = {}

wb = openpyxl.load_workbook(ip_plan)
error_cell = openpyxl.styles.Font(color=openpyxl.styles.colors.RED)


def check_subnets(region):
    test_result = 'PASSED'
    print('Checking subnets in region ' + region.upper())
    net = wb.defined_names[region + '_nets'].attr_text
    ws = wb[str(net[1:net.find('!') - 1])]
    rng = net[net.find('!') + 1:]
    for i in 5, 8:
        for row in ws[rng]:
            try:
                if row[0].value == 'Supernet':
                    supernet = ipaddress.ip_network(row[i].value + row[3].value)
                elif row[0].value in vlans or row[0].value == 'Link subnets':
                    net = ipaddress.ip_network(row[i].value + row[3].value)
                    if not net.subnet_of(supernet):
                        row[i].font = error_cell
                        test_result = 'FAILED'
            except(ValueError, TypeError):
                row[i].font = error_cell
                test_result = 'FAILED'
    return test_result


def check_gw(region):
    test_result = 'PASSED'
    print('Checking gateways in region ' + region.upper())
    net = wb.defined_names[region + '_nets'].attr_text
    ws = wb[str(net[1:net.find('!') - 1])]
    rng = net[net.find('!') + 1:]
    for i in 5, 8:
        for row in ws[rng]:
            try:
                if row[0].value in vlans:
                    net = ipaddress.ip_network(row[i].value + row[3].value)
                    if ipaddress.ip_address(row[i+1].value) != net[-2]:
                        row[i+1].font = error_cell
                        test_result = 'FAILED'
            except(ValueError, TypeError):
                row[i].font = error_cell
                test_result = 'FAILED'
    return test_result


def check_ip(region, vlan):
    test_result = 'PASSED'
    print('Checking IPs in VLAN ' + vlan + ' in region ' + region.upper())
    net = wb.defined_names[region + '_nets'].attr_text
    ws = wb[str(net[1:net.find('!') - 1])]
    rng = net[net.find('!') + 1:]
    for row in ws[rng]:
        if row[0].value == vlan:
            net1 = ipaddress.ip_network(row[5].value + row[3].value)
            gw1 = ipaddress.ip_address(row[5].value)
            net2 = ipaddress.ip_network(row[8].value + row[3].value)
            gw2 = ipaddress.ip_address(row[9].value)
    ws = wb[region.upper()]
    for row in ws.iter_rows():
        if row[3].value == vlan:
            if row[6].value == 'Site1':
                net = net1
                gw = gw1
            elif row[6].value == 'Site2':
                net = net2
                gw = gw2
            if ipaddress.ip_address(row[5].value) not in net.hosts() or ipaddress.ip_address(row[5].value) == gw:
                row[5].font = error_cell
                test_result = 'FAILED'
    return test_result


def check_uniq_ip(region, vlan):
    test_result = 'PASSED'
    print('Checking for IPs uniq in VLAN ' + vlan + ' in region ' + region.upper())
    ws = wb[region.upper()]
    addr = []
    for row in ws.iter_rows():
        if row[3].value == vlan:
            addr.append(row[5].value)
    addr_set = set(addr)
    if len(addr) != len(addr_set):
        test_result = 'FAILED'
    return test_result


for region in mr:
    check_results['Subnets'] = check_subnets(region)
    check_results['GW'] = check_gw(region)
    for vlan in vlans:
        check_results['IP_' + vlan] = check_ip(region, vlan)
    for vlan in vlans:
        check_results['Uniq_IP_' + vlan] = check_uniq_ip(region, vlan)

print('Check results:')
for test in check_results:
    print(test + ': ' + check_results[test])


wb.save(ip_plan)
wb.close()