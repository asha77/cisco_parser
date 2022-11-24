import textfsm
import os
from regparsers import *
from txtfsmparsers import *


interfaces = [
    [["Ethernet", "Eth"], "Eth"],
    [["FastEthernet", " FastEthernet", "Fa", "interface FastEthernet"], "Fa"],
    [["GigabitEthernet", "Gi", " GigabitEthernet", "interface GigabitEthernet"], "Gi"],
    [["TenGigabitEthernet", "Te"], "Te"],
    [["Port-channel", "Po"], "Po"],
    [["Serial"], "Ser"],
]


def init_files():
    if not os.path.isdir("output"):
        os.mkdir("output")

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
    resfile.write(
        'File Name;Hostname;Switch type;Num of Ph ports;Num of SVI ints;Num of access ports;Num of trunk ports;Num of '
        'access dot1x ports;Num of ints w/IP;Access Vlans;Native Vlans;Voice Vlans;Trunk Vlans;Vlan database;users '
        'id;iot_toro id;media_equip id;off_equip id;admin id;\n')
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
                    "proxy arp;log con;log sysl;log fail;log succ;tcp-kp-in;tcp-kp-out "
                    "inetd;bootp;auth_retr;weak_pass;motd;acc_com;acc_conn;"
                    "acc_exec;acc_system;new model;auth_login;auth_enable;ntp srv\n")
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

    f_interfaces.write('{0:1s};{1:1s};{2:1s};{3:4d};{4:4d};{5:4d};{6:4d};{7:4d};{8:4d};{9:1s};{10:1s};{11:1s};{12:1s};{13:1s};{14:1s};{15:1s};{16:1s};{17:1s};{18:1s}\n'.format(
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
        int_config[18]
        ))
    f_interfaces.close()

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



def check_compliance(num, file, curr_path, config):
    dev_access = get_access_config(config, curr_path)
    dev_con_access = get_con_access_config(config, curr_path)

    # вывод в файл compliance информации
    resfile = open("output\compliance_output.csv", "a")

    # def obtain_timezone(config):
    # def obtain_secret_settings(config):
    # def obtain_snmp_version(config):
    # def check_source_route(config):
    # def check_service_password_encryption(config):
    # def check_weak_service_password_encryption(config):
    # def check_md5_service_password_encryption(config):

    # def check_syslog_timestamp(config)
    # def check_proxy_arp(config)
    # def check_logging_console(config)
    # def check_logging_syslog(config)
    # def check_log_failures(config)
    # def check_log_success(config)
    # def check_tcp_keepalives_in(config)
    # def check_tcp_keepalives_out(config)
    # def check_inetd_disable(config)
    # def check_bootp_disable(config)
    # def check_authentication_retries(config)
    # def check_weak_local_users_passwords(config)
    # def check_motd_banner(config)
    # def check_accounting_commands(config)
    # def check_connection_accounting(config)
    # def check_exec_commands_accounting(config)
    # def check_system_accounting(config)
    # def check_new_model(config)
    # def check_auth_login(config)
    # def check_auth_enable(config):
    # def get_ntp_servers(config)

    print('| {0:4d} | {1:75s} | {2:25s} | {3:15s} | {4:20s} | {5:18s} | {6:10s} | {7:12s} | {8:12s} | {9:10s} | {10:10s} | {11:10s} | {12:10s} | {13:12s} | {14:6s} | {15:25s} | {16:12s} | {17:6s} | {18:6s} | {19:6s} | {20:14s} | {21:14s} | {22:14s} | {23:12s} | {24:8s} | {25:14s} | {26:14s} | {27:12s} | {28:12s} |{29:8s} | {30:14s} | {31:14s} | {32:12s} | {33:12s} | {34:10s} | {35:10s} | {36:10s} | {37:10s} | {38:10s} | {39:10s} | {40:10s} | {41:10s} | {42:10s} | {43:10s} | {44:10s} | {45:10s} | {46:10s} | {47:10s} | {48:10s} | {49:10s} | {50:10s} | {51:10s} | {52:29s} | {53:30s} | {54:65s} |'.format(
            num,
            file,
            obtain_hostname(config),
            obtain_mng_ip_from_config(config),
            obtain_domain(config),
            obtain_model(config),
            obtain_serial(config),
            obtain_software_version(config),
            obtain_timezone(config),
            obtain_snmp_version(config),
            check_source_route(config),
            check_service_password_encryption(config),
            check_weak_service_password_encryption(config),
            check_md5_service_password_encryption(config),
            check_ssh_version(config),
            check_logging_buffered(config),
            check_ssh_timeout(config),
            check_boot_network(config),
            check_service_config(config),
            check_cns_config(config),
            dev_con_access[0][1],
            dev_con_access[0][2],
            dev_con_access[0][3],
            dev_con_access[0][4],
            dev_access[0][0],
            dev_access[0][1],
            dev_access[0][2],
            dev_access[0][3],
            dev_access[0][4],
            dev_access[1][0],
            dev_access[1][1],
            dev_access[1][2],
            dev_access[1][3],
            dev_access[1][4],
            check_syslog_timestamp(config),
            check_proxy_arp(config),
            check_logging_console(config),
            check_logging_syslog(config),
            check_log_failures(config),
            check_log_success(config),
            check_tcp_keepalives_in(config),
            check_tcp_keepalives_out(config),
            check_inetd_disable(config),
            check_bootp_disable(config),
            check_authentication_retries(config),
            check_weak_local_users_passwords(config),
            check_motd_banner(config),
            check_accounting_commands(config),
            check_connection_accounting(config),
            check_exec_commands_accounting(config),
            check_system_accounting(config),
            check_new_model(config),
            check_auth_login(config),
            check_auth_enable(config),
            get_ntp_servers(config)
    ))

    resfile.write('{0:4d};{1:75s};{2:25s};{3:15s};{4:20s};{5:18s};{6:10s};{7:12s};{8:12s};{9:10s};{10:10s};{11:10s};{12:10s};{13:12s};{14:6s};{15:25s};{16:12s};{17:6s};{18:6s};{19:6s};{20:14s};{21:14s};{22:14s};{23:12s};{24:8s}:{25:14s};{26:14s};{27:12s};{28:12s};{29:8s};{30:14s};{31:14s};{32:12s};{33:12s};{34:10s};{35:10s};{36:10s};{37:10s};{38:10s}:{39:10s};{40:10s};{41:10s};{42:10s};{43:10s};{44:10s};{45:10s};{46:10s};{47:10s};{48:10s};{49:10s};{50:10s};{51:10s};{52:29s};{53:30s};{54:65s}\n'.format(
            num,
            file,
            obtain_hostname(config),
            obtain_mng_ip_from_config(config),
            obtain_domain(config),
            obtain_model(config),
            obtain_serial(config),
            obtain_software_version(config),
            obtain_timezone(config),
            obtain_snmp_version(config),
            check_source_route(config),
            check_service_password_encryption(config),
            check_weak_service_password_encryption(config),
            check_md5_service_password_encryption(config),
            check_ssh_version(config),
            check_logging_buffered(config),
            check_ssh_timeout(config),
            check_boot_network(config),
            check_service_config(config),
            check_cns_config(config),
            dev_con_access[0][1],
            dev_con_access[0][2],
            dev_con_access[0][3],
            dev_con_access[0][4],
            dev_access[0][0],
            dev_access[0][1],
            dev_access[0][2],
            dev_access[0][3],
            dev_access[0][4],
            dev_access[1][0],
            dev_access[1][1],
            dev_access[1][2],
            dev_access[1][3],
            dev_access[1][4],
            check_syslog_timestamp(config),
            check_proxy_arp(config),
            check_logging_console(config),
            check_logging_syslog(config),
            check_log_failures(config),
            check_log_success(config),
            check_tcp_keepalives_in(config),
            check_tcp_keepalives_out(config),
            check_inetd_disable(config),
            check_bootp_disable(config),
            check_authentication_retries(config),
            check_weak_local_users_passwords(config),
            check_motd_banner(config),
            check_accounting_commands(config),
            check_connection_accounting(config),
            check_exec_commands_accounting(config),
            check_system_accounting(config),
            check_new_model(config),
            check_auth_login(config),
            check_auth_enable(config),
            get_ntp_servers(config)
    ))

    resfile.close()


"""
    for i in range(0, len(dev_access_template) - 1):
        if (ports[i][2] == 'connected'):
            ports_used = ports_used + 1

        resfile.write('{0:1s};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1s};{8:1s};{9:1d};{10:1d};{11:1d};{12:1d};{13:1d} \n'.format(
        file,
        obtain_hostname(config),
        obtain_domain(config),
        obtain_mng_ip_from_config(config),
        obtain_model(config),
        obtain_serial(config),
        obtain_software_version(config),
        obtain_timezone(config),
        obtain_snmp_version(config),
        obtain_secret_settings(config),
        check_source_route(config),
        check_service_password_encryption(config),
        check_weak_service_password_encryption(config),
        check_md5_service_password_encryption(config)
        ))
"""

