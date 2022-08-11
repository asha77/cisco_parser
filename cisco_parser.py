import argparse
import os
import pathlib
import re
from typing import List, Any

import textfsm
#from manuf import manuf

interfaces = [
    [["Ethernet", "Eth"], "Eth"],
    [["FastEthernet", " FastEthernet", "Fa", "interface FastEthernet"], "Fa"],
    [["GigabitEthernet", "Gi", " GigabitEthernet", "interface GigabitEthernet"], "Gi"],
    [["TenGigabitEthernet", "Te"], "Te"],
    [["Port-channel", "Po"], "Po"],
    [["Serial"], "Ser"],
]


# Create a function to easily repeat on many lists:
def ListToFormattedString(alist):
    # Each item is right-adjusted, width=3
    formatted_list = ['{:>3}' for item in alist]
    s = ','.join(formatted_list)
    return s.format(*alist)


def obtain_stack_members(config):
    match = re.findall("ip address unit (.*)", config)
    if match:
        return len(match)
    else:
        return None

def obtain_hostname(config):
    '''
    Extract device hostname
    '''

    match = re.search("hostname (.*)", config)
    if match:
        return match.group(1)
    else:
        return "** Not Found! **"


def obtain_model(config):
    '''
    Extract model number
    '''

    match = re.search("Model \wumber\ *: (.*)", config)
    if match:
        return match.group(1)
    else:
        match = re.search("\wisco (.*) \(.*\) \w* (with )*\d+K\/\d+K bytes of memory.", config)
        if match:
            return match.group(1)
        return "** Not Found! **"

def obtain_serial(config):
    '''
    Extract serial number
    '''

    match = re.search("\wystem \werial \wumber\ *: (.*)", config)
    if match:
        return match.group(1)
    else:
        match = re.search("\wrocessor board ID (.*)", config)
        if match:
            return match.group(1)
        return "** Not Found! **"

def obtain_domain(config):
    '''
    Extract domain name
    '''

    match = re.search("ip domain[\s\S]name (.*)", config)
    if match:
        return match.group(1)
    else:
        return "** Not set! **"


def obtain_software_version(config):
    '''
    Extract software version
    '''

    match = re.search("version (.*)", config)
    if match:
        return match.group(1)
    else:
        return "** Not Found! **"


def obtain_mng_ip_from_config(filename):
    '''
    Extract mng ip - TODO: need to rethink - return just first ip on interface !!!!!
    '''

    match = re.search(" ip address ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", filename)
    if match:
        return match.group(1)
    else:
        return " Not Found! "


def check_macs(macs, count):
    mm_macs = []
    for mac_num in range(len(macs)):
        if macs[mac_num][3] != 'CPU' and ('Po' not in macs[mac_num][3]):
# and macs[mac_num][3] != 'Gi0/1' and ('Po' not in macs[mac_num][3]) and macs[mac_num][3] != 'Gi1/0/1' and ('Twe' not in macs[mac_num][3]) and macs[mac_num][3] != 'Gi0/11'
            if ((len([object() for array in macs if array[3] == macs[mac_num][3]])) > (count -1)):
                mm_macs.append(macs[mac_num])
    return mm_macs


def split_interface(interface):
    num_index = interface.index(next(x for x in interface if x.isdigit()))
    str_part = interface[:num_index]
    num_part = interface[num_index:]
    return [str_part, num_part]


def normalize_interface_names(non_norm_int):
    tmp = split_interface(non_norm_int)
    interface_type = tmp[0]
    port = tmp[1]
    for int_types in interfaces:
        for names in int_types:
            for name in names:
                if interface_type in name:
                    return_this = int_types[1] + port
                    return return_this
    return "normalize_interface_names Failed"



def createParser():
    parser = argparse.ArgumentParser(description='Утилита анализа конфигураций коммутаторов Cisco v0.1.')
    parser.add_argument('mode', help='single - process single file | all - process all files in directory')
    parser.add_argument('-r', '--showrun', required=False, help='Specify cisco config file made (show run output)', type=argparse.FileType())
    parser.add_argument('-d', '--configdir', required=False, help='Specify directory with cisco config files', type=pathlib.Path)

    # parser.add_argument('-i', '--showinterfaces', type=argparse.FileType())
    # parser.add_argument('-a', '--showall', action='store_const', const=True)
    # parser.add_argument('-m', '--showmacs', nargs='?', type=argparse.FileType())
    # parser.add_argument('-s', '--skstable', nargs='?', type=argparse.FileType())
    # parser.add_argument('-c', '--commtable', nargs='?', type=argparse.FileType())
    return parser


def main():
#    print("Утилита анализа конфигураций коммутаторов Cisco v0.1.")

    parser = createParser()
    namespace = parser.parse_args()

    if ((namespace.mode == 'single') and (namespace.showrun == None)):
        print("!!! Ошибка: Необходмо указать файл конфигурации Cisco для анализа (полный вывод show running-config)")
        exit()

    if ((namespace.mode == 'single') and (not namespace.showrun == None)):
        cfilename = namespace.showrun

    resfile = open("cparser_output.csv", "w")
    resfile.write("Configfile;Hostname;Mng IP;Domain Name;Model;Serial;SW Version;Ports avail.;Ports used\n")

    cdp_neighbours = open("cdp_nei_output.csv", "w")
    cdp_neighbours.write("ConfigFile;Source hostname;Source Model;Source Mng IP;Source port;Dest hostname;Dest Model;Dest IP;Dest portn\n")

    all_found_neighbours = open("all_nei_output.csv", "w")
    all_found_neighbours.write("Hostname;Source Model;Source Mng IP;Source port;Dest hostname;Dest Model;Dest IP;Dest portn\n")


    many_macs = open("many_macs.csv", "w")
    many_macs.write("Hostname;VLAN;MAC;PORT\n")

    print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------")
    print("|        Hostname        |          Mng IP        |       Domain Name      |              Model     |       Serial     | SW Version | Ports avail. | Ports used |")
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------")

    curr_path = os.path.abspath(os.getcwd())
    if namespace.configdir:
        os.chdir(namespace.configdir)

    nei_template = open(curr_path + '\\nrt_cdp_nei.template')
    fsm = textfsm.TextFSM(nei_template)

    mac_template = open(curr_path + '\\nrt_macs.template')
    mac_fsm = textfsm.TextFSM(mac_template)

    port_template = open(curr_path + '\\nrt_interfaces.template')
    port_fsm = textfsm.TextFSM(port_template)

    all_neighbours = []
    lastindex = 0
    i = 0
    j = 0
    k = 0

    if namespace.mode == 'single':
        config = cfilename.read()
        print('|  {0:20s}  |  {1:20s}  |  {2:20s}  |  {3:20s}  |   {4:12s}   |   {5:7s}  |   {6:10s}  |   {7:10s}  |'.format(obtain_hostname(config),obtain_mng_ip_from_config(config),obtain_software_version(config),obtain_domain(config),obtain_model(config),obtain_serial(config),obtain_software_version(config)))
    else:
        list_of_files = os.listdir(namespace.configdir)
        for file in list_of_files:
            conffile = open(file, "r")
            config = conffile.read()

            #  проверяем сколько портов активно на коммутаторе
            port_fsm.Reset()
            ports = port_fsm.ParseText(config)

            ports_used = 0
            ports_all = len(ports)-1

            for i in range(0, len(ports)-1):
                if (ports[i][2] == 'connected'):
                    ports_used = ports_used + 1

            devinfo = [obtain_hostname(config), obtain_mng_ip_from_config(config), obtain_domain(config), obtain_model(config), obtain_serial(config), obtain_software_version(config)]

            print('|  {0:20s}  |  {1:20s}  |  {2:20s}  |  {3:20s}  |   {4:12s}   |   {5:7s}  |    {6:3d}    |     {7:3d}    |'.format(devinfo[0], devinfo[1], devinfo[2], devinfo[3], devinfo[4], devinfo[5], ports_all, ports_used))
            resfile.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1d};{8:1d} \n'.format(file, devinfo[0], devinfo[1], devinfo[2], devinfo[3], devinfo[4], ' '+devinfo[5], ports_all, ports_used))

            fsm.Reset()
            neighbours = fsm.ParseText(config)

            for i in range(lastindex, len(neighbours)):
                all_neighbours.append([])
                all_neighbours[len(all_neighbours)-1].append(file)
                all_neighbours[len(all_neighbours)-1].append(devinfo[0]+'.'+devinfo[2])
                all_neighbours[len(all_neighbours)-1].append(devinfo[3])
                all_neighbours[len(all_neighbours)-1].append(devinfo[1])
                all_neighbours[len(all_neighbours)-1].append(neighbours[i][4])
                all_neighbours[len(all_neighbours)-1].append(neighbours[i][1])
                all_neighbours[len(all_neighbours)-1].append(neighbours[i][3])
                all_neighbours[len(all_neighbours)-1].append(neighbours[i][2])
                all_neighbours[len(all_neighbours)-1].append(neighbours[i][5])
            if i != 0:
                lastindex=i+1

            mac_fsm.Reset()
            macs = mac_fsm.ParseText(config)

            if len(macs) !=0:
                multimacs = check_macs(macs, 3)
                for j in range(len(multimacs)):
                    nei_found = False
                    for k in range(len(neighbours)):
                        if normalize_interface_names(multimacs[j][3]) == normalize_interface_names(neighbours[k][4]):
                            nei_found = True
                    if not nei_found:
                        many_macs.write('{0:1s};{1:1s};{2:1s};{3:1s} \n'.format(devinfo[0], multimacs[j][2], multimacs[j][0], multimacs[j][3]))
            conffile.close()

        nei_template.close()
        mac_template.close()
        port_template.close()

        resfile.close()
        many_macs.close()

        for i in range(len(all_neighbours)):
            cdp_neighbours.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1s};{8:1s} \n'.format(all_neighbours[i][0], all_neighbours[i][1], all_neighbours[i][2], all_neighbours[i][3], all_neighbours[i][4], all_neighbours[i][5], all_neighbours[i][6], all_neighbours[i][7], all_neighbours[i][8]))
            all_found_neighbours.write('{0:1s};{1:1s};{2:1s} \n'.format(all_neighbours[i][1], all_neighbours[i][2], all_neighbours[i][3]))
            all_found_neighbours.write('{0:1s};{1:1s};{2:1s} \n'.format(all_neighbours[i][5], all_neighbours[i][6], all_neighbours[i][7]))
        cdp_neighbours.close()
        all_found_neighbours.close()


if __name__ == "__main__":
    main()