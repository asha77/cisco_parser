import textfsm
from regparsers import *

def get_cdp_neighbours(config, curr_path, file, devinfo):
    nei_template = open(curr_path + '\\nrt_cdp_nei.template')
    fsm = textfsm.TextFSM(nei_template)

    fsm.Reset()
    neighbours = fsm.ParseText(config)
    all_neighbours = []
    lastindex = 0
    i = 0

    for i in range(lastindex, len(neighbours)):
        all_neighbours.append([])
        all_neighbours[len(all_neighbours) - 1].append(file)
        all_neighbours[len(all_neighbours) - 1].append(devinfo[0] + '.' + devinfo[2])
        all_neighbours[len(all_neighbours) - 1].append(devinfo[3])
        all_neighbours[len(all_neighbours) - 1].append(devinfo[1])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][4])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][1])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][3])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][2])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][5])
    if i != 0:
        lastindex = i + 1

    nei_template.close()

    return all_neighbours


def get_vrfs(config, curr_path, file, devinfo):
    nei_template = open(curr_path + '\\nrt_cdp_nei.template')
    fsm = textfsm.TextFSM(nei_template)

    fsm.Reset()
    neighbours = fsm.ParseText(config)
    all_neighbours = []
    lastindex = 0
    i = 0

    for i in range(lastindex, len(neighbours)):
        all_neighbours.append([])
        all_neighbours[len(all_neighbours) - 1].append(file)
        all_neighbours[len(all_neighbours) - 1].append(devinfo[0] + '.' + devinfo[2])
        all_neighbours[len(all_neighbours) - 1].append(devinfo[3])
        all_neighbours[len(all_neighbours) - 1].append(devinfo[1])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][4])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][1])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][3])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][2])
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][5])
    if i != 0:
        lastindex = i + 1

    nei_template.close()

    return all_neighbours



def get_interfaces_config(config, curr_path, file, devinfo):
    interfaces = []
    nei_template = open(curr_path + '\\nrt_interfaces_config.template')
    fsm = textfsm.TextFSM(nei_template)
    fsm.Reset()
    interfaces = fsm.ParseText(config)

    interfaces_configuration = []
    lastindex = 0
    i = 0

    # interfaces_configuration
    # [0] - file
    # [1] - hostname
    # [2] - type of switch (asw, dsw, csw, undefined)
    # [3] - number of physical interfaces
    # [4] - number of SVI interfaces
    # [5] - number of access interfaces
    # [6] - number of trunk interfaces
    # [7] - number of access ports with dot1x
    # [8] - number of ip addresses
    # [9] - list of access vlan(s)
    # [10] - list of native vlan(s)
    # [11] - list of voice vlan(s)
    # [12] - list of vlan(s) on trunks

    interfaces_configuration.append([])
    interfaces_configuration[i].append(file)
    interfaces_configuration[i].append(devinfo[0])
    interfaces_configuration[i].append(get_type_of_sw_from_hostname(devinfo[0]))
    interfaces_configuration[i].append(get_num_of_physical_ints(interfaces))
    interfaces_configuration[i].append(get_num_of_svi_ints(interfaces))
    interfaces_configuration[i].append(get_num_of_access_int_from_interface_list(interfaces))
    interfaces_configuration[i].append(get_num_of_trunk_int_from_interface_list(interfaces))
    interfaces_configuration[i].append(get_num_of_dot1x_interfaces(interfaces))
    interfaces_configuration[i].append(get_num_of_ints_with_ip(interfaces))
    interfaces_configuration[i].append(get_access_vlan_ids(interfaces))
    interfaces_configuration[i].append(get_native_vlan_ids(interfaces))
    interfaces_configuration[i].append(get_voice_vlan_ids(interfaces))
    interfaces_configuration[i].append(get_trunk_vlan_ids(interfaces))

    nei_template.close()
    return interfaces_configuration

