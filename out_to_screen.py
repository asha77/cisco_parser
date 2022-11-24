import os
import pathlib
from regparsers import *


def tbl_header_out2scr():
    print("---------------------------------------------------------------------"
          "-------------------------------------------------------------------------------"
          "----------------------------------------------------------")

    print("|  Num |                                   Filename                                  |     "
          "   Hostname           |        IP       |      Domain Name    "
          " |       Model        |    Serial   |  SW Version  |")
    print("---------------------------------------------------------------------"
          "-------------------------------------------------------------------------------"
          "----------------------------------------------------------")


def tbl_footer_out2scr():
    print("---------------------------------------------------------------------"
          "-------------------------------------------------------------------------------"
          "----------------------------------------------------------")


def tbl_files_info_out2scr():
    print("Файлы сохраняются в подпапке \"оutput\" папки с обрабатываемыми конфигурациями")
    print("     - cparser.txt               - основные сведения о KE (inventory)")
    print("     - all_nei_output.csv        - список активных портов, на которых CDP видит подключнное оборудование")
    print("     - cdp_nei_output.csv        - список связей между устройствами, орпределенный с помощью")
    print("     - many_macs.csv             - список портов, за которыми скрывается множество MAC-адресов")
    print("     - compliance_output.csw     - результаты проверки compliance")


def tbl_complheader_out2scr():
    print("---------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "---------------------------------------------------------------------------"
        "-----------------------------")

    print("|  Num |                                   Filename                                  |     "
        "   Hostname           |        IP       |      Domain Name    "
        " |       Model        |    Serial   |  SW Version  |   TimeZone   |  SNMP ver  |"
        "  No SrcRt  |  Pass Encr | Weak Encr  | Strong Encr | SSH Chk |  Logging buffered "
        "(level) |  SSH Timeout |Boot Cnf| ServCnf| CNSCnf | con0 exec-time | con0 trans pref"
        "| con0 trans inp | con0 logiauth|  vty num |  vty exec-time | vty trans pref |vty trans inp | "
        "vty acc class| vty num | vty exec-time  | vty trans pref |vty trans inp | vty acc class| syslog TS  |"
        " proxy arp  | log con    | log sysl   | log fail   | log succ   | tcp-kp-in  | tcp-kp-out "
        "| inetd      | bootp      | auth_retr  | weak_pass  | motd       | acc_com    | acc_conn   "
        "| acc_exec   | acc_system | new model  |          auth_login           |           auth_enable"
        "          |                                ntp srv                             |")


    print("---------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "---------------------------------------------------------------------------"
        "-----------------------------")



def tbl_complfooter_out2scr():
    print("---------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "-------------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "----------------------------------------------------------------------------"
        "---------------------------------------------------------------------------"
        "-----------------------------")


def devices_summary_output(number, filename, config: object):
    print('| {0:4d} | {1:75s} | {2:25s} | {3:15s} | {4:20s} | {5:18s} |  {6:10s} | {7:12s} |'.format(
        number + 1,
        filename,
        obtain_hostname(config),
        obtain_mng_ip_from_config(config),
        obtain_domain(config),
        obtain_model(config),
        obtain_serial(config),
        obtain_software_version(config))
    )
