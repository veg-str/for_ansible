import json
import openpyxl
import re
import jinja2
import datetime
from pprint import pprint
from shared import ip_plan, sig_int

file_ip_plan = 'project_files\\Tele2_IP_plan_v2.04-draft.xlsx'
conf_template = 'project_files\\psm_config_template.json'
file_sig_int = 'project_files\\Tele2_TMS_Signal_integration_v3.5.xlsx'
new_conf_path = 'c:\\temp\\psm_conf\\'

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('project_files')
)

mr = ['MOS']
# mr = ['EKT', 'NIN', 'NSK', 'MOS']

defaultDestinationRealm = 'bercut'
originRealm = 'node.epc.mnc020.mcc250.3gppnetwork.org'


def prepare_template(source):
    parts = source['components']
    remove_list = ['psm.diameterdmanager', 'psm.provisionerng.host']
    new_list = []
    for part in parts:
        if part['componentId'] not in remove_list:
            new_list.append(part)
    source['components'] = new_list
    return source

'''
def psm_list(region):
    psm_list = {}
    wb = openpyxl.load_workbook(file_ip_plan, True)
    ws = wb[region]
    for row in ws.iter_rows():
        if re.search("^psm\d\d\." + region.lower() + "\d.*", str(row[1].value)) and row[3].value == 'vm_Mgmt':
            psm_list[row[1].value] = {'Site': row[6].value}
    for psm in psm_list.keys():
        psm_ips = {}
        for row in ws.iter_rows():
            if row[1].value == psm:
                psm_ips[row[3].value] = row[5].value
        psm_list[psm] = psm_ips
    return psm_list
'''

def get_pre_list(region):
    pre_list = []
    wb = openpyxl.load_workbook(file_ip_plan, True)
    ws = wb[region]
    for row in ws.iter_rows():
        if re.search("^pre\d\d\." + region.lower() + "\d.*", str(row[1].value)) and row[3].value == 'Provisioning':
            pre_list.append(row[5].value)
    return pre_list


def cluster_list(region):
    cluster_list = []
    wb = openpyxl.load_workbook(file_ip_plan, True)
    ws = wb[region]
    for row in ws.iter_rows():
        if re.search("^psm\d\d\." + region.lower() + ".*\(VRRP VIP\)", str(row[1].value)) and row[3].value == 'Radius':
            cluster_list.append(row[1].value[:9])
    return cluster_list


def get_psm_vip(srv):
    wb = openpyxl.load_workbook(file_ip_plan, True)
    ws = wb[region]
    psm_vip = {}
    for row in ws.iter_rows():
        if re.search(srv + ".*\(VRRP VIP\)", str(row[1].value)):
            psm_vip[row[2].value] = row[5].value
    return psm_vip


def get_radius_secret(region):
    wb = openpyxl.load_workbook(file_sig_int, True)
    ws = wb[region]
    radius_secret = ws['M6'].value
    return radius_secret


def get_gy_peers(mr):
    wb = openpyxl.load_workbook(file_sig_int, True)
    s1_gy = wb.defined_names[mr.lower() + '_s1_gy'].attr_text
    ws = wb[mr]
    rng = s1_gy[s1_gy.find('!') + 1:]
    gy_peers = []
    for row in ws[rng]:
        gy_peers.append({"peerId": row[13].value,
                         "hostName": row[9].value,
                         "port": int(row[11].value),
                         "bindAddress": None,
                         "enabled": True,
                         "watchdogTimeoutMs": 30000
                         })
    gy_peers.append({"peerId": "T2TST-RTUCG-01-2",
                     "hostName": "10.78.245.57",
                     "port": 3878,
                     "bindAddress": None,
                     "enabled": False, #True,
                     "watchdogTimeoutMs": 30000
                     })
    return gy_peers


def get_local_gx_config(srv, region):
    wb = openpyxl.load_workbook(file_sig_int, True)
    ws = wb[region]
    s1_gx = wb.defined_names[region.lower() + '_s1_gx'].attr_text
    s2_gx = wb.defined_names[region.lower() + '_s2_gx'].attr_text
    primPCRF = {}
    secPCRF = {}
    if int(srv[3:5]) % 2 != 0:
        rng = s1_gx[s1_gx.find('!') + 1:]
        env.globals['originRealm'] = region.lower() + '01.' + originRealm
    else:
        rng = s2_gx[s2_gx.find('!') + 1:]
        env.globals['originRealm'] = region.lower() + '02.' + originRealm
    for row in ws[rng]:
        if row[-1].value == 'local_pcrf':
            if row[9].value != None:
                primPCRF['IP'] = row[9].value
                primPCRF['hostName'] = row[13].value
                primPCRF['realm'] = row[14].value
            elif row[10].value != None:
                secPCRF['IP'] = row[10].value
                secPCRF['hostName'] = row[13].value
                secPCRF['realm'] = row[14].value
    template = env.get_template('local_gx_config.txt.j2')
    env.globals['originHost'] = srv[:5]
    env.globals['gxVIP'] = psm_vip['Gx']
    env.globals['primPCRF'] = primPCRF
    env.globals['secPCRF'] = secPCRF
    local_gx_config = template.render()
    return local_gx_config


def get_remote_gx_config(srv, region):
    wb = openpyxl.load_workbook(file_sig_int, True)
    ws = wb[region]
    s1_gx = wb.defined_names[region.lower() + '_s1_gx'].attr_text
    s2_gx = wb.defined_names[region.lower() + '_s2_gx'].attr_text
    primPCRF = {}
    secPCRF = {}
    if int(srv[3:5]) % 2 != 0:
        rng = s1_gx[s1_gx.find('!') + 1:]
        env.globals['originRealm'] = region.lower() + '01.' + originRealm
    else:
        rng = s2_gx[s2_gx.find('!') + 1:]
        env.globals['originRealm'] = region.lower() + '02.' + originRealm
    for row in ws[rng]:
        if row[-1].value == 'dra':
            if row[9].value != None:
                primPCRF['IP'] = row[9].value
                primPCRF['hostName'] = row[13].value
                primPCRF['realm'] = row[14].value
            elif row[10].value != None:
                secPCRF['IP'] = row[10].value
                secPCRF['hostName'] = row[13].value
                secPCRF['realm'] = row[14].value
    template = env.get_template('remote_gx_config.txt.j2')
    env.globals['originHost'] = srv[:5]
#    env.globals['originRealm'] = originRealm
    env.globals['gxVIP'] = psm_vip['Gx']
    env.globals['primPCRF'] = primPCRF
    env.globals['secPCRF'] = secPCRF
    remote_gx_config = template.render()
    return remote_gx_config


def edit_psm_schema(config, srv):
    obj = config['objects']
    for item in obj:
        if item['name'] == 'session':
            fields = obj[obj.index(item)]['fields']
            for field in fields:
                if field[1]['name'] == 'psmOriginHost':
                    field[1]['defaultValue'] = srv + '.' + originRealm
    config['objects'] = obj
    messages = config['messages']
    for msg in messages:
        if msg['name'] == 'tele2cdr':
            fields = messages[messages.index(msg)]['fields']
            for field in fields:
                if field['name'] == 'nodeId':
                    field['defaultValue'] = srv
    config['messages'] = messages
    return config


def edit_psm_provisionerng_base(config, srv):
    fields = config['schemas'][0]['fields']
    for field in fields:
        if field['name'] == 'psmIdentity':
            field['mapping'] = '\"' + srv[:5] + '\"'
    config['schemas'][0]['fields'] = fields
    return config


def set_psm_diameterdmanager(gx_config):
    element = {'componentId': 'psm.diameterdmanager',
               'instanceId': None,
               'version': 5,
               'config': {'config': gx_config}
               }
    return element


def set_psm_provisionerng_host(pre):
    element = {'componentId': 'psm.provisionerng.host',
               'instanceId': None,
               'version': 4,
               'config': {'hostName': pre,
                          'serviceOrPort': '',
                          'useDirectConnection': False,
                          'startupState': 'enabled',
                          'group': ''}
               }
    return element


for region in mr:
    sheet_list = ip_plan.get_sheets_list(region)
    for sheet in sheet_list:
        full_srv_list = ip_plan.rows_to_dict(sheet)
        gy_peers = sig_int.get_gy_peers(sheet)
        srv_type = 'psm'
        psm_list = list(filter(ip_plan.check_srv_type, full_srv_list))
        pprint(psm_list)

    '''
    srv_list = cluster_list(region)
    pprint(srv_list)
    virtual_ips = {}
    gy_peers = get_gy_peers(region)
    psms = psm_list(region)
    pre_list = get_pre_list(region)
    radius_secret = get_radius_secret(region)
    with open(conf_template, "r", newline='\n') as file:
        config_template = json.load(file)
        for srv in srv_list:
            config_source = prepare_template(config_template)
            psm_vip = get_psm_vip(srv)
            # **** Editing different component parameters ****
            components = config_source['components']
            for component in components:
                if component['componentId'] == 'psm.diameter':
                    component['config']['originHost'] = srv[:9]
                    for gy_session in component['config']['gySessions']:
                        gy_session['defaultDestinationRealm'] = defaultDestinationRealm
                elif component['componentId'] == 'psm.diameter.peers':
                    component['config']['routes'][0]['routes'][0]['destinationRealm'] = defaultDestinationRealm
                    peers = []
                    for peer in gy_peers:
                        peer["bindAddress"] = psm_vip['Gy']
                        peers.append(peer['peerId'])
                    component['config']['routes'][0]['routes'][0]['peerIds'] = peers
                    component['config']['peers'] = gy_peers
                elif component['componentId'] == 'psm.model.syncer.client':
                    syncer_client = []
                    for psm in psms.keys():
                        if srv in psm:
                            syncer_client.append({'hostName': psms[psm]['ClusterSync'],
                                                  'serviceOrPort': "",
                                                  'useDirectConnection': False})
                    component['config']['nodes'] = syncer_client
                elif component['componentId'] == 'psm.schema':
                    component['config'] = edit_psm_schema(component['config'], srv)
                elif component['componentId'] == 'psm.source.udp.radius':
                    component['config']['hostName'] = psm_vip['Radius']
                    component['config']['secrets'][0]['secret'] = radius_secret
                elif component['componentId'] == 'psm.provisionerng.base':
                    component['config']['identity'] = srv[:5]
                    component['config'] = edit_psm_provisionerng_base(component['config'], srv)
            # **** Adding remote and local Gx configuration sections ****
            components.append(set_psm_diameterdmanager(get_remote_gx_config(srv, region)))
            components.append(set_psm_diameterdmanager(get_local_gx_config(srv, region)))
            # **** Adding Provisioning component for all PRE in region ****
            for pre in pre_list:
                components.append(set_psm_provisionerng_host(pre))
            # **** Writing new config to JSON file ****
            new_config_file = new_conf_path + srv.replace('.', '_') + '_' + str(
                datetime.datetime.today().isoformat(sep='_', timespec='minutes')).replace(':', '_') + '.json'
            with open(new_config_file, 'w', newline='\n') as new_cfg:
                json.dump(config_source, new_cfg)'''
