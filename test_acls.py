#! /usr/bin/python3

import json
import requests
import urllib3
from pprint import pprint
from ciscoconfparse import CiscoConfParse
from asa_object import Name, Network, ICMP, Service
from fmc import FMC, NetworkGroup, PortGroup
from asa_acl import ACL, ACE   
from pprint import pprint   

def get_zones(fmc, acl, hostname):
    zone_name = acl.get_int_zone(fmc, hostname)
    zone_id = fmc.get_obj_id(zone_name, 'securityzones')
    src_zone =  {
        'objects':  [{
            'name': zone_name,
            'id':   zone_id,
            'type': 'SecurityZone'
        }]
    }
    return src_zone

def push_acls(fmc, acls, hostname):
    for acl in acls:
        count = 0
        policy_name = input('[*] Please enter the name of the policy you would like to insert the new rules into: ')
        policy_id = fmc.get_obj_id(policy_name, 'accesspolicies')
        if policy_id is None:
            print('[*] Creating a new policy: ', policy_name)
            data = {
                'type':             'AccessPolicy',
                'name':             policy_name,
                'defaultAction':    {
                    'action':   'BLOCK'
                }
            }
            policy_id = fmc.post(json.dumps(data), 'accesspolicies')
            print('[D] Created a new policy with ID: ', policy_id)
        for ace in acl.aces:
            count += 1
            zone = get_zones(fmc, acl, hostname)
            access_rule = {
                'action':           ace.action,
                'enabled':          'true',
                'name':             str(acl.name) + '_' + str(count),
                'logBegin':         ace.logging,
                'sourceZones':      zone,
                'destinationPorts': ace.dst_port
            }
            ace_id = fmc.post(access_rule, 'accesspolicies/' + policy_id + '/accessrules')
            print('[D] Created a new access rule: ')
            pprint(access_rule)


def parse_acls(parse):
    acls = []
    aces = parse.find_objects(r'^access-list ')
    access_groups = parse.find_objects(r'^access-group')
    for access_group in access_groups:
        acl = ACL(access_group.text)
        acls.append(acl)
    for ace in aces:
        tokens = ace.text.split(' ')
        acl_name = tokens[1]
        for acl in acls:
            if acl.name == acl_name:
                acl.add_ace(ace.text)
    return acls

def main():
    asa_file = input('[*] Please enter the path to your ASA config file: ')
    hostname = input('[*] Please enter the hostname of the NEW firewall: ')
    parse = CiscoConfParse(asa_file, syntax='asa')
    acls = parse_acls(parse)
    for acl in acls:
        print('[D] ACL created:')
        pprint(acl.to_dict())
    fmc_url = input('[*] Please enter the FQDN or IP address of the FMC you want to connect to: ')
    fmc_url = 'https://' + fmc_url
    fmc = FMC(fmc_url)
    fmc.connect()
    push_acls(fmc, acls, hostname)

if __name__ == '__main__':
    main()