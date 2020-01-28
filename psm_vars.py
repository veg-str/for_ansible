import openpyxl, yaml, re

ip_plan = 'project_files\\Tele2_IP_plan_v036.xlsx'
vars_dir = 'c:\\temp\\host_vars\\'

# Open Excel file in read-only mode
wb = openpyxl.load_workbook(ip_plan, True)

mr = ['spb', 'mos', 'ros', 'nin', 'ekt', 'nsk']
quorum = '2'


def prefix(mr, vlan):
    prefix = ''
    net = wb.defined_names[mr + '_nets'].attr_text
    ws = wb[str(net[1:net.find('!') - 1])]
    rng = net[net.find('!') + 1:]
    for row in ws.iter_rows():
        if row[0].value == vlan:
            prefix = row[3].value
    return prefix



def psm_list(mr):
    ws = wb[mr.upper()]
    psms = []
    for row in ws.iter_rows():
        if row[3].value == 'vm-Mgmt' and re.search("^psm", row[1].value):
            psms.append(row[1].value)
    return psms

def psm_vars(mr, psm):
    ws = wb[mr.upper()]
    ha = {}
    vars = {}
    for row in ws.iter_rows():
        if row[1].value == psm:
            vars[row[3].value] = row[5].value + prefix(mr, row[3].value)
    ha['cluster_id'] = psm[4]
    for row in ws.iter_rows():
        if row[1].value == psm[:-14] + ' (VRRP VIP)':
            ha[row[3].value + '_vip'] = row[5].value + prefix(mr, row[3].value)
    vars['ha'] = ha
    psm_vars = {psm[:-13]: vars}
    return psm_vars


for item in mr:
    psms = psm_list(item)
#    print(psms)
    for psm in psms:
        vars = psm_vars(item, psm)
#        print(vars)
        var_file = vars_dir + psm + '.yml'
        with open(var_file, 'w', newline='\n') as f:
            f.write('# Variables for ' + psm + '\n#\n')
            f.write('# High availability related vars\n#\n')
            f.write('ha:\n')
            f.write('  cluster_id: ' + vars[psm[:-13]]['ha']['cluster_id'] + '\n')
            f.write('  quorum: ' + quorum + '\n')
            f.write('  elector: ' + '\n')
            f.write('  vip:\n')
            f.write('    gx_vip: ' + vars[psm[:-13]]['ha']['Gx_vip'] + '\n')
            f.write('    gy_vip: ' + vars[psm[:-13]]['ha']['Gy_vip'] + '\n')
            f.write('    aaa_vip: ' + vars[psm[:-13]]['ha']['Radius_vip'] + '\n')
            f.write('    res_vip: ' + vars[psm[:-13]]['ha']['Resource_vip'] + '\n')
            f.write('#\n' + '# NICs related vars\n#\n')
            f.write('gx_ip: ' + vars[psm[:-13]]['Gx'] + '\n')
            f.write('gy_ip: ' + vars[psm[:-13]]['Gy'] + '\n')
            f.write('aaa_ip: ' + vars[psm[:-13]]['Radius'] + '\n')
            f.write('res_ip: ' + vars[psm[:-13]]['Resource'] + '\n')
            f.write('provisioning_ip: ' + vars[psm[:-13]]['Provisioning'] + '\n')
            f.write('cluster_sync_ip: ' + vars[psm[:-13]]['ClusterSync'])
        print(vars)

print(yaml.dump(vars[list(vars.keys())[0]]))