# YACPS = Yet Another Cisco Parser Script 

YACPS is a python cli script used to extract various information from configs and diagnostic commands output from cisco network devices (mainly switches). 
Script use text files with configuration asnd result of commands executed on devices - one file per device. It tries to process all files in a given folder. 
File name and order of commands does not matters. 


## Features
YACPS can:
- get inventory from command's output
- get connectivity information based on cdp
- perform some security compliance checking 
- create L1 scheme for [drawio](https://app.diagrams.net)
- check for duplicate devices (based on unique device's serial numbers)

## TODO
YACPS still can not:
- understand portchannels
- get actual link speed and type (currently script use port type)
- many things

## List of recommended commands to be collected from devices (required commands are in bold):
** Cisco Switches
```
show tech-support
**show int status**
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

** Cisco Routers **
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

** Cisco PIX/ASA Firewalls **
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
