# -*- coding: utf-8 -*-
import openpyxl, re, datetime
import lxml.etree as xml

mr = ['ekt', 'nsk']
#mr = ['ekt', 'mos', 'nin', 'nsk', 'ros', 'spb']
base_srv_types = ['pre', 'psm', 'pic']
ext_srv_types = ['epsm', 'rb', 'log', 'rs']
ip_plan = 'project_files\\Tele2_IP_plan_v045.xlsx'
wb = openpyxl.load_workbook(ip_plan, True)


def get_srv_list():
#    ip_plan = 'project_files\\Tele2_IP_plan_v044.xlsx'
#    wb = openpyxl.load_workbook(ip_plan, True)
    host_list = {}
    vm_list = {}
    for region in mr:
        ws = wb[region.upper()]
        h = []
        vm = []
        for row in ws.iter_rows():
            if row[3].value == 'Host_Mgmt':
                h.append({'hostname': row[0].value, 'ip': row[5].value, 'site': row[6].value})
            elif row[3].value == 'vm_Mgmt':
                vm.append({'vmname': row[1].value, 'ip': row[5].value, 'site': row[6].value})
        host_list[region] = h
        vm_list[region] = vm
    return host_list, vm_list


def get_sw_list():
#    ip_plan = 'project_files\\Tele2_IP_plan_v044.xlsx'
#    wb = openpyxl.load_workbook(ip_plan, True)
    sw_list = {}
    for region in mr:
        net = wb.defined_names[region + '_nets'].attr_text
        ws = wb[str(net[1:net.find('!') - 1])]
        rng = net[net.find('!') + 1:]
        sw = []
        for row in ws[rng]:
            if row[0].value == 'OOB_Mgmt':
                sw.append({'swname': region.upper() + '-TMS-1-1', 'ip': row[6].value, 'site': 'Site1'})
                sw.append({'swname': region.upper() + '-TMS-2-1', 'ip': row[9].value, 'site': 'Site2'})
        sw_list[region] = sw
    return sw_list


def create_superputty_inv():
    """
    Creating XML file for SuperPutty
    """
    dir = 'c:\\temp\\mgmt_soft\\'
#    filename = dir + 'SuperPutty_test.xml'
    filename = dir + 'SuperPutty_' + str(
                datetime.datetime.today().isoformat(sep='_', timespec='minutes')).replace(':', '_') + '.xml'
    attr = {}
    root = xml.Element("ArrayOfSessionData")
    for region in mr:
        for sw in switches[region]:
            attr['SessionId'] = 'Tele2-TMS/' + region.upper() + '/' + sw['site'] + '/' + sw['swname']
            attr['SessionName'] = sw['swname']
            attr['ImageKey'] = 'drive_network'
            attr['Host'] = sw['ip']
            attr['Port'] = '22'
            attr['Proto'] = 'SSH'
            attr['PuttySession'] = "Default Settings"
            attr['Username'] = 'jet'
            attr['ExtraArgs'] = ''
            attr['SPSLFileName'] = ''
            xml.SubElement(root, "SessionData", attrib=attr)
        for srv in hosts[region]:
            attr['SessionId'] = 'Tele2-TMS/' + region.upper() + '/' + srv['site'] + '/Hosts/' + srv['hostname']
            attr['SessionName'] = srv['hostname']
            attr['ImageKey'] = 'computer'
            attr['Host'] = srv['ip']
            attr['Port'] = '22'
            attr['Proto'] = 'SSH'
            attr['PuttySession'] = "Default Settings"
            attr['Username'] = 'root'
            attr['ExtraArgs'] = ''
            attr['SPSLFileName'] = ''
            xml.SubElement(root, "SessionData", attrib = attr)
        for srv in vms[region]:
            type = re.search("^\D{1,4}", srv['vmname']).group(0)
            if type in base_srv_types:
                type = type.upper()
                attr['Port'] = '42002'
                attr['Username'] = 'pladmin'
            else:
                type = 'Other'
                attr['Username'] = 'root'
                attr['Port'] = '22'
            attr['SessionId'] = 'Tele2-TMS/' + region.upper() + '/' + srv['site'] + '/' + type + '/' + srv['vmname']
            attr['SessionName'] = srv['vmname']
            attr['ImageKey'] = 'computer'
            attr['Host'] = srv['ip']
            attr['Proto'] = 'SSH'
            attr['PuttySession'] = "Default Settings"
            attr['ExtraArgs'] = ''
            attr['SPSLFileName'] = ''
            xml.SubElement(root, "SessionData", attrib = attr)
    tree = xml.ElementTree(root)
    with open(filename, "wb") as file:
        tree.write(file, pretty_print=True, encoding="utf-8", xml_declaration=True)


def create_plclient_inv():
    """
    Creating XML file for SuperPutty
    """
    dir = 'c:\\temp\\mgmt_soft\\'
    filename = dir + 'PLClient_' + str(
        datetime.datetime.today().isoformat(sep='_', timespec='minutes')).replace(':', '_') + '.psx'
    attr = {}
    root = xml.Element("Systems", version = "2")
    lvl1 = xml.SubElement(root, 'folder', name = "Tele2-TMS")
    for region in mr:
        lvl2 = xml.SubElement(lvl1, 'folder', name = region.upper())
        for site in 'Site1', 'Site2':
            lvl3 = xml.SubElement(lvl2, 'folder', name = site)
            for type in base_srv_types:
                lvl4 = xml.SubElement(lvl3, 'folder', name = type.upper())
                for srv in vms[region]:
                    t = re.search("^\D{1,4}", srv['vmname']).group(0)
                    if srv['site'] == site and t == type:
                        attr['username'] = "jet"
                        attr['address'] = srv['ip']
                        attr['defaultview'] = "SystemOverview"
                        attr['name'] = srv['vmname']
                        attr['Password'] = "00000008789c2b342c0443000bec0289"
                        xml.SubElement(lvl4, 'system', attrib = attr)
    tree = xml.ElementTree(root)
    with open(filename, "wb") as file:
        tree.write(file, pretty_print=True, encoding="utf-8", xml_declaration=False)

switches = get_sw_list()
hosts, vms = get_srv_list()

create_superputty_inv()
create_plclient_inv()