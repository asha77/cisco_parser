import argparse
from out_to_screen import *
from txtfsmparsers import *
from outintofiles import *


from txtfsmparsers import *
import os
import pathlib

#from manuf import manuf

devinfo = []

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

    curr_path = os.path.abspath(os.getcwd())
    if namespace.configdir:
        os.chdir(namespace.configdir)

    if namespace.mode == 'single':
        config = cfilename.read()
        print("---------------------------------------------------------------------"
              "-------------------------------------------------------------------------------"
              "----------------------------------------------------------")
        print("|  Num |                                   Filename                                  |     "
              "   Hostname           |        IP       |      Domain Name    "
              " |       Model        |     Serial   |  SW Version  |")
        print("---------------------------------------------------------------------"
              "-------------------------------------------------------------------------------"
              "----------------------------------------------------------")
        devices_summary_output(1, config)
    else:
        list_of_files = os.listdir(namespace.configdir)
        print("---------------------------------------------------------------------"
              "-------------------------------------------------------------------------------"
              "----------------------------------------------------------")

        print("|  Num |                                   Filename                                  |     "
              "   Hostname           |        IP       |      Domain Name    "
              " |       Model        |     Serial   |  SW Version  |")
        print("---------------------------------------------------------------------"
              "-------------------------------------------------------------------------------"
              "----------------------------------------------------------")
        # инициализация файлов с результатами работы скрипта
        init_files()

        # создать папку для результатов, если она еще не создана
        if not os.path.isdir("output"):
            os.mkdir("output")
        serial_list =[]


        # поиск дубликатов конфигураций - конфигов с одним и тем же serial number
        # заполняем массив с серийниками
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()
                    serial_list.append([])
                    serial_list[list_of_files.index(file)].append(list_of_files.index(file)+1)
                    serial_list[list_of_files.index(file)].append(file)
                    serial_list[list_of_files.index(file)].append(obtain_serial(config))

        # ищем дупликаты в массиве с серийниками
        for num in range(0, len(serial_list)):
            for num2 in range(num + 1, len(serial_list)):
                if serial_list[num][2] == serial_list[num2][2]:
                    print("Устраните дублирование конфигураций:")
                    print("Файл: "+serial_list[num][1]+" Serial: " +serial_list[num][2])
                    print("Файл: "+serial_list[num2][1]+" Serial: " +serial_list[num2][2])
                    quit()

        # Выводим базовую информацию по всем устройствам на экран и в файл
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()

                    # формирование списка инвентаризационной информации
                    devices_summary_output(list_of_files.index(file), file, config)   # print to screen
                    ports_file_output(file, curr_path, config)                        # print to file

                    # формирование перечня cdp-связности
                    cdp_neighbours=get_cdp_neighbours(config, curr_path, file, fill_devinfo_from_config(config))

                    # формирование перечня CDP-соседей
                    all_neighbours_file_output(cdp_neighbours)       # print ports with neighbours to file
                    neighbours_file_output(cdp_neighbours)           # print CDP connectivity to file

                    # формирование перечня портов, за которым видно много MAC-адресов
                    many_macs_file_output(config, curr_path, cdp_neighbours, fill_devinfo_from_config(config))

                    # формирование перечня VRF



        # conffile.close()
        print("---------------------------------------------------------------------"
              "-------------------------------------------------------------------------------"
              "----------------------------------------------------------")

        print("Output:")
        print("     - cparser.txt               - основные сведения о KE (inventory)")
        print("     - all_nei_output.csv        - список активных портов, на которых CDP видит подключнное оборудование")
        print("     - cdp_nei_output.csv        - список связей между устройствами, орпределенный с помощью")
        print("     - many_macs.csv             - список портов, за которыми скрывается множество MAC-адресов")


if __name__ == "__main__":
    main()