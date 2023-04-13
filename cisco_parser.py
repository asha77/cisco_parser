import argparse
import out_to_screen
import outintofiles
import check_duplicates
import txtfsmparsers
import diagram_utils
import datamodel
import os
import pathlib
import N2G
import regparsers
import copy
from alive_progress import alive_bar


compliance_result = []
devices = []
empty_device = {}


def createparser():
    parser = argparse.ArgumentParser(prog='CiscoParser', description='Utility for analyzing network device configurations v0.6.', epilog='author: asha77@gmail.com')
    parser.add_argument('-d', '--configdir', required=False, help='Specify directory with cisco config files', type=pathlib.Path)
    parser.add_argument('-c', '--compcheck', required=False, help='Perform compliance check on config files', action='store_true')
    parser.add_argument('-u', '--disablefilecheck', required=False, help='Disable checking for unique devices config files', action='store_true')
    parser.add_argument('-e', '--extractdata', required=False, help='Perform extraction of data from configs and diagnostic commands and draw picture', action='store_true')
    return parser


def main():
    parser = createparser()
    namespace = parser.parse_args()

    curr_path = os.path.abspath(os.getcwd())
    if namespace.configdir:
        os.chdir(namespace.configdir)

    if namespace.extractdata is True:
        # get list of files with configs and diagnostic
        list_of_files = os.listdir(namespace.configdir)
        print("Starting processing files in folder: " + str(namespace.configdir))

        # create output files where we will save results
        outintofiles.init_files()

        # check file duplicates using extracted serial numbers
        if namespace.disablefilecheck is False:
            if not check_duplicates.check_config_duplicates(list_of_files):
                quit()

        # Start processing of configs
        with alive_bar(len(list_of_files), length=55, title='Progress', force_tty=True) as bar:
            for file in list_of_files:
                bar.text = f'Processing file: {file}, please wait...'
                if os.path.isfile(file):
                    with open(file, "r") as conffile:
                        config = conffile.read()
                        empty_device = copy.deepcopy(datamodel.config_entity)

                        # get basic parameters
                        regparsers.fill_devinfo_to_model_from_config(empty_device, config, file)   # add to model

                        # get list of cdp neighbours
                        txtfsmparsers.get_cdp_neighbours_to_model(empty_device, config, curr_path)

                        # get list of ports with many MAC-addresses under them
                        # outintofiles.many_macs_file_output(config, curr_path, cdp_neighbours, devinfo)  # optional - to rework

                        # get interfaces configuration
                        txtfsmparsers.get_interfaces_config_to_model(empty_device, config, curr_path)

                        txtfsmparsers.get_vlans_configuration_to_model(empty_device, config, curr_path)

                        # add collected device data into array
                        devices.append(empty_device)
                bar()

        out_to_screen.print_devices_summary(devices)

        # print inventory data into cparser.csv file
        outintofiles.summary_file_output(devices)       # ToDo: check stacked devices

        #  print all neighbours from all devices into 'all_neighbours_output.csv' file
        outintofiles.all_neighbours_to_file(devices)

        #  print links (connectivity) to all neighbours from all devices into file 'cdp_nei_output.csv'
        outintofiles.connectivity_to_file(devices)

        # print interfaces info into file
        outintofiles.interfaces_to_file(devices)

        # Trying to find missed devices that can be found in cdp data and save this to "missed_devices.csv" file
        missed_devices = outintofiles.find_missed_devices()
        outintofiles.missed_devices_file_output(missed_devices)

        if len(missed_devices) > 0:
            print('In CDP configuration we found mentioned {} devices, for whom we have no configurations.\n'
                  'See file \"missed.devices.csv\"'.format(len(missed_devices)))

        # analysis of required VLAN on trunk ports
#        trunking_analisys()

        print("")
        print("Creating network diagram...")

        diagram = N2G.drawio_diagram()
        diagram.add_diagram("Page-1")

        # diagram.add_node(id="R2", style=".\\styles\\router.txt")
        # diagram.add_node(id="R2", style=router_style)
        # diagram.add_node(id="R1", style=router_style)
        # diagram.add_node(id="R3", style=router_style)
        # diagram.add_link("R1", "R2", src_label="Gi0/1", trgt_label="ge-0/1/2", data={"speed": "1G", "media": "10G-LR"})
        # diagram.add_link("R2", "R3", src_label="Gi0/1", trgt_label="ge-0/1/2", data={"speed": "1G", "media": "10G-LR"})

        for device in devices:
            if diagram_utils.filter_devices(regparsers.get_only_name(device['hostname'])):
                lbtext = regparsers.get_only_name(device['hostname']) + "&lt;div&gt;" + device['model']
                if device['domain_name'] == "Not set":
                    dev_id = device['hostname']
                else:
                    dev_id = device['hostname'] + "." + device['domain_name']

                style = diagram_utils.get_dev_style_from_model(device['model'])
                diagram.add_node(id=dev_id, label=lbtext,
                                 style=style[0],
                                 width=(style[1]),
                                 height=(style[2]),
                                 data={"IP": device['mgmt_ipv4_from_filename'], "Serial": device['serial']}
                                 )
            else:
                print("skipped: " + device['hostname'])

        # Add links between devices on diagram
        for device in devices:
            for cdp_neighbour in device['cdp_neighbours']:

                if diagram_utils.filter_devices(regparsers.get_only_name(cdp_neighbour['local_id'])) and diagram_utils.filter_devices(regparsers.get_only_name(cdp_neighbour['remote_id'])):

                    linkstyle = diagram_utils.get_link_style_from_model(cdp_neighbour['local_interface'])   # ToDo: provide actual data info on links

                    diagram.add_link(cdp_neighbour['local_id'], cdp_neighbour['remote_id'],
                                     src_label=diagram_utils.shorten_ifname(cdp_neighbour['local_interface']),
                                     trgt_label=diagram_utils.shorten_ifname(cdp_neighbour['remote_interface']),
                                     style=linkstyle,
                                     data={"speed": "1G", "media": "10G-LR"})
                else:
                    print("skipped: " + cdp_neighbour['local_id'] + " - " + cdp_neighbour['remote_id'])

        diagram.layout(algo="drl")
        diagram.dump_file(filename="network_graph.drawio", folder="./output/")

        print("Finished processing files in folder: " + str(namespace.configdir) + '\n')

        # print devices summary
        out_to_screen.tbl_files_info_out2scr()

    elif (namespace.configdir is not None) and (namespace.compcheck is True):
        # check compliance
        list_of_files = os.listdir(namespace.configdir)

        out_to_screen.tbl_complheader_out2scr()

        # init output files
        outintofiles.init_comliance_files()

        # check devices duplicates
        if namespace.disablefilecheck is False:
            if not check_duplicates.check_config_duplicates(list_of_files):
                quit()

        # processing compliance checks on config files
        for file in list_of_files:
            if os.path.isfile(file):
                with open(file, "r") as conffile:
                    config = conffile.read()
                    outintofiles.check_compliance(list_of_files.index(file), file, curr_path, config)
                    outintofiles.write_compliance()

        outintofiles.write_xls_report(curr_path)
        out_to_screen.tbl_complfooter_out2scr()
        out_to_screen.tbl_files_info_out2scr()


if __name__ == "__main__":
    main()
