import openpyxl, yaml, ipaddress, copy, os
from pprint import pprint

sig_int = 'project_files\\Tele2_TMS_Signal_integration_v4.4.xlsx'
vars_dir = 'c:\\temp\\group_vars\\'

# Open Excel file in read-only mode
wb = openpyxl.load_workbook(sig_int, True)

#mr = ['nin']
#mr = ['spb', 'nin', 'ekt', 'nsk', 'ros', 'mos']
mr = ['nin', 'ekt', 'nsk']


def make_var_dirs(dir_name):
    if dir_name not in os.listdir(vars_dir):
        os.mkdir(vars_dir + dir_name)
    dir = vars_dir + dir_name + '\\'
    return dir

def get_sig_nets():
    signals = ['radius', 'gx', 'gy']
    sig_nets = {}
    for region in mr:
        sig_nets[region] = {}
        for item in signals:
            nets = []
            for i in 1, 2:
                dn = wb.defined_names[region + '_s' + str(i) + '_' + item].attr_text
                ws = wb[str(dn[0:dn.find('!')])]
                rng = dn[dn.find('!') + 1:]
                for row in ws[rng]:
                    if row[15].value != None:
                        nets.append({'ip': row[15].value.strip(), 'site': i})
                sig_nets[region][item] = nets
    return sig_nets


def summarise_nets(range): # Summarise addresses into /24 subnets
    supernets = set()
    for ip in range:
        supernets.add(str(ipaddress.IPv4Network(ip['ip']).supernet(new_prefix=24)))
    supernets = list(set(supernets))
    return supernets


def check_site_of_net(net, region, sig):
    for addr in signal_networks[region][sig]:
        if ipaddress.IPv4Network(addr['ip']).subnet_of(ipaddress.IPv4Network(net)):
            site = addr['site']
    return site


def get_psm_static_route(sig, nets, region):
    static_routes = []
    # Signal Integration dependent part
    next_hops = {
        'radius': {
            1: '{{ rb01_vip }}',
            2: '{{ rb02_vip }}'
        },
        'gx': '{{ networks[site]["Gx1" if inventory_hostname_short[-2:] | int is odd else "Gx2"].gw }}',
        'gy': '{{ networks[site]["Gy1" if inventory_hostname_short[-2:] | int is odd else "Gy2"].gw }}'
    }
    interfaces = {
        'radius': "Radius",
        'gx': "Gx",
        'gy': "Gy"
    }
    if sig == 'radius':
        for net in nets:
            site = check_site_of_net(net, region, sig)
            sr = {
                'route': net,
                'next_hop': next_hops['radius'][site],
                'interface': interfaces['radius']
            }
            static_routes.append(sr)
    else:
        for net in nets:
            sr = {
                'route': net,
                'next_hop': next_hops[sig],
                'interface': interfaces[sig]
            }
            static_routes.append(sr)
    return static_routes


def get_psm_const_sr():
    # Signal Integration independent part. Constant for all regions
    static_routes = []
    sr = {
        'route': "{{ networks[other_site].Provisioning.subnet + networks[other_site].Provisioning.prefix }}",
        'next_hop': "{{ networks[site].Provisioning.gw }}",
        'interface': "Provisioning"
    }
    static_routes.append(sr)
    sr = {
        'route': "{{ networks[other_site].ClusterSync.subnet + networks[other_site].ClusterSync.prefix }}",
        'next_hop': "{{ networks[site].ClusterSync.gw }}",
        'interface': "ClusterSync"
    }
    static_routes.append(sr)
    return static_routes


# Getting Signal Interation subnets
signal_networks = get_sig_nets()

#  Get summarized subnets
sum_networks = copy.deepcopy(signal_networks)
for region in mr:
    keys = list(sum_networks[region].keys())
    for key in keys:
        nets = summarise_nets(sum_networks[region][key])
        nets.sort()
        sum_networks[region][key] = nets

# Create PSM group vars files with static routes
for region in mr:
    keys = list(sum_networks[region].keys())
    psm_sr = []
    dir = make_var_dirs('pl_' + region + '_psm')
    with open(dir + 'static_routes.yml', 'w', newline='\n') as file:
        for key in keys:
            nets = sum_networks[region][key]
            psm_sr.extend(get_psm_static_route(key, nets, region))
        psm_sr.extend(get_psm_const_sr())
        yaml.dump({'static_routes': psm_sr}, file, width=120, sort_keys=False)


# Create RB group vars files with static routes
for region in mr:
    rb_sr = []
    nets = sum_networks[region]['radius']
    for net in nets:
        sr = {
            'route': net,
            'next_hop': "{{ networks[site].RadiusFE.gw }}",
            'interface': "enp3s0"
        }
        rb_sr.append(sr)
    dir = make_var_dirs('oth_' + region + '_rb')
    with open(dir + 'static_routes.yml', 'w', newline='\n') as file:
        yaml.dump({'static_routes': rb_sr}, file, width=120, sort_keys=False)


# Create ePSM group vars files with static routes
for region in mr:
    epsm_sr = []
    nets = sum_networks[region]['radius']
    for net in nets:
        sr = {
            'route': net,
            'next_hop': "{{ networks[site].Radius.gw }}",
            'interface': "enp2s0"
        }
        epsm_sr.append(sr)
    sr = {
        'route': "{{ networks[other_site].Provisioning.subnet + networks[other_site].Provisioning.prefix }}",
        'next_hop': "{{ networks[site].Provisioning.gw }}",
        'interface': "enp3s0"
    }
    epsm_sr.append(sr)
    dir = make_var_dirs('oth_' + region + '_epsm')
    with open(dir + 'static_routes.yml', 'w', newline='\n') as file:
        yaml.dump({'static_routes': epsm_sr}, file, width=120, sort_keys=False)

#    with open(vars_dir + region + '_psm_static_routes_no_sites.yml', 'w', newline='\n') as file:
#        yaml.dump(sum_networks[region], file)