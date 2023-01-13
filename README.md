# YACPS = Yet Another Cisco Parser Script  (aka Cisco parser)

YACPS is a python cli script for extracting various information from configs and diagnostic commands output on cisco network devices (mostly on switches). 
Script use text files with saved configuration and output from commands  - one file per device. It tries to process all files in a given folder. 
File name and order of commands does not matters. 
List of recommended commands provided [here](https://github.com/asha77/cisco_parser/blob/master/README.md#list-of-recommended-commands-to-be-collected-from-devices-required-commands-are-in-bold).
Commands can be done manually on devices, but it is strongly recommended to use automated data collection (another script, utility, ansible, etc.) to do this job. It should made   


## Features
YACPS can:
- check for duplicate devices (based on unique device's serial numbers)
- get inventory from command's output
- get connectivity information based on cdp
- perform some security compliance checking 
- create L1 scheme for [drawio](https://app.diagrams.net)


## Using
1. Put all files with data from switches into one folder (for example, `c:\tmp\cisco`)
2. Get YACPS: 
`git clone https://github.com/asha77/cisco_parser.git`
3. Open command line, cd to directory with YACPS.
4. Run YACPS:
Extract data from all files in directory:
`cisco_parser.py all -e -d "c:\tmp\cisco"`

Check compliance from all files in directory:
`cisco_parser.py all -c -d "c:\tmp\cisco"`

Draw diagram from all files in directory:
`cisco_parser.py all -p -d "c:\tmp\cisco"`

5. Inspect python console messages.
6. Check "output" subfolder in `c:\tmp\cisco` for results.
7. If any problems:
 - try to research problem, correct and provide patch or correction
 - open git ticket with description
 - or write asha77@gmail.com with questions.


## TODO
YACPS still can not:
- understand portchannels
- get actual link speed and type (currently script use port type)
- collect data from switches (it should be separate script or ansible)
- work with Cisco firewalls (they do not use cdp) 
- many things 

## List of recommended commands to be collected from devices (required commands are in bold):
**Cisco Switches**
```
**show interfaces status**
** show int description **
show tech-support
**show int status**
** show int description **
** show int switchport **
** show int trunk **
** show vlan **
** show mac address-table **
show ip arp
show vrrp
show hsrp
** show ip int br **
** show cdp neighbors *
show lldp neighbors
show ip dhcp snooping binding
show spanning-tree
show spanning-tree bridge
show spanning-tree active
show switch detail
show env all
show etherchannel summary
show port-channel summary
** show int transceiver **
show vtp status
show protocols
show ip protocols
show ip route
** show ip route vrf * **
show ip route summary
show ip ospf
show ip ospf neighbor
show ip ospf interface brief
show ip ospf border-routers
show ip ospf database router self-originate
show ip ospf database external self-originate
show ip eigrp neighbors
show ip eigrp interfaces
show ip eigrp topology
show ip bgp summary
show ip bgp vpnv4 all summary
** show log **
show ntp status
show ntp associations
show ntp peer-status
show processes cpu sorted
show processes memory sorted
** show dot1x interface detail **
```

**Cisco Routers**
```
show tech-support
show int status
show int description
show ip interface brief
** show int switchport **
** show int trunk **
** show vlan **
show protocols
show ip protocols
** show cdp neighbors **
show cdp neighbors detail
** show lldp neighbors **
show spanning-tree
show spanning-tree bridge
show spanning-tree active
** show env all **
** show etherchannel summary **
** show port-channel summary **
** show int transceiver **
** show log **
show ip protocols
show ip route
** show ip route vrf * **
show ip route summary
show ip ospf
show ip ospf neighbor
show ip ospf interface brief
show ip ospf border-routers
show ip ospf database router self-originate
show ip ospf database external self-originate
show ip eigrp neighbors
show ip eigrp interfaces
show ip eigrp topology
show ip bgp summary
show ip bgp vpnv4 all summary
```

**Cisco PIX/ASA Firewalls**
```
show tech-support 
show firewall
show inventory 
show ntp
show cry isakmp stats
show cry ipsec stats
show run
show int
show int ip bri
show route
show ospf neighbor
show ospf database 
show xlate
show nat
show asp drop
show access-list
show log
```
