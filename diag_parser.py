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


def main():
    parser = createparser()
    namespace = parser.parse_args()

    if namespace.file is None:
        print("!!! Error - please specify valid diagram filename")
        exit()

    diagram = drawio_diagram()
    diagram.from_file(namespace.file)

    data = base64.b64decode(diagram.current_diagram.text)
    xml = zlib.decompress(data, wbits=-15)
    xml = unquote(xml)

#    print(xml)
#    tree = ET.parse("netdiag.xml")
#    root = tree.getroot()

    root = ET.fromstring(xml)
    nodes = root.find('root')

    print("This is list of devices:")
    i = 0
    for node in nodes:
#        if (node.attrib.get("connectable") is None) and (node.attrib.get("edge") is None):
        if (node[0].attrib.get("style")):
            if (not node[0].attrib.get("style").find("mxgraph") == -1):
                print(node[0].attrib.get("value"))
                i = i + 1
    print(f"Total number of devices: {i}")

    print(" =============================================== ")

    print("")
    print("This is list of links:")

    i = 0
    links = []

    for node in nodes:
        if (node.attrib.get("edge") == "1"):
            links.append([])
            for child_node in nodes:
                if child_node.attrib.get("parent") == node.attrib.get("id"):
                    links[i].append(child_node.attrib.get("value"))
            i = i + 1

    for lnk in links:
        print(lnk[0] + " - " + lnk[1])

    print(f"Total number of links: {i}")



#    diagram.dump_file("outfile.drawio")





if __name__ == "__main__":
    main()
