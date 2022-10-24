import textfsm
from regparsers import *

interfaces = [
    [["Ethernet", "Eth"], "Eth"],
    [["FastEthernet", " FastEthernet", "Fa", "interface FastEthernet"], "Fa"],
    [["GigabitEthernet", "Gi", " GigabitEthernet", "interface GigabitEthernet"], "Gi"],
    [["TenGigabitEthernet", "Te"], "Te"],
    [["Port-channel", "Po"], "Po"],
    [["Serial"], "Ser"],
]


def init_files():
    # инициализация файла c основным выводом
    resfile = open("output\cparser_output.txt", "w")
    resfile.write("Configfile;Hostname;Mng IP;Domain Name;Model;Serial;SW Version;Ports avail.;Ports used\n")
    resfile.close()

    # инициализация файла с портами, на которых есть соседи
    resfile = open("output\\all_nei_output.csv", "w")
    resfile.write("Hostname;Source Model;Source Mng IP;Port\n")
    resfile.close()

    # инициализация файла со связями CDP
    resfile = open("output\\cdp_nei_output.csv", "w")
    resfile.write(
        "ConfigFile;Source hostname;Source Model;Source Mng IP;Source port;Dest hostname;Dest Model;Dest IP;Dest portn\n")
    resfile.close()

    # инициализация файла с перечнем портов, за которыми можно увидеть много MAC-адресов
    resfile = open("output\\many_macs.csv", "w")
    resfile.write("Hostname;VLAN;MAC;PORT\n")
    resfile.close()

    # инициализация файла с конфигурациями интерфейсов
    resfile = open("output\\interfaces.csv", "w")
    resfile.write("File Name;Hostname;Switch type;Num of Ph ports;Num of SVI ints;Num of access ports;Num of trunk ports;Num of access dot1x ports;Num of ints w/IP;Access Vlans;Native Vlans;Voice Vlans;Trunk Vlans\n")
    resfile.close()










def all_neighbours_file_output(all_neighbours):
    all_found_neighbours = open("output\\all_nei_output.csv", "a")
#    all_found_neighbours.write("Hostname;Source Model;Source Mng IP;Source port;Dest hostname;Dest Model;Dest IP;Dest portn\n")

    for i in range(len(all_neighbours)):
        all_found_neighbours.write('{0:1s};{1:1s};{2:1s} \n'.format(
            all_neighbours[i][1],
            all_neighbours[i][2],
            all_neighbours[i][3],
            all_neighbours[i][4],
        ))
        all_found_neighbours.write('{0:1s};{1:1s};{2:1s} \n'.format(
            all_neighbours[i][5],
            all_neighbours[i][6],
            all_neighbours[i][7],
            all_neighbours[i][8],
        ))
    all_found_neighbours.close()


def neighbours_file_output(all_neighbours):
    cdp_neighbours = open("output\\cdp_nei_output.csv", "a")
#    cdp_neighbours.write("ConfigFile;Source hostname;Source Model;Source Mng IP;Source port;Dest hostname;Dest Model;Dest IP;Dest portn\n")

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


def many_macs_file_output(config, curr_path, neighbours, devinfo):
    mac_template = open(curr_path+'\\nrt_macs.template')
    mac_fsm = textfsm.TextFSM(mac_template)

    many_macs = open("output\\many_macs.csv", "a")
#    many_macs.write("Hostname;VLAN;MAC;PORT\n")

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
    mac_template.close()
    many_macs.close()



def ports_file_output(file, curr_path, config):
    port_template = open(curr_path + '\\nrt_interfaces.template')
    port_fsm = textfsm.TextFSM(port_template)

    resfile = open("output\cparser_output.txt", "a")
#    resfile.write("Configfile;Hostname;Mng IP;Domain Name;Model;Serial;SW Version;Ports avail.;Ports used\n")

    #  проверяем сколько портов активно на коммутаторе
    port_fsm.Reset()
    ports = port_fsm.ParseText(config)

    ports_used = 0
    ports_all = len(ports) - 1

    for i in range(0, len(ports) - 1):
        if (ports[i][2] == 'connected'):
            ports_used = ports_used + 1

            # вывод в файл информации по устройстваи и утилизированным портам
    resfile.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1d};{8:1d} \n'.format(
        file,
        obtain_hostname(config),
        obtain_mng_ip_from_config(config),
        obtain_domain(config),
        obtain_model(config),
        obtain_serial(config),
        obtain_software_version(config),
        ports_all,
        ports_used))
    port_template.close()
    resfile.close()



def interfaces_file_output(int_config):
    f_interfaces = open("output\\interfaces.csv", "a")

    for i in range(0, len(int_config)):
        f_interfaces.write('{0:1s};{1:1s};{2:1s};{3:4d};{4:4d};{5:4d};{6:4d};{7:4d};{8:4d};{9:1s};{10:1s};{11:1s};{12:1s} \n'.format(
            int_config[i][0],
            int_config[i][1],
            int_config[i][2],
            int_config[i][3],
            int_config[i][4],
            int_config[i][5],
            int_config[i][6],
            int_config[i][7],
            int_config[i][8],
            ', '.join(int_config[i][9]),
            ', '.join(int_config[i][10]),
            ', '.join(int_config[i][11]),
            ', '.join(int_config[i][12])
        ))
    f_interfaces.close()




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





# Create a function to easily repeat on many lists:
def ListToFormattedString(alist):
    # Each item is right-adjusted, width=3
    formatted_list = ['{:>3}' for item in alist]
    s = ','.join(formatted_list)
    return s.format(*alist)

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
    return "normalize_interface_names failed"


