def get_dev_style_from_model(model):
    new_link_style = "endArrow=classic;fillColor=#f8cecc;strokeColor=#FF3399;dashed=1;edgeStyle=entityRelationEdgeStyle;startArrow=diamondThin;startFill=1;endFill=0;strokeWidth=5;"
    building_style = "shape=mxgraph.cisco.buildings.generic_building;html=1;pointerEvents=1;dashed=0;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;"
    router_style = "shape=mxgraph.cisco.routers.atm_router;html=1;pointerEvents=1;dashed=0;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;"
    l2_switch_style = "shape=mxgraph.cisco.switches.workgroup_switch;sketch=0;html=1;pointerEvents=1;dashed=0;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;"
    l3_switch_style = "shape=mxgraph.cisco.switches.layer_3_switch;sketch=0;html=1;pointerEvents=1;dashed=0;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;"
    nexus_switch_style = "shape=mxgraph.cisco.switches.server_switch;sketch=0;html=1;pointerEvents=1;dashed=0;fillColor=#036897;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;"
    ind_switch_style = "shape=mxgraph.cisco.switches.workgroup_switch;sketch=0;html=1;pointerEvents=1;dashed=0;fillColor=#006600;strokeColor=#ffffff;strokeWidth=2;verticalLabelPosition=bottom;verticalAlign=top;align=center;outlineConnect=0;"
    other_device_style = "rounded=1;whiteSpace=wrap;html=1;"

    if ("N9K" in model):
        return [nexus_switch_style, 120, 60]
    elif (("WS-C" in model) or ("C1000" in model) or ("C9200" in model)):
        return [l2_switch_style, 120, 60]
    elif (("C9500" in model) or ("C9300" in model)):
        return [l3_switch_style, 120, 120]
    elif (("28" in model) or ("29" in model) or ("39" in model) or ("433" in model) or ("422" in model)  or ("432" in model)):
        return [router_style, 120, 60]
    elif (("CGS" in model) or ("IE-" in model)):
        return [ind_switch_style, 120, 60]
    else:
        return [other_device_style, 120, 60]


def shorten_ifname(ifname):
    if ("GigabitEthernet" in ifname):
        return ifname.replace("GigabitEthernet", "ge")
    elif ("TenGigabitEthernet" in ifname):
        return ifname.replace("TenGigabitEthernet", "te")
    elif ("FastEthernet" in ifname):
        return ifname.replace("FastEthernet", "fa")
    elif ("TwentyFiveGigE" in ifname):
        return ifname.replace("TwentyFiveGigE", "tfge")
    else:
        return ifname


def filter_devices(devname):
    if ("wap" in devname):
        return False
    elif "AP-" in devname:      # TODO: custom filter
        return False
    elif "esxi" in devname:      # TODO: custom filter
        return False
    else:
        return True


def get_link_style_from_model(ints):
    # TODO: make more link styles based on actual type of transceivers, not only port type
    # default link style
    new_link_style = "endArrow=none;fillColor=#f8cecc;strokeColor=#FF3399;dashed=1;edgeStyle=entityRelationEdgeStyle;startArrow=none;startFill=0;endFill=0;strokeWidth=5;noEdgeStyle=1;"

    # special link styles
    gig_RJ45_link_style = "endArrow=none;fillColor=#f8cecc;strokeColor=default;startArrow=none;startFill=0;endFill=0;strokeWidth=3;rounded=0;endSize=0;startSize=0;edgeStyle=orthogonalEdgeStyle;"
    ten_gig_link_style = "endArrow=none;fillColor=#f8cecc;strokeColor=#FF0000;startArrow=none;startFill=0;endFill=0;strokeWidth=5;rounded=0;endSize=0;startSize=0;edgeStyle=orthogonalEdgeStyle;"
    twe_gig_fast_link_style = "endArrow=none;fillColor=#f8cecc;strokeColor=#009900;startArrow=none;startFill=0;endFill=0;strokeWidth=7;rounded=0;endSize=0;startSize=0;edgeStyle=orthogonalEdgeStyle;"
    fast_link_style = "endArrow=none;fillColor=#f8cecc;strokeColor=default;startArrow=none;startFill=0;endFill=0;strokeWidth=1;rounded=0;endSize=0;startSize=0;jumpSize=0;edgeStyle=orthogonalEdgeStyle;"

    if ("TenGigabitEthernet" in ints):
        return ten_gig_link_style
    elif ("GigabitEthernet" in ints):
        return gig_RJ45_link_style
    elif ("TwentyFiveGigE" in ints):
        return twe_gig_fast_link_style
    elif ("FastEthernet" in ints):
        return fast_link_style
    else:
        return new_link_style



def trunking_analisys():
    # structure of interfaces
    # dev_id, [
    # INTERFACE [0], DESCRIPTION [1], IP_ADDRESS [2], NETMASK [3], ACCESS_VLAN_ID [4]
    # PORT_MODE [5], VOICE_VLAN_ID [6], TRUNK_VLAN_ID [7], NATIVE_VLAN_ID [8]
    # CHANNEL_GROUP [9], PO_MODE [10], AUTH_MODE [11] ]

    # structure of cdps
    # file [0], src dev_id [1], src model [2], src ip [3], src_port [4],
    # dst dev_id [5], dst model [6], dst IP [7], dst port [8]

    # structure of devices
    # hostname [0], mng_ip [1], domain [2], model [3], serial [4], sw_ver [5]

    for dev in all_devices:
        for link in all_cdps:

            num = 0
            if link[1] == dev[0]:
                num = num + 1
            if num:
                print("Fake")
