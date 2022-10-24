import re

def obtain_stack_members(config):
    match = re.findall("ip address unit (.*)", config)
    if match:
        return len(match)
    else:
        return None

def obtain_hostname(config):
    '''
    Extract device hostname
    '''

    match = re.search("hostname (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not Found"


def obtain_model(config):
    '''
    Extract model number
    '''

    match = re.search("Model \wumber\ *: (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        match = re.search("\wisco (.*) \(.*\) \w* (with )*\d+K\/\d+K bytes of memory.", config)
        if match:
            return match.group(1).strip()
        return "Not Found"

def obtain_serial(config):
    '''
    Extract serial number
    '''

    match = re.search("\wystem \werial \wumber\ *: (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        match = re.search("\s*\wrocessor \woard ID (.*)", config)
        if match:
            return match.group(1).strip()
        return "Not Found"

def obtain_domain(config):
    '''
    Extract domain name
    '''

    match = re.search("ip domain[\s\S]name (.*)", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not set"


def obtain_software_version(config):
    '''
    Extract software version
    '''

    match = re.search("Version (.*),", config)
    if match:
        return match.group(1).strip()
    else:
        return "Not Found"


def obtain_mng_ip_from_config(filename):
    '''
    Extract mng ip - TODO: need to rethink - return just first ip on interface !!!!!
    '''

    match = re.search(" ip address ([0-9]+.[0-9]+.[0-9]+.[0-9]+)", filename)
    if match:
        return match.group(1).strip()
    else:
        return "Not Found"

def fill_devinfo_from_config(config):
    devinfo = [obtain_hostname(config),
               obtain_mng_ip_from_config(config),
               obtain_domain(config),
               obtain_model(config),
               obtain_serial(config),
               obtain_software_version(config)]
    return devinfo