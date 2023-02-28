import argparse
from out_to_screen import *
from outintofiles import *
from check_duplicates import check_config_duplicates
from txtfsmparsers import *
from diagram_utils import *
from datamodel import *
import os
import pathlib
from N2G import drawio_diagram

devinfo = []
compliance_result = []
all_devices = []
all_interfaces = []
all_cdps = []
devices = []


def createparser():
    parser = argparse.ArgumentParser(prog='CiscoParser', description='Утилита анализа конфигураций коммутаторов Cisco v0.4.', epilog='author: asha77@gmail.com')
    parser.add_argument('-d', '--configdir', required=False, help='Specify directory with cisco config files', type=pathlib.Path)
    parser.add_argument('-c', '--compcheck', required=False, help='Perform compliance check on config files', action='store_true')
    parser.add_argument('-e', '--extractdata', required=False, help='Perform extraction of data from configs and diagnostic commands and draw picture', action='store_true')
    return parser


def main():
    parser = createparser()
    namespace = parser.parse_args()

    curr_path = os.path.abspath(os.getcwd())
    if namespace.configdir:
        os.chdir(namespace.configdir)

    if namespace.extractdata is True:
        # собираем и выводим конфигурационную информацию
        list_of_files = os.listdir(namespace.configdir)
        print("Starting processing files in folder: " + str(namespace.configdir))
        tbl_header_out2scr()

        # инициализация файлов с результатами работы скрипта
        init_files()

        # проверяем дубликаты устройств по серийникам
        if not check_config_duplicates(list_of_files):
            quit()

        devindex = 0

        # Выводим базовую информацию по всем устройствам на экран и в файл
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()
                    devices.append(config_entity)    # create new empty instance of device model

                    # формирование списка инвентаризационной информации
                    devices_summary_output(list_of_files.index(file), file, config)   # print to screen TODO: to the output section in the end
                    ports_file_output(file, curr_path, config)               # print into file TODO: to the output section in the end

                    # заполняем devinfo
                    devinfo = fill_devinfo_from_config(config, file)         # TODO: to be deleted
#                    fill_devinfo_to_model_from_config(devindex, config, file)   # add to model

                    all_devices.append(devinfo)                              # TODO: to be deleted

                    # формирование перечня cdp-связей
                    cdp_neighbours = get_cdp_neighbours(config, curr_path, file, devinfo)       # TODO: to be deleted
#                    get_cdp_neighbours_to_model(devindex, config, curr_path)

                    all_cdps.append(cdp_neighbours)                                             # TODO: to be deleted

                    # формирование перечня активных портов, где CDP видит соседей
                    all_neighbours_file_output(cdp_neighbours)       # print ports with neighbours into file TODO: to the output section in the end
                    neighbours_file_output(cdp_neighbours)           # print CDP connectivity into file TODO: to the output section in the end

                    # формирование перечня портов, за которым видно много MAC-адресов
#                    many_macs_file_output(config, curr_path, cdp_neighbours, devinfo)  # optional - to rework

                    # формирование перечня VLAN на портах
                    int_config = get_interfaces_config(config, curr_path, file, devinfo)    # TODO: to be deleted
#                    get_interfaces_config_to_model(devindex, config, curr_path,)

                    interfaces_file_output(int_config)              # print interfaces info into file TODO: to the output section in the end

        # завершаем таблицу
        tbl_footer_out2scr()

        # Trying to find missed devices that can be found in cdp data and save this to "missed_devices.csv" file
        missed_devices = find_missed_devices()
        missed_devices_file_output(missed_devices)

        if len(missed_devices) > 0:
            print("В конфигурации CDP найдено {} устройств, конфигурации которых отсутствуют. "
                  "См. файл missed.devices.csv".format(len(missed_devices)))

        # анализ необходимых VLAN на транковых портах
#        trunking_analisys()


        # TODO: наверное нужно вытащить из цикла процедуры сохранения cdp, interfaces в файлы и делать это где-то здесь

        print("")
        print("Рисуем схему сети...")

        diagram = drawio_diagram()
        diagram.add_diagram("Page-1")
            #        diagram.add_node(id="R2", style=".\\styles\\router.txt")
            #        diagram.add_node(id="R2", style=router_style)
            #        diagram.add_node(id="R1", style=router_style)
            #        diagram.add_node(id="R3", style=router_style)
            #        diagram.add_link("R1", "R2", src_label="Gi0/1", trgt_label="ge-0/1/2", data={"speed": "1G", "media": "10G-LR"})
            #        diagram.add_link("R2", "R3", src_label="Gi0/1", trgt_label="ge-0/1/2", data={"speed": "1G", "media": "10G-LR"})

            # собираем и выводим конфигурационную информацию
#        list_of_files = os.listdir(namespace.configdir)

            # проверяем дубликаты устройств по серийникам
#        if not check_config_duplicates(list_of_files):
#            quit()

        # Добавляем на диаграмму все устройства
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()
                    # заполняем devinfo
                    devinfo = fill_devinfo_from_config(config, file)

                    if filter_devices(get_only_name(devinfo[0])):
                        lbtext = get_only_name(devinfo[0]) + "&lt;div&gt;" + devinfo[3]
                        #                        lbtext = lbtext.replace(" +", "\u00a0").replace("\n", " ")
                        if devinfo[2] == "Not set":
                            dev_id = devinfo[0]
                        else:
                            dev_id = devinfo[0] + "." + devinfo[2]
                        diagram.add_node(id=dev_id, label=lbtext, style=get_dev_style_from_model(devinfo[3])[0],
                                        width=(get_dev_style_from_model(devinfo[3])[1]),
                                        height=(get_dev_style_from_model(devinfo[3])[2]),
                                        data={"IP": devinfo[1], "Serial": devinfo[4]})
                    else:
                        print("skipped: " + devinfo[0])

            # Добавляем на диаграмму все связи между устройствами
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()
                    # заполняем devinfo
                    devinfo = fill_devinfo_from_config(config, file)
                    # формирование перечня cdp-связности
                    cdp_neighbours = get_cdp_neighbours(config, curr_path, file, devinfo)
                    # ToDo: provide actual data info in links
                    for i in range(0, len(cdp_neighbours)):
                        if (filter_devices(get_only_name(cdp_neighbours[i][1])) and filter_devices(
                            get_only_name(cdp_neighbours[i][5]))):
                                linkstyle = get_link_style_from_model(cdp_neighbours[i][4])
                                diagram.add_link(cdp_neighbours[i][1], cdp_neighbours[i][5],
                                src_label=shorten_ifname(cdp_neighbours[i][4]),
                                trgt_label=shorten_ifname(cdp_neighbours[i][8]), style=linkstyle,
                                data={"speed": "1G", "media": "10G-LR"})
                        else:
                            print("skipped: " + cdp_neighbours[i][1] + " - " + cdp_neighbours[i][5])

        diagram.layout(algo="drl")
        diagram.dump_file(filename="network_graph.drawio", folder="./output/")

        # Добавляем на диаграмму все устройства
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()
                    # заполняем devinfo
                    devinfo = fill_devinfo_from_config(config, file)

                    if filter_devices(get_only_name(devinfo[0])):
                        lbtext = get_only_name(devinfo[0]) + "&lt;div&gt;" + devinfo[3]
                        #                        lbtext = lbtext.replace(" +", "\u00a0").replace("\n", " ")
                        if devinfo[2] == "Not set":
                            dev_id = devinfo[0]
                        else:
                            dev_id = devinfo[0] + "." + devinfo[2]
                        diagram.add_node(id=dev_id, label=lbtext, style=get_dev_style_from_model(devinfo[3])[0],
                                        width=(get_dev_style_from_model(devinfo[3])[1]),
                                        height=(get_dev_style_from_model(devinfo[3])[2]),
                                        data={"IP": devinfo[1], "Serial": devinfo[4]})
                    else:
                        print("skipped: " + devinfo[0])
        print("Finished processing files in folder: " + str(namespace.configdir))
        # выводим summary что где лежит
        tbl_files_info_out2scr()
    elif (namespace.configdir is not None) and (namespace.compcheck is True):
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
                    write_compliance()

        write_xls_report(curr_path)
        tbl_complfooter_out2scr()
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