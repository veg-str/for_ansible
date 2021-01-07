

class PsmComponent:
    """ PSM config components element """

    def __init__(self, c_id, i_id='none', ver=1, **config):
        self.componentId = c_id
        self.instanceId = i_id
        self.version = ver
        self.config = config

    def update_config_element(self, key, value):
        self.config[key] = value


class PlServer:
    """ Packetlogic server """

    def __init__(self, pl_type, hostname, mgmt_ip, region, site, domain, other_ip):
        self.pl_type = pl_type
        self.hostname = hostname
        self.mgmt_ip = mgmt_ip
        self.region = region
        self.site = site
        self.domain = domain

        if self.pl_type == 'pre':
            self.provisioning_ip = other_ip['Provisioning']
        if self.pl_type == 'psm':
            self.provisioning_ip = other_ip['Provisioning']
            self.gx_ip = other_ip['Gx']
            self.gy_ip = other_ip['Gy']
            self.radius_ip = other_ip['Radius']
            self.clustersync_ip = other_ip['ClusterSync']
            self.resourse_ip = other_ip['Resource']


class PsmCluster:
    """ Packetlogic PSM cluster"""

    def __init__(self, name, id, members, vip):
        self.name = name
        self.id = id
        self.members = members
        self.gx_vip = vip['Gx']
        self.gy_vip = vip['Gy']
        self.radius_vip = vip['Radius']
        self.resource_vip = vip['Resource']

