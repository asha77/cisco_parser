import re

def obtain_software_family(config):
    '''
    Extract software family
    '''

    match = re.search(".*show version\n*Cisco IOS.XE .oftware", config)
    if match:
        return "IOS XE"
    else:
        match = re.search("Cisco IOS Software \[Denali\]", config)
        if match:
            return "IOS XE"
        else:
            match = re.search("(.*)show version\nCisco Nexus Operating System", config)
            if match:
                return "NX-OS"
            else:
                match = re.search("(.*)show version\n*(\s)*Cisco IOS Software", config)
                if match:
                    return "IOS"
                else:
                    return "Not Found"


def devices_summary_output(number, filename, config: object):
    print('| {0:4d} | {1:75s} | {2:25s} | {3:15s} | {4:15s} | {5:20s} | {6:18s} |  {7:10s} | {8:12s} |'.format(
        number + 1,
        filename,
        obtain_hostname(config),
        obtain_mng_ip_from_filename(filename),
        obtain_mng_ip_from_config(config),
        obtain_domain(config),
        obtain_model(config),
        obtain_serial(config),
        obtain_software_version(config))
    )


def fill_devinfo_from_config(config, filename):
    devinfo = [obtain_hostname(config),
               obtain_mng_ip_from_filename(filename),
               obtain_domain(config),
               obtain_model(config),
               obtain_serial(config),
               obtain_software_version(config)]
    return devinfo



def get_interfaces_config(config, curr_path, file, devinfo):
#    global all_interfaces

    int_template = open(curr_path + '\\cisco_interfaces_config.template')
    fsm = textfsm.TextFSM(int_template)
    fsm.Reset()
    interfaces = fsm.ParseText(config)
    int_template.close()

    interfaces_configuration = []
    lastindex = 0
    i = 0
    j = 0
    vlan_id = 0

    interfaces_status = get_int_status(config, curr_path)

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
    # [13] - all vlan from vlan database
    # [14] - vlan id of users vlan
    # [15] - vlan id of iot_toro vlan
    # [16] - vlan id of media_equip vlan
    # [17] - vlan id of off_equip vlan
    # [18] - vlan id of admin vlan
    # [19] - number of UP access interfaces

    if devinfo[2] == "Not set":
        dev_id = devinfo[0]
    else:
        dev_id = devinfo[0] + '.' + devinfo[2]

    interfaces_configuration.append(file)
    interfaces_configuration.append(dev_id)
    interfaces_configuration.append(regparsers.get_type_of_sw_from_hostname(devinfo[0]))
    interfaces_configuration.append(regparsers.get_num_of_physical_ints(interfaces))
    interfaces_configuration.append(regparsers.get_num_of_svi_ints(interfaces))
    interfaces_configuration.append(regparsers.get_num_of_access_int_from_interface_list(interfaces))
    interfaces_configuration.append(regparsers.get_num_of_trunk_int_from_interface_list(interfaces))
    interfaces_configuration.append(regparsers.get_num_of_dot1x_interfaces(interfaces))
    interfaces_configuration.append(regparsers.get_num_of_ints_with_ip(interfaces))
    interfaces_configuration.append(regparsers.get_access_vlan_ids(interfaces))
    interfaces_configuration.append(regparsers.get_native_vlan_ids(interfaces))
    interfaces_configuration.append(regparsers.get_voice_vlan_ids(interfaces))
    interfaces_configuration.append(regparsers.get_trunk_vlan_ids(interfaces))

    vlans_from_config = get_vlan_config(config, curr_path)
    interfaces_configuration.append(vlans_from_config)

    cisco_parser.all_interfaces.append(interfaces)

    """
    fill vlan id for vlans with names   
     - users
     - iot_toro
     - media_equip
     - off_equip
     - admin
    """

    vlan_id = "0"
    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'users':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'iot_toro':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'media_equip':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'off_equip':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")

    vlan_id = "0"

    for j in range(0, len(vlans_from_config)):
        if vlans_from_config[j][1] == 'admin':
            vlan_id = vlans_from_config[j][0]

    if vlan_id != "0":
        interfaces_configuration.append(vlan_id)
    else:
        interfaces_configuration.append("")
    interfaces_configuration.append(regparsers.get_num_of_up_interfaces(interfaces_status))
    return interfaces_configuration


def get_native_vlan_ids(ints):
    '''
    Extract native vlan ids on any port
    Returns set of vlan id values
    '''
    i: int = 0
    vlan_ids = set()
    for i in range(0, len(ints)):
        if ints[i][8] != "":
            vlan_ids.add(ints[i][8])
    return (vlan_ids)


def get_access_vlan_ids(ints):
    '''
    Extract access vlan id numbers
    Returns set of vlan id values
    '''
    i: int = 0
    vlan_ids = set()
    for i in range(0, len(ints)):
        if ints[i][5] == "access":
            if ints[i][4] != "":
                vlan_ids.add(ints[i][4])
    return (vlan_ids)


def get_voice_vlan_ids(ints):
    '''
    Extract voice vlan ids on access ports
    Returns set of vlan id values
    '''
    i: int = 0
    vlan_ids = set()
    for inter in ints:
        if inter['switchport_mode'] == "access":
            if inter['native_vlan'] != "":
                vlan_ids.add(inter['native_vlan'])
    return (vlan_ids)




def neighbours_file_output(all_neighbours):
    cdp_neighbours = open("output\\cdp_nei_output.csv", "a")
#    cdp_neighbours.write("ConfigFile;Source hostname;Source Model;Source Mng IP;Source port;Dest hostname;Dest Model;Dest IP;Dest portn\n")
#   ConfigFile	Source hostname	Source Model	Source Mng IP	Source port	Dest hostname	Dest Model	Dest IP	Dest portn
    for i in range(len(all_neighbours)):
        cdp_neighbours.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1s};{8:1s} \n'.format(
            all_neighbours[i][0],
            all_neighbours[i][1],
            all_neighbours[i][2],
            all_neighbours[i][3],
            all_neighbours[i][4],
            all_neighbours[i][5],
            all_neighbours[i][6],
            all_neighbours[i][7],
            all_neighbours[i][8]
        ))
    cdp_neighbours.close()



def ports_file_output(file, curr_path, config):
    port_template = open(curr_path + '\\cisco_interfaces.template')
    port_fsm = txtfsmparsers.textfsm.TextFSM(port_template)

    resfile = open("output\cparser_output.csv", "a")
#    resfile.write("Configfile;Hostname;Mng IP;Domain Name;Model;Serial;SW Version;Ports avail.;Ports used\n")

    #  проверяем сколько портов активно на коммутаторе
    port_fsm.Reset()
    ports = port_fsm.ParseText(config)

    ports_used = 0
    ports_all = len(ports) - 1
# ToDo: сортировать по именам при выводе в файл!!!
# ToDo: подумать над сравнением двух выводов inventory!!!

    for i in range(0, len(ports) - 1):
        if (ports[i][2] == 'connected'):
            ports_used = ports_used + 1

            # вывод в файл информации по устройстваи и утилизированным портам
    resfile.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1s};{8:1d};{9:1d} \n'.format(
        file,
        regparsers.obtain_hostname(config),
        regparsers.obtain_mng_ip_from_filename(file),
        regparsers.obtain_mng_ip_from_config(config),
        regparsers.obtain_domain(config),
        regparsers.obtain_model(config),
        regparsers.obtain_serial(config),
        " " + regparsers.obtain_software_version(config),
        ports_all,
        ports_used))
    port_template.close()
    resfile.close()



def interfaces_file_output(int_config):
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
    # [13] - all vlan from vlan database
    # [14] - vlan id of users vlan
    # [15] - vlan id of iot_toro vlan
    # [16] - vlan id of media_equip vlan
    # [17] - vlan id of off_equip vlan
    # [18] - vlan id of admin vlan

    f_interfaces = open("output\\interfaces.csv", "a")

    vlans_all = ""

    for i in range(len(int_config[13])):
        vlans_all = vlans_all + int_config[13][i][1] + " " + int_config[13][i][0]
        if (i < len(int_config[13])-1):
            vlans_all = vlans_all + ", "

    f_interfaces.write('{0:1s};{1:1s};{2:1s};{3:4d};{4:4d};{5:4d};{6:4d};{7:4d};{8:4d};{9:1s};{10:1s};{11:1s};{12:1s};{13:1s};{14:1s};{15:1s};{16:1s};{17:1s};{18:1s};{19:3d}\n'.format(
        int_config[0],
        int_config[1],
        int_config[2],
        int_config[3],
        int_config[4],
        int_config[5],
        int_config[6],
        int_config[7],
        int_config[8],
        ', '.join(int_config[9]),
        ', '.join(int_config[10]),
        ', '.join(int_config[11]),
        ', '.join(int_config[12]),
        vlans_all,
        int_config[14],
        int_config[15],
        int_config[16],
        int_config[17],
        int_config[18],
        int_config[19]
        ))
    f_interfaces.close()


def get_cdp_neighbours(config, curr_path, file, devinfo):
    nei_template = open(curr_path + '\\cisco_cdp_nei_ios.template')
    fsm = textfsm.TextFSM(nei_template)

    fsm.Reset()
    neighbours = fsm.ParseText(config)
    all_neighbours = []
    lastindex = 0
    i = 0

    if devinfo[2] == "Not set":
        dev_id = devinfo[0]
    else:
        dev_id = devinfo[0] + '.' + devinfo[2]

    for i in range(lastindex, len(neighbours)):
        all_neighbours.append([])
        all_neighbours[len(all_neighbours) - 1].append(file)        # ConfigFile
        all_neighbours[len(all_neighbours) - 1].append(dev_id)      # Source hostname
        all_neighbours[len(all_neighbours) - 1].append(devinfo[3])  # Source Model
        all_neighbours[len(all_neighbours) - 1].append(devinfo[1])  # Source Mng IP
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][4])    # Source port
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][1])    # Dest hostname
        all_neighbours[len(all_neighbours) - 1].append(regparsers.strip_cisco_from_cdp_name(neighbours[i][3]))   # Dest Model
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][2])    # Dest IP
        all_neighbours[len(all_neighbours) - 1].append(neighbours[i][5])    # Dest portn

    if i != 0:
        lastindex = i + 1

    nei_template.close()
    return all_neighbours



def obtain_stack_members(config):
    match = re.findall("ip address unit (.*)", config)
    if match:
        return len(match)
    else:
        return None


"""
def obtain_secret_settings(config):
    '''
    Extract enable secret settings
    '''

    match = re.search("enable secret (\d) (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not Found"
"""