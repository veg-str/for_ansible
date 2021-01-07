import json
import openpyxl
import re
import jinja2
import datetime
from pprint import pprint
from shared import ip_plan, sig_int
from shared.classes import PsmComponent

conf_template = 'project_files\\psm_config_template.json'
new_conf_path = 'c:\\temp\\psm_conf\\'

now = str(datetime.datetime.today().isoformat(sep="_", timespec="minutes")).replace(":", "_")

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('project_files')
)

mr = ['MOS']
# mr = ['EKT', 'NIN', 'NSK', 'MOS']

defaultDestinationRealm = 'bercut'
originRealm = 'node.epc.mnc020.mcc250.3gppnetwork.org'

components_changed = []
components_to_replace_per_dom = [
    'psm.provisionerng.host'
]

components_to_replace_per_psm = [
    'psm.diameterdmanager',
]

components_to_change_per_dom = []

components_to_change_per_psm = [
    'psm.diameter',
    'psm.diameter.peers',
    'psm.model.syncer.client',
    'psm.schema',
    'psm.source.udp.radius',
    'psm.provisionerng.base'
]


def get_non_changed_components(source):
    components_non_changed = []
    for component in source:
        if component['componentId'] not in components_to_replace_per_dom + components_to_replace_per_psm:
            element = PsmComponent(
                component['componentId'],
                component['instanceId'],
                component['version'],
                config=component['config']
            )
            components_non_changed.append(element)
    return components_non_changed


def get_gx_config(srv, peer_list, region, conf_type):
    if int(re.search('\d\d', srv).group(0)) % 2 != 0:
        part = 'odd'
        env.globals['originRealm'] = region.lower() + '01.' + originRealm
    else:
        part = 'even'
        env.globals['originRealm'] = region.lower() + '02.' + originRealm
    template = env.get_template(f'{conf_type}_gx_config.txt.j2')
    env.globals['originHost'] = srv[:5]
    env.globals['gxVIP'] = psm_vip['Gx']
    env.globals['peer_list'] = peer_list[part]
    gx_config = template.render()
    return gx_config


def get_psm_diameterdmanager(cluster):

    res = 'test1'
    return res


def get_psm_provisionerng_host(srv_list):
    pre_list = ip_plan.filter_by_type(srv_list, 'pre')
    provisioner = []
    for pre in pre_list:
        element = PsmComponent(
            'psm.provisionerng.host',
            config={
                "hostName": pre.provisioning_ip,
                "serviceOrPort": "",
                "useDirectConnection": False,
                "startupState": "enabled",
                "group": ""
            }
        )
        provisioner.append(element)
    return provisioner


with open(conf_template, "r", newline='\n') as file:
    config_template = json.load(file)
    # Get common for all regions components
    shared_components = get_non_changed_components(config_template['components'])

for region in mr:
    sheet_list = ip_plan.get_sheets_list(region)
    for sheet in sheet_list:
        dom_num = int(sheet[-1])
        srv_list = ip_plan.get_pl_list(region, dom_num)
        psm_list = ip_plan.filter_by_type(srv_list, 'psm')
        clusters_list = ip_plan.get_psm_clusters(region, dom_num)

        # Get common for domain components
        domain_components = []
        for component in components_to_replace_per_dom + components_to_change_per_dom:
            func = locals()[f'get_{component}'.replace('.', '_')]
            element = func(srv_list)
            domain_components.append(element)

        # Get common for cluster components
        for cluster in clusters_list:
            cluster_components = []
            for component in components_to_replace_per_psm + components_to_change_per_psm:
                func = locals()[f'get_{component}'.replace('.', '_')]
                element = func(cluster)
                cluster_components.append(element)

                pass
            pass
