import os
import txtfsmparsers
from cisco_parser import compliance_result
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.writer.excel import save_workbook
import regparsers


interfaces = [
    [["Ethernet", "Eth"], "Eth"],
    [["FastEthernet", " FastEthernet", "Fa", "interface FastEthernet"], "Fa"],
    [["GigabitEthernet", "Gi", " GigabitEthernet", "interface GigabitEthernet"], "Gi"],
    [["TenGigabitEthernet", "Te"], "Te"],
    [["Port-channel", "Po"], "Po"],
    [["Serial"], "Ser"],
    [["Vlan"], "Vlan"],
    [["Loopback"], "Lo"],
]


def init_files():
    if not os.path.isdir("output"):
        os.mkdir("output")

    # инициализация файла c основным выводом
    resfile = open("output\cparser_output.csv", "w")
    resfile.write("Configfile;Hostname;Mng IP from filename;Mng from config;Domain Name;Family;Model;Serial;OS;SW Version;Ports avail.;Ports used\n")
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
    resfile.write(
        'File Name;Hostname;Domain;Switch type;Num of physical ports;Num of SVI ints;Num of ints w/IP;Num up l3 phys ints;'
        'Num access ints;Num up access ints;Num of trunk interfaces;Num up trunk interf;Num access dot1x ports;'
        'Vlan database;Access Vlans;Trunk Vlans;Proposed vlan list;current native Vlans;current Voice Vlans;'
        'current users vlan id;current iot_toro vlan id;current media_equip vlan id;current off_equip vlan id;'
        'current admin vlan id;'
        '\n')
    resfile.close()

    resfile = open("output\\missed_devices.csv", "w")
    resfile.write('Hostname;Model;IP;\n')
    resfile.close()


def init_comliance_files():
    if not os.path.isdir("output"):
        os.mkdir("output")

    # инициализация файла c основным выводом данных соответствия
    resfile = open("output\compliance_output.csv", "w")
    resfile.write("Num;Filename;Hostname;IP;Domain Name;Model;Serial;SW Version;TimeZone;SNMP ver;No SrcRt;"
                  "Pass Encr;Weak Encr;Strong Encr;SSH Chk;Logging buffered (level);SSH Timeout;Boot Cnf;"
                  "ServCnf;CNSCnf;con0 exec-time;con0 trans pref;"
                    "con0 trans inp;con0 logiauth;vty num;vty exec-time;vty trans pref;vty trans inp;"
                    "vty acc class;vty num;vty exec-time;vty trans pref;vty trans inp;vty acc class;syslog TS;"
                    "proxy arp;log con;log sysl;log fail;log succ;tcp-kp-in;tcp-kp-out;"
                    "inetd;bootp;auth_retr;weak_pass;motd;acc_com;acc_conn;"
                    "acc_exec;acc_system;new model;auth_login;auth_enable;ntp srv;BPDU Guard;"
                    "arp inspection;dhcp snoooping;tacacs server ips;disable aux;port security;"
                    "storm control;SNMP usr enc\n")
    resfile.close()


def all_neighbours_file_output(all_neighbours):
    all_found_neighbours = open("output\\all_nei_output.csv", "a")

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


def all_neighbours_to_file(devices):
    all_neighbours = open("output\\all_nei_output.csv", "a")

    for devs in devices:
        for neighbour in devs['cdp_neighbours']:
            all_neighbours.write('{0:1s};{1:1s};{2:1s} \n'.format(
                neighbour['local_id'],
                neighbour['local_model'],
                neighbour['local_ip_addr'],
                neighbour['local_interface']
            ))

            all_neighbours.write('{0:1s};{1:1s};{2:1s} \n'.format(
                neighbour['remote_id'],
                neighbour['remote_model'],
                neighbour['remote_ip_addr'],
                neighbour['remote_interface']
            ))
    all_neighbours.close()
    return True




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


def connectivity_to_file(devices):
    cdp_neighbours = open("output\\cdp_nei_output.csv", "a")
#    cdp_neighbours.write("ConfigFile;Source hostname;Source Model;Source Mng IP;Source port;Dest hostname;Dest Model;Dest IP;Dest portn\n")
#   ConfigFile	Source hostname	Source Model	Source Mng IP	Source port	Dest hostname	Dest Model	Dest IP	Dest portn

    for dev in devices:
        for neighbour in dev['cdp_neighbours']:
            cdp_neighbours.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1s};{8:1s} \n'.format(
                dev['config_filename'],
                neighbour['local_id'],
                neighbour['local_model'],
                neighbour['local_ip_addr'],
                neighbour['local_interface'],
                neighbour['remote_id'],
                neighbour['remote_model'],
                neighbour['remote_ip_addr'],
                neighbour['remote_interface']
            ))
    cdp_neighbours.close()


def many_macs_file_output(config, curr_path, neighbours, devinfo):
    mac_template = open(curr_path+'\\nrt_macs.template')
    mac_fsm = txtfsmparsers.textfsm.TextFSM(mac_template)

    many_macs = open("output\\many_macs.csv", "a")
#    many_macs.write("Hostname;VLAN;MAC;PORT\n")

    mac_fsm.Reset()
    macs = mac_fsm.ParseText(config)

    if len(macs) !=0:
        multimacs = check_macs(macs, 1)
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



def summary_file_output(devices):
    resfile = open("output\cparser_output.csv", "a")
#    resfile.write("Configfile;Hostname;Mng IP;Domain Name;Model;Serial;SW Version;Ports avail.;Ports used\n")
    # ToDo: сортировать по именам при выводе в файл!!!
    # ToDo: подумать над сравнением двух выводов inventory!!!

    for dev in devices:
        ports_used = 0
        ports_all = 0

        for inter in dev['interfaces']:
            if regparsers.is_physical_interface(inter['int_type']):
                ports_all = ports_all + 1

                if (inter['status'] == 'connected'):
                    ports_used = ports_used + 1

        # вывод в файл информации по устройстваи и утилизированным портам
        resfile.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1s};{8:1s};{9:1s};{10:1d};{11:1d} \n'.format(
            dev['config_filename'],
            dev['hostname'],
            dev['mgmt_ipv4_from_filename'],
            dev['mgmt_v4_autodetect'],
            dev['domain_name'],
            dev['family'],
            dev['model'],
            dev['serial'],
            dev['os'],
            " " +dev['sw_version'],
            ports_all,
            ports_used))

    resfile.close()

    return True


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




def interfaces_to_file(devices):
    f_interfaces = open("output\\interfaces.csv", "a")

    for dev in devices:
        vlans_all = ""
        ports_used = 0
        ports_all = 0

        for inter in dev['interfaces']:
#            vlans_all = vlans_all + int_config[13][i][1] + " " + int_config[13][i][0]

#            if (i < len(int_config[13])-1):
#                vlans_all = vlans_all + ", "

            # count physical interfaces
            if regparsers.is_physical_interface(inter['int_type']):
                ports_all = ports_all + 1
                if (inter['status'] == 'connected'):
                    ports_used = ports_used + 1

        str_vlan_db = '"'
        for key, name in dev['vlans'].items():
            str_vlan_db = str_vlan_db + '{0} {1}, \n'.format(name, key)
        if len(str_vlan_db) > 3:
            str_vlan_db = str_vlan_db[:len(str_vlan_db)-3]
        str_vlan_db = str_vlan_db + '"'


        access_vlans = regparsers.get_access_vlans(dev)
        str_access_vlans = '"'
        for key, name in access_vlans.items():
            str_access_vlans = str_access_vlans + '{0} {1}, \n'.format(name, key)
        if len(str_access_vlans) > 3:
            str_access_vlans = str_access_vlans[:len(str_access_vlans)-3]
        str_access_vlans = str_access_vlans + '"'

        # get dict of specially named vlans with predefined names (802.1x if any)
        # TODO: change txtfsmparsers.do_vlan_analytics() if your vlan names set is different
        vlan_analytics_asis = txtfsmparsers.do_vlan_analytics(dev)

        # propose new ordered set of vlans on device
        native_vlans = regparsers.get_native_vlan_ids(dev['interfaces'])
        if len(native_vlans) == 1:
            vlan_analytics_asis['native'] = int(list(native_vlans)[0])
        elif len(native_vlans) == 0:
            vlan_analytics_asis['native'] = -1
        else:
            vlan_analytics_asis['native'] = int(list(native_vlans)[0])          # TODO: same shit - assertion?

        voice_vlans = regparsers.get_voice_vlan_ids(dev['interfaces'])
        if len(voice_vlans) == 1:
            vlan_analytics_asis['voice'] = int(list(voice_vlans)[0])
        elif len(voice_vlans) == 0:
            vlan_analytics_asis['voice'] = -1
        else:
            vlan_analytics_asis['voice'] = int(list(voice_vlans)[0])          # TODO: same shit - assertion?

        proposed_vlans = proposed_vlans_list(access_vlans)

        str_proposed_vlans = '"'
        for key, name in proposed_vlans.items():
            str_proposed_vlans = str_proposed_vlans + '{0} {1}, \n'.format(name, key)
        if len(str_proposed_vlans) > 3:
            str_proposed_vlans = str_proposed_vlans[:len(str_proposed_vlans)-3]
        str_proposed_vlans = str_proposed_vlans + '"'

        f_interfaces.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1d};{5:1d};{6:1d};{7:1d};{8:1d};{9:1d};{10:1d};{11:1d};{12:1d};{13:1s};{14:1s};{15:1s};{16:1s};{17:1s};{18:1s};{19:1s};{20:1s};{21:1s};{22:1s};{23:1s}\n'.format(
            dev['config_filename'],                                                 # [0] filename
            dev['hostname'],                                                        # [1] hostname
            dev['domain_name'],                                                     # [2] domain name
            '',                                     # TODO: check device type here  # [3] type of switch (asw, dsw, csw, undefined)
            regparsers.get_number_of_physical_ints(dev['interfaces']),              # [4] number of physical interfaces
            regparsers.get_number_of_svis(dev['interfaces']),                       # [5] number of SVI interfaces
            regparsers.get_number_of_ints_with_ip(dev['interfaces']),               # [6] number of interfaces with ip addresses
            regparsers.get_number_of_connected_l3_ints(dev['interfaces']),          # [7] number of connected L3 interfaces
            regparsers.get_number_of_acc_int(dev['interfaces']),                    # [8] number of access interfaces
            regparsers.get_number_of_connected_access_ints(dev['interfaces']),      # [9] number of connected access interfaces
            regparsers.get_number_of_trunk_int(dev['interfaces']),                  # [10] number of trunk interfaces
            regparsers.get_number_of_connected_trunk_ints(dev['interfaces']),       # [11] number of connected trunk interfaces
            regparsers.get_number_of_dot1x_ints(dev['interfaces']),                 # [12] number of access ports with dot1x
            str_vlan_db,                                                            # [13] all vlan from vlan database
            str_access_vlans,                                                       # [14] list of access vlan(s)
            ', '.join(regparsers.get_all_vlan_ids_from_trunk(dev['interfaces'])),   # [15] list of vlan(s) on trunks
            str_proposed_vlans,                                                     # [16] list of proposed vlans to be in database and on trunk
            ', '.join(native_vlans),                                                # [17] list of native vlan(s)
            ', '.join(voice_vlans),                                                 # [18] list of voice vlan(s)
            vlan_id_to_str(vlan_analytics_asis['users']),                           # [19] vlan id of 'users' vlan
            vlan_id_to_str(vlan_analytics_asis['iot_toro']),                        # [20] vlan id of 'iot_toro' vlan
            vlan_id_to_str(vlan_analytics_asis['media_equip']),                     # [21] vlan id of media_equip vlan
            vlan_id_to_str(vlan_analytics_asis['off_equip']),                       # [22] vlan id of off_equip vlan
            vlan_id_to_str(vlan_analytics_asis['admin']),                           # [23] vlan id of admin vlan
        ))

    f_interfaces.close()
    return True


def vlan_id_to_str(id):
    if id == -1:
        return ''
    else:
        return '{0}'.format(id)


def proposed_vlans_list(current_vlans):
    proposed_vlans = {}

    # current = {id: 'name'}

    # TODO: subject to change !!!!
    # куст 007596
    # proposed = {id: 'name'}
    proposed_vlans[1000] = 'native'
    proposed_vlans[254] = 'mgmt'
    proposed_vlans[29] = 'users'
    proposed_vlans[3983] = 'off_equip'
    proposed_vlans[9999] = 'media_equip'

    # dictionary of correct vlan names for proposed list
    nice_dictionary = {150: 'uaz.ent.mgmt.ap_wifi', 8: 'ASUTP_GLZ', 56: 'Pritok', 27: 'ohrana_uaz', 397: 'scada_dop'}

    excluded_keys = [1, 3960, 3986, 13, 3990, -1, 3982]

    for curr_key in list(current_vlans.keys()):
        if curr_key not in list(proposed_vlans.keys()) and curr_key not in excluded_keys:
            if current_vlans[curr_key] == '':
                if curr_key in nice_dictionary.keys():
                    proposed_vlans[curr_key] = nice_dictionary[curr_key]
                else:
                    proposed_vlans[curr_key] = 'not set'
            else:
                if curr_key in nice_dictionary.keys():
                    proposed_vlans[curr_key] = nice_dictionary[curr_key]
                else:
                    proposed_vlans[curr_key] = current_vlans[curr_key]
    return proposed_vlans


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
    if non_norm_int == 'Drop':
        return 'Failed'

    tmp = split_interface(non_norm_int)
    interface_type = tmp[0]
    port = tmp[1]
    for int_types in interfaces:
        for names in int_types:
            for name in names:
                if interface_type in name:
                    return_this = int_types[1] + port
                    return return_this
    return 'Failed'


def check_compliance(num, file, curr_path, config):
    dev_access = txtfsmparsers.get_access_config(config, curr_path)
    dev_con_access = txtfsmparsers.get_con_access_config(config, curr_path)

    # ToDo: transform to tuple values?
    compliance_result.append([])

    compliance_result[len(compliance_result) - 1] = [
    num,                                # 0
    file,                               # 1
    regparsers.obtain_hostname(config),            # 2
    regparsers.obtain_mng_ip_from_config(config),  # 3
    regparsers.obtain_domain(config),              # 4
    regparsers.obtain_model(config),               # 5
    regparsers.obtain_serial(config),              # 6
    " " + regparsers.obtain_software_version(config),  # 7
    regparsers.obtain_timezone(config),            # 8
    regparsers.obtain_snmp_version(config),        # 9!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    regparsers.check_source_route(config),         # 10
    regparsers.check_service_password_encryption(config), # 11
    regparsers.check_weak_enable_password_encryption(config), # 12
    regparsers.check_enable_password_encryption_method(config),  # 13
    regparsers.check_ssh_version(config),          # 14
    regparsers.check_logging_buffered(config),     # 15
    regparsers.check_ssh_timeout(config),          # 16
    regparsers.check_boot_network(config),         # 17
    regparsers.check_service_config(config),       # 18
    regparsers.check_cns_config(config),           # 19
    dev_con_access[0][1],               # 20 con0 exec-time
    dev_con_access[0][2],               # 21 con0 transport preferred
    dev_con_access[0][3],               # 22 con0 trans inp
    dev_con_access[0][4],               # 23 con0 logiauth
    dev_access[0][0],                   # 24 vty num
    dev_access[0][1],                   # 25 vty exec-time
    dev_access[0][2],                   # 26 vty trans pref
    dev_access[0][3],                   # 27 vty trans inp
    dev_access[0][4],                   # 28 vty acc class
    dev_access[1][0],                   # 29 vty num
    dev_access[1][1],                   # 30 vty exec-time
    dev_access[1][2],                   # 31 vty trans pref
    dev_access[1][3],                   # 32 vty trans inp
    dev_access[1][4],                   # 33 vty acc class
    regparsers.check_syslog_timestamp(config),     # 34
    regparsers.check_proxy_arp(config),            # 35
    regparsers.check_logging_console(config),      # 36
    regparsers.check_logging_syslog(config),       # 37
    regparsers.check_log_failures(config),         # 38
    regparsers.check_log_success(config),          # 39
    regparsers.check_tcp_keepalives_in(config),    # 40
    regparsers.check_tcp_keepalives_out(config),   # 41
    regparsers.check_inetd_disable(config),        # 42
    regparsers.check_bootp_disable(config),        # 43
    regparsers.check_authentication_retries(config),   # 44
    regparsers.check_weak_local_users_passwords(config), # 45
    regparsers.check_motd_banner(config),          # 46
    regparsers.check_accounting_commands(config),  # 47
    regparsers.check_connection_accounting(config),    # 48
    regparsers.check_exec_commands_accounting(config), #49
    regparsers.check_system_accounting(config),        # 50
    regparsers.check_new_model(config),            # 51
    regparsers.check_auth_login(config),           # 52
    regparsers.check_auth_enable(config),          # 53
    regparsers.get_ntp_servers(config),            # 54
    regparsers.check_bpduguard(config),            # 55
    regparsers.check_iparp_inspect(config),        # 56
    regparsers.check_dhcp_snooping(config),        # 57
    txtfsmparsers.get_tacacs_server_ips(config, curr_path),   #58
    regparsers.check_aux(config),                  # 59
    regparsers.check_portsecurity(config),         # 60
    regparsers.check_stormcontrol(config),         # 61
    regparsers.obtain_snmp_user_encr(config),      # 62
    regparsers.check_snmpv3_authencr(config),      # 63
    regparsers.check_snmpv2_ACL(config)            # 64
]


def write_compliance():
    # вывод в файл compliance информации
    resfile = open("output\compliance_output.csv", "a")

    print('| {0:4d} | {1:75s} | {2:25s} | {3:15s} | {4:20s} | {5:18s} | {6:10s} | {7:12s} | {8:12s} | {9:10s} | {10:10s} | {11:10s} | {12:10s} | {13:12s} | {14:6s} | {15:25s} | {16:12s} | {17:6s} | {18:6s} | {19:6s} | {20:14s} | {21:14s} | {22:14s} | {23:12s} | {24:8s} | {25:14s} | {26:14s} | {27:12s} | {28:12s} |{29:8s} | {30:14s} | {31:14s} | {32:12s} | {33:12s} | {34:10s} | {35:10s} | {36:10s} | {37:10s} | {38:10s} | {39:10s} | {40:10s} | {41:10s} | {42:10s} | {43:10s} | {44:10s} | {45:10s} | {46:10s} | {47:10s} | {48:10s} | {49:10s} | {50:10s} | {51:10s} | {52:34s} | {53:34s} | {54:65s} | {55:10s} | {56:10s} | {57:10s} | {58:40s} | {59:10s} | {60:10s} | {61:10s} | {62:10s} | {63:10s} | {64:10s} |'.format(*compliance_result[len(compliance_result) - 1]))
#    resfile.write('{0:4d};{1:75s};{2:25s};{3:15s};{4:20s};{5:18s};{6:10s};{7:12s};{8:12s};{9:10s};{10:10s};{11:10s};{12:10s};{13:12s};{14:6s};{15:25s};{16:12s};{17:6s};{18:6s};{19:6s};{20:14s};{21:14s};{22:14s};{23:12s};{24:8s};{25:14s};{26:14s};{27:12s};{28:12s};{29:8s};{30:14s};{31:14s};{32:12s};{33:12s};{34:10s};{35:10s};{36:10s};{37:10s};{38:10s};{39:10s};{40:10s};{41:10s};{42:10s};{43:10s};{44:10s};{45:10s};{46:10s};{47:10s};{48:10s};{49:10s};{50:10s};{51:10s};{52:29s};{53:30s};{54:65s};{55:10s};{56:10s};{57:10s};{58:40s};{59:10s};{60:10s};{61:10s};{62:10s}\n'.format(*compliance_result[len(compliance_result) - 1]))
    resfile.write('{0:4d};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1s};{8:1s};{9:1s};{10:1s};{11:1s};{12:1s};{13:1s};{14:1s};{15:1s};{16:1s};{17:1s};{18:1s};{19:1s};{20:1s};{21:1s};{22:1s};{23:1s};{24:1s};{25:1s};{26:1s};{27:1s};{28:1s};{29:1s};{30:1s};{31:1s};{32:1s};{33:1s};{34:1s};{35:1s};{36:1s};{37:1s};{38:1s};{39:1s};{40:1s};{41:1s};{42:1s};{43:1s};{44:1s};{45:1s};{46:1s};{47:1s};{48:1s};{49:1s};{50:1s};{51:1s};{52:1s};{53:1s};{54:1s};{55:1s};{56:1s};{57:1s};{58:1s};{59:1s};{60:1s};{61:1s};{62:1s};{63:1s};{63:1s}\n'.format(*compliance_result[len(compliance_result) - 1]))
    resfile.close()


def write_xls_report(curr_path, ):
    file_name = os.path.join(curr_path, 'report_templates')
    file_name = os.path.join(file_name, 'compliance_report_template.xlsx')

    compliance_report = load_workbook(filename=file_name)
    sheet_ranges = compliance_report['Compl_report']

    # clearing data if any...
    for row in sheet_ranges['F12:F70']:
        for cell in row:
            cell.value = ""

    sheet_ranges['C3'].value = str(datetime.now())
    # starting to fill in compliance report
    # counting devices without auth on con 0
    i = 0
    for cresult in compliance_result:
        if cresult[23] == "Not set":
            sheet_ranges['F12'].value = sheet_ranges['F12'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F12'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F12'].value

    # counting devices without input acl on vtu 0 4
    i = 0
    for cresult in compliance_result:
        if cresult[28] == "Not set":
            sheet_ranges['F13'].value = sheet_ranges['F13'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F13'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F13'].value

    # counting devices without input acl on vtu 5 15
    i = 0
    for cresult in compliance_result:
        if cresult[33] == "Not set":
            sheet_ranges['F14'].value = sheet_ranges['F14'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F14'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F14'].value

    # counting devices without aaa-new model
    i = 0
    for cresult in compliance_result:
        if cresult[51] == "Not set":
            sheet_ranges['F15'].value = sheet_ranges['F15'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F15'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F15'].value

    # counting devices aaa accounting commands
    i = 0
    for cresult in compliance_result:
        if cresult[47] == "Not set":
            sheet_ranges['F16'].value = sheet_ranges['F16'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F16'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F16'].value

    # counting devices aaa accounting connections
    i = 0
    for cresult in compliance_result:
        if cresult[48] == "Not set":
            sheet_ranges['F17'].value = sheet_ranges['F17'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F17'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F17'].value

    # counting devices aaa accounting exec
    i = 0
    for cresult in compliance_result:
        if cresult[49] == "Not set":
            sheet_ranges['F18'].value = sheet_ranges['F18'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F18'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F18'].value

    # counting devices aaa accounting system
    i = 0
    for cresult in compliance_result:
        if cresult[50] == "Not set":
            sheet_ranges['F19'].value = sheet_ranges['F19'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F19'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F19'].value

    # counting devices aaa authentication login
    i = 0
    for cresult in compliance_result:
        if cresult[52] == "Not set":
            sheet_ranges['F20'].value = sheet_ranges['F20'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F20'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F20'].value

    # counting devices aaa authentication enable
    i = 0
    for cresult in compliance_result:
        if cresult[53] == "Not set":
            sheet_ranges['F21'].value = sheet_ranges['F21'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F21'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F21'].value

    # counting devices with enabled aux
    i = 0
    for cresult in compliance_result:
        if cresult[59] == "Not set":
            sheet_ranges['F22'].value = sheet_ranges['F22'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F22'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F22'].value

    # counting devices with con 0 exec timeout not set
    i = 0
    for cresult in compliance_result:
        if cresult[20] == "Not set":
            sheet_ranges['F23'].value = sheet_ranges['F23'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
        else:
            if int(cresult[20]) > 10:
                sheet_ranges['F23'].value = sheet_ranges['F23'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
                i = i + 1
    sheet_ranges['F23'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F23'].value

    # counting devices with con 0  transport preferred none not set
    i = 0
    for cresult in compliance_result:
        if cresult[21] == "Not set":
            sheet_ranges['F24'].value = sheet_ranges['F24'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F24'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F24'].value

    # counting devices without vty 0 4 transport input ssh
    i = 0
    for cresult in compliance_result:
        if ((cresult[27] == "Not set") or (not cresult[27].find('telnet') == -1)):
            sheet_ranges['F25'].value = sheet_ranges['F25'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F25'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F25'].value

    # counting devices without vty 0 4 exec-timeout 10
    i = 0
    for cresult in compliance_result:
        if cresult[25] == "Not set":
            sheet_ranges['F26'].value = sheet_ranges['F26'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
        else:
            if int(cresult[25]) > 10:
                sheet_ranges['F26'].value = sheet_ranges['F26'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
                i = i + 1
    sheet_ranges['F26'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F26'].value

    # counting devices without vty 0 4 transport preferred none
    i = 0
    for cresult in compliance_result:
        if cresult[26] == "Not set":
            sheet_ranges['F27'].value = sheet_ranges['F27'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F27'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F27'].value

    # counting devices without vty 0 4  ip access-class
    i = 0
    for cresult in compliance_result:
        if cresult[28] == "Not set":
            sheet_ranges['F28'].value = sheet_ranges['F28'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F28'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F28'].value

    # counting devices without vty 5 15 transport input ssh
    i = 0
    for cresult in compliance_result:
        if ((cresult[32] == "Not set") or (not cresult[32].find('telnet') == -1)):
            sheet_ranges['F29'].value = sheet_ranges['F29'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F29'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F29'].value

    # counting devices without vty 5 15 exec-timeout 10
    i = 0
    for cresult in compliance_result:
        if cresult[30] == "Not set":
            sheet_ranges['F30'].value = sheet_ranges['F30'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
        else:
            if int(cresult[30]) > 10:
                sheet_ranges['F30'].value = sheet_ranges['F30'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
                i = i + 1
    sheet_ranges['F30'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F30'].value

    # counting devices without vty 5 15 transport preferred none
    i = 0
    for cresult in compliance_result:
        if cresult[31] == "Not set":
            sheet_ranges['F31'].value = sheet_ranges['F31'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F31'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F31'].value

    # counting devices without vty 5 15 ip access-class
    i = 0
    for cresult in compliance_result:
        if cresult[33] == "Not set":
            sheet_ranges['F32'].value = sheet_ranges['F32'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F32'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F32'].value

    # counting devices without motd
    i = 0
    for cresult in compliance_result:
        if cresult[46] == "Not set":
            sheet_ranges['F33'].value = sheet_ranges['F33'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F33'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F33'].value

    # counting devices without service password-encryption
    i = 0
    for cresult in compliance_result:
        if cresult[11] == "Not set":
            sheet_ranges['F34'].value = sheet_ranges['F34'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F34'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F34'].value

    # counting devices with enable password or weak enable secret encryption
    i = 0
    for cresult in compliance_result:
        if not cresult[12] == "Not set":
            sheet_ranges['F35'].value = sheet_ranges['F35'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
        else:
            if not cresult[13].find('Fail') == -1:
                sheet_ranges['F35'].value = sheet_ranges['F35'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
                i = i + 1
    sheet_ranges['F35'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F35'].value

    # check_service_password_encryption(config),  # 11
    # check_weak_enable_password_encryption(config),  # 12
    # check_enable_password_encryption_method(config),  # 13
    # check_weak_local_users_passwords(config),  # 45

    # counting devices without username <user> secret
    i = 0
    for cresult in compliance_result:
        if (not cresult[45].find('Fail') == -1):
            sheet_ranges['F36'].value = sheet_ranges['F36'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F36'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F36'].value

    # obtain_snmp_version(config),  # 9
    # obtain_snmp_user_encr(config),  # 62
    # check_snmpv3_authencr(config),  # 63
    # check_snmpv2_ACL(config)  # 64

    # counting devices with snmp version 3 without priv

    i = 0
    for cresult in compliance_result:
        if cresult[9] == "v3":
            if not cresult[63] == "priv":
                sheet_ranges['F37'].value = sheet_ranges['F37'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
                i = i + 1
    sheet_ranges['F37'].value = "Настройки SNMPv3 без шифрования найдены на " + str(i) +" устройствах:\n" + sheet_ranges['F37'].value

    # counting devices with correct snmp v2 with ACL
    i = 0
    for cresult in compliance_result:
        if cresult[9] == 'v2c':
            if not cresult[64] == "":
                sheet_ranges['F38'].value = sheet_ranges['F38'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
                i = i + 1
    sheet_ranges['F38'].value = "Настройки SNMPv2 без ACL найдены на " + str(i) +" устройствах:\n" + sheet_ranges['F38'].value

    # counting devices with SNMP v3 users with encryption
    i = 0
    for cresult in compliance_result:
        if cresult[9] == "v3":
            if cresult[62] == "Fail":
                sheet_ranges['F39'].value = sheet_ranges['F39'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
                i = i + 1
    sheet_ranges['F39'].value = "Настройки пользователей SNMPv3 без шифрования найдены на " + str(i) +" устройствах:\n" + sheet_ranges['F39'].value

    # counting devices without domain name
    i = 0
    for cresult in compliance_result:
        if cresult[4] == "Not set":
            sheet_ranges['F40'].value = sheet_ranges['F40'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F40'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F40'].value

    # counting devices without timezone
    i = 0
    for cresult in compliance_result:
        if cresult[8] == "Not set":
            sheet_ranges['F41'].value = sheet_ranges['F41'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F41'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F41'].value

    # counting devices without ssh version 2
    i = 0
    for cresult in compliance_result:
        if cresult[14] == "Not set":
            sheet_ranges['F42'].value = sheet_ranges['F42'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F42'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F42'].value

    # counting devices without ssh timeout
    i = 0
    for cresult in compliance_result:
        if cresult[16] == "Not set":
            sheet_ranges['F43'].value = sheet_ranges['F43'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F43'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F43'].value

    # counting devices without no boot network
    i = 0
    for cresult in compliance_result:
        if cresult[17] == "Not set":
            sheet_ranges['F44'].value = sheet_ranges['F44'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F44'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F44'].value

    # counting devices without no boot network
    i = 0
    for cresult in compliance_result:
        if cresult[18] == "Not set":
            sheet_ranges['F45'].value = sheet_ranges['F45'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F45'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F45'].value

    # counting devices without service tcp-keepalives-in
    i = 0
    for cresult in compliance_result:
        if cresult[40] == "Not set":
            sheet_ranges['F46'].value = sheet_ranges['F46'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F46'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F46'].value

    # counting devices without service tcp-keepalives-out
    i = 0
    for cresult in compliance_result:
        if cresult[41] == "Not set":
            sheet_ranges['F47'].value = sheet_ranges['F47'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F47'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F47'].value

    # counting devices without no ip inetd
    i = 0
    for cresult in compliance_result:
        if cresult[42] == "Not set":
            sheet_ranges['F48'].value = sheet_ranges['F48'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F48'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F48'].value

    # counting devices without no ip bootp server
    i = 0
    for cresult in compliance_result:
        if cresult[43] == "Not set":
            sheet_ranges['F49'].value = sheet_ranges['F49'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F49'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F49'].value

    # counting devices without ip ssh authentication-retries
    i = 0
    for cresult in compliance_result:
        if cresult[44] == "Not set":
            sheet_ranges['F50'].value = sheet_ranges['F50'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F50'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F50'].value

    # counting devices with service pad
    sheet_ranges['F51'].value = "please check pad manually!!! It is for routers mainly!!!"

    # counting devices with cdp
    sheet_ranges['F52'].value = "please check cdp manually!!! Recomendations with caution!!!"

    # counting devices without logging buffered
    i = 0
    for cresult in compliance_result:
        if cresult[15] == "Not set":
            sheet_ranges['F53'].value = sheet_ranges['F53'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F53'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F53'].value

    # counting devices without logging console critical
    i = 0
    for cresult in compliance_result:
        if cresult[36] == "Not set":
            sheet_ranges['F54'].value = sheet_ranges['F54'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F54'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F54'].value

    # counting devices without logging syslog informational
    i = 0
    for cresult in compliance_result:
        if cresult[37] == "Not set":
            sheet_ranges['F55'].value = sheet_ranges['F55'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F55'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F55'].value

    # counting devices without login on-failure log
    i = 0
    for cresult in compliance_result:
        if cresult[38] == "Not set":
            sheet_ranges['F56'].value = sheet_ranges['F56'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F56'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F56'].value

    # counting devices without login on-success log
    i = 0
    for cresult in compliance_result:
        if cresult[39] == "Not set":
            sheet_ranges['F57'].value = sheet_ranges['F57'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F57'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F57'].value

    # counting devices without service timestamps debug datetime
    i = 0
    for cresult in compliance_result:
        if cresult[34] == "Not set":
            sheet_ranges['F58'].value = sheet_ranges['F58'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F58'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F58'].value

    # counting devices without ntp settings
    i = 0
    for cresult in compliance_result:
        if cresult[54] == "Not set":
            sheet_ranges['F59'].value = sheet_ranges['F59'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F59'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F59'].value

    # counting devices without no ip proxy arp
    i = 0
    for cresult in compliance_result:
        if cresult[35] == "Not set":
            sheet_ranges['F60'].value = sheet_ranges['F60'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F60'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F60'].value

    # counting devices with uRPF
    sheet_ranges['F61'].value = "please check uPRPF manually!!! Recomendations with caution!!!"

    # counting devices with OSPF authentification manually
    sheet_ranges['F62'].value = "please check OSPF authentification manually!!! Recomendations with caution!!!"

    # counting devices with BGP authentification manually
    sheet_ranges['F63'].value = "please check BGP authentification manually!!! Recomendations with caution!!!"

    # counting devices with ip source routing enabled
    i = 0
    for cresult in compliance_result:
        if cresult[10] == "Not set":
            sheet_ranges['F64'].value = sheet_ranges['F64'].value + cresult[2] + " " + cresult[3] + " " + cresult[6] + "\n"
            i = i + 1
    sheet_ranges['F64'].value = "Найдено на " + str(i) +" устройствах:\n" + sheet_ranges['F64'].value

    save_workbook(compliance_report, 'output\\compliance_report.xlsx')
    compliance_report.close()


def find_missed_devices():
    devs = []
    cdps = []
    missed_devices = []
    dname = ''

    with open("output\\cparser_output.csv") as f_cparser:
        for line in f_cparser.readlines():
            devs.append(line.split(";"))

    with open("output\\all_nei_output.csv") as f_allnei:
        for line in f_allnei.readlines():
            cdps.append(line.split(";"))

    for cdp in cdps:
        found = False
        if cdp[0] == "Hostname":
            continue

        for dev in devs:
            if found:
                break

            if dev[0] == "Hostname":
                continue

            if dev[4] == "Not set":
                dname = dev[1]
            else:
                dname = dev[1] + '.' + dev[4]

            if cdp[0] == dname:
                found = True

        if not found:  # cdp entry not found in configurations -> add to missed
            if cdp not in missed_devices:
                missed_devices.append(cdp)
    return missed_devices


def missed_devices_file_output(missed_devices):
    f_missed = open("output\\missed_devices.csv", "a")
    for i in range(len(missed_devices)):
        f_missed.write('{0:1s};{1:1s};{2:1s}'.format(
            missed_devices[i][0],
            missed_devices[i][1],
            missed_devices[i][2],
        ))
    f_missed.close()
