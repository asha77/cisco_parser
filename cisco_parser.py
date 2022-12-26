import argparse
from out_to_screen import *
from outintofiles import *
from check_duplicates import *
from txtfsmparsers import *
from diagram_utils import *
import os
import pathlib
from N2G import drawio_diagram


devinfo = []


def createparser():
    parser = argparse.ArgumentParser(prog='CiscoParser', description='Утилита анализа конфигураций коммутаторов Cisco v0.4.', epilog='author: agulyaev@jet.su')
    parser.add_argument('mode', help='single - process single file | all - process all files in directory')
    parser.add_argument('-r', '--showrun', required=False, help='Specify single cisco config file (show run output)', type=argparse.FileType())
    parser.add_argument('-d', '--configdir', required=False, help='Specify directory with many cisco config files', type=pathlib.Path)
    parser.add_argument('-c', '--compcheck', required=False, help='Perform compliance check on config files', action='store_true')
    parser.add_argument('-e', '--extractdata', required=False, help='Perform extraction of data from configs and diagnostic commands', action='store_true')
    parser.add_argument('-p', '--picture', required=False, help='Create drawio connectivity diagram configs and diagnostic commands', action='store_true')

    # parser.add_argument('-i', '--showinterfaces', type=argparse.FileType())
    # parser.add_argument('-a', '--showall', action='store_const', const=True)
    # parser.add_argument('-m', '--showmacs', nargs='?', type=argparse.FileType())
    # parser.add_argument('-s', '--skstable', nargs='?', type=argparse.FileType())
    # parser.add_argument('-c', '--commtable', nargs='?', type=argparse.FileType())
    return parser


def main():
    #    print("Утилита анализа конфигураций коммутаторов Cisco v0.1.")

    parser = createparser()
    namespace = parser.parse_args()

    if (namespace.mode == 'single') and (namespace.showrun is None):
        print("!!! Ошибка: Необходмо указать файл конфигурации Cisco для анализа (полный вывод show running-config)")
        exit()

    curr_path = os.path.abspath(os.getcwd())
    if namespace.configdir:
        os.chdir(namespace.configdir)

    if (namespace.mode == 'single') and (namespace.showrun is not None):
        cfilename = namespace.showrun
        tbl_header_out2scr()
        devices_summary_output(1, namespace.showrun, cfilename.read())
        tbl_footer_out2scr()
    elif (namespace.mode == 'all') and (namespace.configdir is not None) and (namespace.extractdata is True):
        # собираем и выводим конфигурационную информацию
        list_of_files = os.listdir(namespace.configdir)
        tbl_header_out2scr()

        # инициализация файлов с результатами работы скрипта
        init_files()

        # проверяем дубликаты устройств по серийникам
        if not check_config_duplicates(list_of_files):
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
                    devinfo = fill_devinfo_from_config(config)

                    # формирование перечня cdp-связности
                    cdp_neighbours = get_cdp_neighbours(config, curr_path, file, devinfo)

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

    elif (namespace.mode == 'all') and (namespace.configdir is not None) and (namespace.compcheck is True):
        # проверяем compliance
        list_of_files = os.listdir(namespace.configdir)
        tbl_complheader_out2scr()

        # инициализация файлов с результатами работы скрипта
        init_comliance_files()

        # проверяем дубликаты устройств по серийникам
        if not check_config_duplicates(list_of_files):
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

    elif (namespace.mode == 'all') and (namespace.configdir is not None) and (namespace.picture is True):
        diagram = drawio_diagram()
        diagram.add_diagram("Page-1")
#        diagram.add_node(id="R2", style=".\\styles\\router.txt")
#        diagram.add_node(id="R2", style=router_style)
#        diagram.add_node(id="R1", style=router_style)
#        diagram.add_node(id="R3", style=router_style)
#        diagram.add_link("R1", "R2", src_label="Gi0/1", trgt_label="ge-0/1/2", data={"speed": "1G", "media": "10G-LR"})
#        diagram.add_link("R2", "R3", src_label="Gi0/1", trgt_label="ge-0/1/2", data={"speed": "1G", "media": "10G-LR"})

        # собираем и выводим конфигурационную информацию
        list_of_files = os.listdir(namespace.configdir)

        # проверяем дубликаты устройств по серийникам
        if not check_config_duplicates(list_of_files):
            quit()

        # Добавляем на диаграмму все устройства
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()
                    # заполняем devinfo
                    devinfo = fill_devinfo_from_config(config)

                    if filter_devices(get_only_name(devinfo[0])):
                        lbtext = get_only_name(devinfo[0]) + "\n" + devinfo[3]
                        lbtext = lbtext.replace(" +", "\u00a0").replace("\n", " ")
                        diagram.add_node(id=get_only_name(devinfo[0]), label=lbtext, style=get_dev_style_from_model(devinfo[3])[0], width=(get_dev_style_from_model(devinfo[3])[1]), height=(get_dev_style_from_model(devinfo[3])[2]))
                    else:
                        print("skipped: " + get_only_name(devinfo[0]))

        # Добавляем на диаграмму все связи между устройствами
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()
                    # заполняем devinfo
                    devinfo = fill_devinfo_from_config(config)
                    # формирование перечня cdp-связности
                    cdp_neighbours = get_cdp_neighbours(config, curr_path, file, devinfo)

                    for i in range(0, len(cdp_neighbours)):
                        if (filter_devices(get_only_name(cdp_neighbours[i][1])) and filter_devices(get_only_name(cdp_neighbours[i][5]))):
                            linkstyle = get_link_style_from_model(cdp_neighbours[i][4])
                            diagram.add_link(get_only_name(cdp_neighbours[i][1]), get_only_name(cdp_neighbours[i][5]), src_label=shorten_ifname(cdp_neighbours[i][4]), trgt_label=shorten_ifname(cdp_neighbours[i][8]), style=linkstyle, data={"speed": "1G", "media": "10G-LR"})
                        else:
                            print("skipped: " + get_only_name(cdp_neighbours[i][1]) + " - " + get_only_name(cdp_neighbours[i][5]))

        diagram.layout(algo="drl")
        diagram.dump_file(filename="network_graph.drawio", folder="./output/")
        tbl_files_info_out2scr()

if __name__ == "__main__":
    main()




"""
        | algo name                       |    description                                                                                                 |
        | circle, circular                | Deterministic layout that places the vertices on a circle                                                      |
        | drl                             | The Distributed Recursive Layout algorithm for large graphs                                                    |
        | fr                              | Fruchterman-Reingold force-directed algorithm                                                                  |
        | fr3d, fr_3d                     | Fruchterman-Reingold force-directed algorithm in three dimensions                                              |
        | grid_fr                         | Fruchterman-Reingold force-directed algorithm with grid heuristics for large graphs                            |
        | kk                              | Kamada-Kawai force-directed algorithm                                                                          |
        | kk3d, kk_3d                     | Kamada-Kawai force-directed algorithm in three dimensions                                                      |
        | large, lgl, large_graph         | The Large Graph Layout algorithm for large graphs                                                              |
        | random                          | Places the vertices completely randomly                                                                        |
        | random_3d                       | Places the vertices completely randomly in 3D                                                                  |
        | rt, tree                        | Reingold-Tilford tree layout, useful for (almost) tree-like graphs                                             |
        | rt_circular, tree               | Reingold-Tilford tree layout with a polar coordinate post-transformation, useful for (almost) tree-like graphs |
        | sphere, spherical, circular_3d  | Deterministic layout that places the vertices evenly on the surface of a sphere                                |
"""