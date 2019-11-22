import os, openpyxl, yaml

ip_plan_dir = 'c:\\Users\\ve.gusarin\\Seafile\\Tele2-2018-TMS\\07. Design\\'
ip_plan = 'Tele2_IP_plan_v031.xlsx'
vars_dir = 'c:\\temp\\group_vars\\'

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
        if row[1].value == psm[:-10] + ' (VRRP VIP)':
            ha[row[3].value + '_vip'] = row[5].value
    vars['ha'] = ha
    psm_vars = {psm[:-9]: vars}
    return psm_vars

for item in mr:
    psms = psm_list(item)
    print(psms)
    for psm in psms:
        vars = psm_vars(item, psm)
        print(vars)

print(yaml.dump(vars[list(vars.keys())[0]]))