import argparse
from N2G import drawio_diagram
import zlib
import base64
from urllib.parse import unquote
import xml.etree.ElementTree as ET


def createparser():
    parser = argparse.ArgumentParser(prog='DiagramParser', description='Utility for extraction information from drawio network diagram', epilog='author: asha77@gmail.com')
    parser.add_argument('-f', '--file', required=True, help='Create data and connectivity tables using drawio pictures')
    return parser


def get_dev_by_id(nodes, id):
    devname = ""
    for node in nodes:
        if len(list(node)):
            if (node[0].attrib.get("style")):
                if (not node[0].attrib.get("style").find("mxgraph") == -1):
                    if id == node.attrib.get("id"):
                        devname = node.attrib.get("Name")

#    if devname == "":
#        print("One link ")

    return devname


def main():
    parser = createparser()
    namespace = parser.parse_args()

    if namespace.file is None:
        print("!!! Error - please specify valid diagram filename")
        exit()

    diagram = drawio_diagram()
    diagram.from_file(namespace.file)

#    diagram.from_file("net_diag.drawio.xml")
#    data = base64.b64decode(diagram.current_diagram.text)
#    xml = zlib.decompress(data, wbits=-15)
#    xml = unquote(xml)

#    print(xml)
#    tree = ET.parse("netdiag.xml")
#    root = tree.getroot()

#    root = ET.fromstring(diagram.drawio_diagram_xml)

    #    root = ET.fromstring(xml)
#    nodes = root.find('root')


    nodes = diagram.current_root

    print("List of devices:")
    i = 0
    devices = []

    for node in nodes:
        if len(list(node)):
            if (node[0].attrib.get("style")):
                if (not node[0].attrib.get("style").find("mxgraph") == -1):
                    devices.append([])
                    devices[i].append(node.attrib.get("Name"))
                    devices[i].append(node.attrib.get("Model"))
                    devices[i].append(node.attrib.get("Power"))
                    devices[i].append(node.attrib.get("Height"))
                    devices[i].append(node.attrib.get("id"))
                    #       print(node.attrib.get("Name"))
                    i = i + 1

    print('-------------------------------------------------------------------------------------')
    print('|  №   | Device name          |    Модель                 |   Pwr, W   |   Size, U  |')
    print('-------------------------------------------------------------------------------------')

    resfile = open("output\devices.csv", "w")
    resfile.write('№;Device name;Модель;Pwr, W;Size, U\n')

    for dev in devices:
        print('| {0:4d} | {1:20s} | {2:25s} | {3:10s} | {4:10s} |'.format(devices.index(dev)+1, dev[0], dev[1], dev[2], dev[3]))
        resfile.write('{0:1d};{1:1s};{2:1s};{3:1s};{4:1s}\n'.format(devices.index(dev)+1, dev[0], dev[1], dev[2], dev[3]))

    print('-------------------------------------------------------------------------------------\n')
    print(f"Total number of devices: {i} \n")
    print('\n')
    resfile.close()

    i = 0
    links = []

    for node in nodes:
        if (node.attrib.get("edge") == "1"):
            for child_node in nodes:
                if (len(list(child_node))):
                    if child_node[0].attrib.get("parent") == node.attrib.get("id"):
                        links.append([])
                        links[i].append(child_node.attrib.get("Interface"))
                        links[i].append(child_node.attrib.get("Type"))
                        links[i].append(child_node.attrib.get("Media"))

                        # получить адреса устройств source и destination
                        links[i].append(get_dev_by_id(nodes, node.attrib.get("source")))
                        links[i].append(get_dev_by_id(nodes, node.attrib.get("target")))
                        i = i + 1


    # node with node[0].attrib.get("edge") == "1" - patch cord with node.attrib.get
    #    node.attrib.get('label') = "%Length%"
    #    node.attrib.get('Length') = "2m"
    #    node.attrib.get('Media') = "MMF Duplex LC"
    #    node.attrib.get('Type') = "patch-cord"
    #    node.attrib.get('id') = "fldpP99OWHAwPYHl0EUT-5"

    # child_node with child_node[0].attrib.get("parent") = node.attrib.get('id') ("fldpP99OWHAwPYHl0EUT-5")
    #   child_node.attrib.get("id") = "fldpP99OWHAwPYHl0EUT-6"
    #   child_node.attrib.get("label") = "%Interface%"
    #   child_node.attrib.get("Interface") = "TGE1/1/48"
    #   child_node.attrib.get("Type") = "10GBaseLR"
    #   child_node.attrib.get("Speed") = "10G"
    #   child_node.attrib.get("Socket") = "SFP+"

    for node in nodes:                      # node - trying to find patch cord - get("edge") == "1")
        if len(list(node)) > 0:
            if (node[0].attrib.get("edge") == "1"):
                for child_node in nodes:    # serching for objects with interfaces description
                    if (len(list(child_node))):
                        if child_node[0].attrib.get("parent") == node.attrib.get("id"):
                            links.append([])
                            links[i].append(child_node.attrib.get("Interface"))
                            links[i].append(child_node.attrib.get("Type"))
                            links[i].append(node.attrib.get('Media'))

                            # получить адреса устройств source и destination
                            links[i].append(get_dev_by_id(nodes, node[0].attrib.get("source")))
                            links[i].append(get_dev_by_id(nodes, node[0].attrib.get("target")))
                i = i + 1

# print list of links

    print('---------------------------------------------------------------------------------------------------------------------------------------------------------------')
    print('|  №   | Device name          |    Interface    |     Int Type    |           Media           | Device name          |       Interface      |      Int Type   |')
    print('---------------------------------------------------------------------------------------------------------------------------------------------------------------')

    resfile = open("output\cable_journal.csv", "w")
    resfile.write('№;Device name;Interface;Int Type;Media;Device name;Interface;Int Type\n')

    for lnk in links:
        if len(lnk) == 0:
            continue
        print('| {0:4d} | {1:20s} | {2:15s} | {3:15s} | {4:25s} | {5:20s} | {6:20s} | {7:15s} |'.format(links.index(lnk)+1, lnk[3], lnk[0], lnk[1], lnk[2], lnk[4], lnk[5], lnk[6]))
        resfile.write('{0:1d};{1:1s};{2:1s};{3:1s};{4:1s};{5:1s};{6:1s};{7:1s}\n'.format(links.index(lnk)+1, lnk[3], lnk[0], lnk[1], lnk[2], lnk[4], lnk[5], lnk[6]))

    print('---------------------------------------------------------------------------------------------------------------------------------------------------------------\n')
    resfile.close()

    print(f"Total number of links: {i}")
#    diagram.dump_file("outfile.drawio")


if __name__ == "__main__":
    main()
