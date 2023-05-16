import re

vendor_id_vendor = {
    'cisco': 'Cisco Systems Inc.',
    'huawei': 'Huawei Enterprise',
    'hpe': 'Hewlett-Packard Enterprise',
    'hpe_aruba': 'Hewlett-Packard Enterprise (Aruba)',
    'hpe_comware': 'Hewlett-Packard Enterprise (Comware)',
    'arista': 'Arista Networks',
}



def vendor_id_to_vendor(vendor_id):
    '''
    Assign vendor name based on vendor id
    '''

    try:
        vendor = vendor_id_vendor[vendor_id]
    except KeyError as error:
        # можно также присвоить значение по умолчанию вместо бросания исключения
        print("No suitable vendor for vendor_id {}".format(vendor_id))
        vendor = ""
    return vendor


def obtain_device_vendor_id(config):
    '''
    Extract device vendor: cisco, arista, huawei, hpe
    '''

    match = re.search("Copyright \(c\) [0-9]{4}-[0-9]{4} by Cisco Systems, Inc.", config)
    if match:
        return 'cisco'

    match = re.search("Technical Support: http://www.cisco.com/techsupport", config)
    if match:
        return 'cisco'

    match = re.search("TAC support: http://www.cisco.com/tac", config)
    if match:
        return 'cisco'

    match = re.search("Cisco Adaptive Security Appliance Software Version", config)
    if match:
        return 'cisco'

    match = re.search("Huawei Versatile Routing Platform Software", config)
    if match:
        return 'huawei'

    match = re.search("hpStack_WC Configuration Editor; Created on release", config)
    if match:
        return 'hpe_aruba'

    match = re.search("Configuration Editor; Created on release", config)
    if match:
        return 'hpe'

    match = re.search("!System Description \"HPE OfficeConnect Switch", config)
    if match:
        return 'hpe_comware'


    match = re.search("version \d*.\d*, Release \s*", config)
    if match:
        return 'hpe_comware'


    match = re.search("D-Link Corporation. All rights reserved.", config)
    if match:
        return 'dlink'

    match = re.search("Last configuration change at", config)
    if match:
        return 'cisco'

    match = re.search("Manufacturer's Name.............................. Cisco Systems Inc.", config)
    if match:
        return 'cisco'

    match = re.search("Arista vEOS", config)
    if match:
        return 'arista'

    return "Not Found"


def obtain_device_family(vendor, config):
    '''
    Extract device family: cisco_catalyst, cisco_isr, cisco_nexus, arista_switch, cisco_vrouter, huawei_ce, huawei_s, huawei_ar
    '''
    if vendor == 'cisco':
        match = re.search("Model\s+\wumber\s*:\s+(.*)", config)
        if match:
            return 'cisco_catalyst'
        else:
            match = re.search("\wisco\s+(\S+)\s+.*\s+(with)*\d+K\/\d+K\sbytes\sof\smemory.", config)
            if match:
                return 'cisco_isr'
            else:
                match = re.search("\s+cisco Nexus9000 (.*) Chassis", config)
                if match:
                    return 'cisco_nexus'
                else:
                    match = re.search("ROM: Bootstrap program is Linux", config)
                    if match:
                        return 'cisco_vrouter'

    if vendor == 'arista':
        match = re.search("Arista vEOS", config)
        if match:
            return 'arista_switch'

    if vendor == 'huawei':
        match = re.search('(Quidway|HUAWEI)\s(\S+)\s+Routing\sSwitch\S*', config)
        if match:
            return 'huawei_s'
        else:
            match = re.search('HUAWEI\sCE(\S+)\s+uptime\S*', config)
            if match:
                return 'huawei_ce'
            else:
                match = re.search('Huawei\s(\S+)\s+Router\s\S*', config)
                if match:
                    return 'huawei_ar'

    if vendor == 'hpe' or vendor == 'hpe_comware' or vendor == 'hpe_aruba':
        match = re.search(';\s(\S+)\sConfiguration\sEditor;', config)
        if match:
            return 'hpe_aruba_switch'
        else:
            match = re.search('System Description "HPE(.+)', config)
            if match:
                return 'hpe_comware_switch'
            else:
                match = re.search('\sversion\s(\S+),\sRelease\s(\S+)\n#\n\ssysname\s(\S+)', config)
                if match:
                    return 'hpe_switch2'
    return "Not Found"


def obtain_device_os(vendor_id, config):
    '''
    Extract software family from show version: cisco_ios_xe, cisco_ios, cisco_ios_xr, arista_eos, cisco_nx_os, huawei_vrp, aruba_aoscx
    '''
    if vendor_id == 'cisco':
        match = re.search("Cisco IOS.XE .oftware", config)
        if match:
            return 'cisco_ios_xe'
        else:
            match = re.search("Cisco Nexus Operating System", config)
            if match:
                return 'cisco_nx_os'
            else:
                match = re.search("Cisco IOS Software", config)
                if match:
                    return 'cisco_ios'

    if vendor_id == 'arista':
        match = re.search("Arista", config)
        if match:
            return 'arista_eos'

    if vendor_id == 'huawei':
        match = re.search("Huawei Versatile Routing Platform", config)
        if match:
            return 'huawei_vrp'

    if vendor_id == 'hpe' or vendor_id == 'hpe_comware' or vendor_id == 'hpe_aruba':
        match = re.search(';\s(\S+)\sConfiguration\sEditor;', config)
        if match:
            return 'aruba_aos-s'
        else:
            match = re.search('!System\sDescription\s"HPE(.+)', config)
            if match:
                return 'hpe_os'
            else:
                match = re.search('\sversion\s(\S+),\sRelease\s(\S+)\n#\n\ssysname\s(\S+)', config)
                if match:
                    return 'hpe_comware'

    return "Not Found"


def get_hp_model_from_pn(partnumber):
    if partnumber == 'J9781A':
        return 'HPE Aruba 2530-48'
    if partnumber == 'J9775A':
        return 'HPE Aruba 2530-48G'
    if partnumber == 'J9773A':
        return 'HPE Aruba 2530-24G-PoE+'
    if partnumber == 'J9782A':
        return 'HPE Aruba 2530-24'
    if partnumber == 'JL385A':
        return 'HPE 1920S-24G-2SFP-PoE+'
    if partnumber == 'J9774A':
        return 'HPE 2530-8G-PoE+'
    if partnumber == 'J9783A':
        return 'HPE Aruba 2530-8FE'
    if partnumber == 'J9780A':
        return 'HPE Aruba 2530-8-PoE+'
    if partnumber == 'J9776A':
        return 'HPE Aruba 2530-24G-PoE+'
    if partnumber == 'J9772A':
        return 'HPE Aruba 2530-48G-PoE+'
    if partnumber == 'J9778A':
        return 'HPE Aruba 2530-48G-PoE+'
    if partnumber == 'J9779A':
        return 'HPE Aruba 2530-24-PoE+'
    if partnumber == 'hpStack_WC':
        return 'HPE Aruba-VSF-2930F'
    else:
        return 'HP unknown'
