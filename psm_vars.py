import os, openpyxl, yaml

ip_plan_dir = 'c:\\Users\\ve.gusarin\\Seafile\\Tele2-2018-TMS\\07. Design\\'
ip_plan = 'Tele2_IP_plan_v035.xlsx'
vars_dir = 'c:\\temp\\group_vars\\'
quorum = '2'

mr = ['SPB', 'MOS', 'ROS', 'NIN', 'EKT', 'NSK']

os.chdir(vars_dir)

# Open Excel file in read-only mode:q

wb = openpyxl.load_workbook(ip_plan_dir + ip_plan, True)

def psm_list(mr):
    ws = wb[mr]
    psms = []
    for row in ws.iter_rows():
        if row[3].value == 'vm-Mgmt' and 'psm' in row[1].value and 'epsm' not in row[1].value:
            psms.append(row[1].value)
    return psms

def psm_vars(mr, psm):
    ws = wb[mr]
    ha = {}
    vars = {}
    for row in ws.iter_rows():
        if row[1].value == psm:
            vars[row[3].value] = row[5].value
    ha['cluster_id'] = psm[4]
    for row in ws.iter_rows():
        if row[1].value == psm[:-14] + ' (VRRP VIP)':
            ha[row[3].value + '_vip'] = row[5].value
    vars['ha'] = ha
    psm_vars = {psm[:-13]: vars}
    return psm_vars


for item in mr:
    psms = psm_list(item)
#    print(psms)
    for psm in psms:
        vars = psm_vars(item, psm)
#        print(vars)
        var_file = psm + '.yml'
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