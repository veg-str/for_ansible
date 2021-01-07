# -*- coding: utf-8 -*-
import openpyxl
import re
from datetime import datetime
import lxml.etree as xml
from shared import ip_plan

mr = ['MOS','EKT', 'NIN', 'NSK', 'SPB']
# mr = ['MOS','EKT', 'NIN', 'NSK', 'SPB', 'ROS']
base_srv_types = ['pre', 'psm', 'pic', 'apic']
ext_srv_types = ['epsm', 'rb', 'log', 'rs']
ip_plan_file = 'project_files\\Tele2_IP_plan_v3.02.xlsx'
wb = openpyxl.load_workbook(ip_plan_file, True)

f_dir = 'c:\\temp\\mgmt_soft\\'


def create_superputty_inv(root):
    attr = {}
    for sw in sw_list:
        attr['SessionId'] = f'Tele2-TMS/{region.upper()}/Domain{dom_num}/{sw["swname"]}'
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
    for srv in host_list:
        attr['SessionId'] = f'Tele2-TMS/{region.upper()}/Domain{dom_num}/{srv["site"]}/Hosts/{srv["hostname"]}'
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
    for srv in vm_list:
        type = re.search("^\D{1,4}", srv['vm']).group(0)
        if type in base_srv_types:
            type = type.upper()
            attr['Port'] = '42002'
            attr['Username'] = 'pladmin'
        else:
            type = 'Other'
            attr['Username'] = 'root'
            attr['Port'] = '22'
        attr['SessionId'] = f'Tele2-TMS/{region.upper()}/Domain{dom_num}/{srv["site"]}/{type}/{srv["vm"]}'
        attr['SessionName'] = srv['vm']
        attr['ImageKey'] = 'computer'
        attr['Host'] = srv['ip']
        attr['Proto'] = 'SSH'
        attr['PuttySession'] = "Default Settings"
        attr['ExtraArgs'] = ''
        attr['SPSLFileName'] = ''
        xml.SubElement(root, "SessionData", attrib = attr)
    return root


def create_plclient_inv():
    attr = {}
    lvl3 = xml.Element('folder', name = f'Domain{dom_num}')
    for site in sites:
        lvl4 = xml.Element('folder', name=site)
        for s_type in base_srv_types:
            lvl5 = xml.Element('folder', name=s_type.upper())
            for srv in vm_list:
                t = re.search("^\D{1,4}", srv['vm']).group(0)
                if srv['site'] == site and t == s_type:
                    attr['username'] = "jet"
                    attr['address'] = srv['ip']
                    attr['defaultview'] = "SystemOverview"
                    attr['name'] = srv['vm']
                    attr['Password'] = "00000008789c2b342c0443000bec0289"
                    xml.SubElement(lvl5, 'system', attrib=attr)
            lvl4.append(lvl5)
        lvl3.append(lvl4)
    return lvl3


sp_root = xml.Element("ArrayOfSessionData")
pl_root = xml.Element("Systems", version = "2")
pl_lvl1 = xml.SubElement(pl_root, 'folder', name = "Tele2-TMS")
for region in mr:
    sheets = ip_plan.get_sheets_list(region)
    pl_lvl2 = xml.SubElement(pl_lvl1, 'folder', name = region.upper())
    for sheet in sheets:
        dom_num = sheets.index(sheet) + 1
        host_list = list(filter(ip_plan.filter_host_only, ip_plan.rows_to_dict(sheet)))
        vm_list = list(filter(ip_plan.filter_vm_only, ip_plan.rows_to_dict(sheet)))
        sw_list = ip_plan.get_sw_list(sheet, dom_num)
        sites = sorted(set(map(lambda i: i['site'], host_list)))
        sp_root = create_superputty_inv(sp_root)
        pl_lvl2.append(create_plclient_inv())

tree = xml.ElementTree(sp_root)
filename = f'{f_dir}SuperPutty_{str(datetime.today().isoformat(sep="_", timespec="minutes")).replace(":", "_")}.xml'
with open(filename, "wb") as file:
    tree.write(file, pretty_print=True, encoding="utf-8", xml_declaration=True)

tree = xml.ElementTree(pl_root)
filename = f'{f_dir}PLCient_{str(datetime.today().isoformat(sep="_", timespec="minutes")).replace(":", "_")}.psx'
with open(filename, "wb") as file:
    tree.write(file, pretty_print=True, encoding="utf-8", xml_declaration=True)