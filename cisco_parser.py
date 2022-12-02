import argparse
from out_to_screen import *
from outintofiles import *
from check_duplicates import *
from txtfsmparsers import *
import os
import pathlib


devinfo = []

def createParser():
    parser = argparse.ArgumentParser(prog='CiscoParser', description='Утилита анализа конфигураций коммутаторов Cisco v0.4.', epilog = 'author: agulyaev@jet.su')
    parser.add_argument('mode', help='single - process single file | all - process all files in directory')
    parser.add_argument('-r', '--showrun', required=False, help='Specify single cisco config file (show run output)', type=argparse.FileType())
    parser.add_argument('-d', '--configdir', required=False, help='Specify directory with many cisco config files', type=pathlib.Path)
    parser.add_argument('-c', '--compcheck', required=False, help='Perform compliance check on config files', action='store_true')
    parser.add_argument('-e', '--extractdata', required=False, help='Perform extraction of data from configs and diagnostic commands', action='store_true')

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

    curr_path = os.path.abspath(os.getcwd())
    if namespace.configdir:
        os.chdir(namespace.configdir)

    if ((namespace.mode == 'single') and (not namespace.showrun == None)):
        cfilename = namespace.showrun
        tbl_header_out2scr()
        devices_summary_output(1, namespace.showrun, cfilename.read())
        tbl_footer_out2scr()
    elif ((namespace.mode == 'all') and (not namespace.configdir == None) and (namespace.extractdata == True)):
        # собираем и выводим конфигурационную информацию
        list_of_files = os.listdir(namespace.configdir)
        tbl_header_out2scr()

        # инициализация файлов с результатами работы скрипта
        init_files()

        # проверяем дубликаты устройств по серийникам
        if (not check_config_duplicates(list_of_files)):
            quit()

        # Выводим базовую информацию по всем устройствам на экран и в файл
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()

                    # формирование списка инвентаризационной информации
                    devices_summary_output(list_of_files.index(file), file, config)   # print to screen
                    ports_file_output(file, curr_path, config)                        # print into file

                    # заполняем devinfo
                    devinfo=fill_devinfo_from_config(config)

                    # формирование перечня cdp-связности
                    cdp_neighbours=get_cdp_neighbours(config, curr_path, file, devinfo)

                    # формирование перечня CDP-соседей
                    all_neighbours_file_output(cdp_neighbours)       # print ports with neighbours into file
                    neighbours_file_output(cdp_neighbours)           # print CDP connectivity into file

                    # формирование перечня портов, за которым видно много MAC-адресов
                    many_macs_file_output(config, curr_path, cdp_neighbours, devinfo)

                    # формирование перечня VLAN на портах
                    int_config = get_interfaces_config(config, curr_path, file, devinfo)
                    interfaces_file_output(int_config)              # print interfaces info into file

        # conffile.close()
        tbl_footer_out2scr()
        tbl_files_info_out2scr()

    elif ((namespace.mode == 'all') and (not namespace.configdir == None) and (namespace.compcheck == True)):
        # проверяем compliance

        list_of_files = os.listdir(namespace.configdir)
        tbl_complheader_out2scr()

        # инициализация файлов с результатами работы скрипта
        init_comliance_files()

        # проверяем дубликаты устройств по серийникам
        if (not check_config_duplicates(list_of_files)):
            quit()

        # Выводим базовую информацию по всем устройствам на экран и в файл

        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()

                    # формирование списка инвентаризационной информации
#                    devices_summary_output(list_of_files.index(file), file, config)   # print to screen
#                    ports_file_output(file, curr_path, config)                        # print into file

                    # заполняем devinfo
                    # devinfo=fill_devinfo_from_config(config)

                    check_compliance(list_of_files.index(file), file, curr_path, config)

        tbl_complfooter_out2scr()
        tbl_files_info_out2scr()


if __name__ == "__main__":
    main()