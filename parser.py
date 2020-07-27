#! /usr/bin/python3

import json
import requests
import urllib3
from pprint import pprint
from ciscoconfparse import CiscoConfParse
from asa_object import Name, Network, ICMP, Service
from fmc import FMC, NetworkGroup, PortGroup

def process_obj(object_list, obj_type):
    obj_list = []
    if obj_type == 'Name':
        for obj in object_list:
            name_obj = Name(obj.text)
            obj_list.append(name_obj.to_dict())
        return obj_list
    else:
        for obj in object_list:
            if obj_type == 'Network':
                new_obj = Network(obj.text)
            elif obj_type == 'ICMP':
                new_obj = ICMP(obj.text)
            elif obj_type == 'Service':
                new_obj = Service(obj.text)
            else:
            # Error condition
                print('[E] Error: Unknown type!')
                return
            for child in obj.all_children:
                new_obj.add_child(child.text)
            obj_list.append(new_obj.to_dict())
    return obj_list

def parse_objects(parse):
    names = parse.find_objects(r'^name ')
    name_list = process_obj(names, 'Name')
    
    network_objects = parse.find_objects(r'^object-group network')
    network_list = process_obj(network_objects, 'Network')
    
    icmp_type_objects = parse.find_objects(r'^object-group icmp-type')
    icmp_list = process_obj(icmp_type_objects, 'ICMP')
    
    service_objects = parse.find_objects(r'^object-group service')
    service_list = process_obj(service_objects, 'Service')
    return {
        'hosts':                    name_list,
        'networkgroups':            network_list,
        'icmp':                     icmp_list,
        'portobjectgroups':         service_list
    } 

def create_object(fmc, entry, obj_type):
    if obj_type == 'networkgroups':
        return(NetworkGroup(entry, fmc).obj)
    if obj_type == 'portobjectgroups' or 'icmp':
        return(PortGroup(entry, fmc).obj)

def insert_objects(fmc, objects):
# It might be better to iterate through objects and post them individually rather than in bulk so that individual failures don't
# cause the whole operation to fail
    object_types = {
        'icmp':             'portobjectgroups',
        'hosts':            'hosts',
        'networkgroups':    'networkgroups',
        'portobjectgroups': 'portobjectgroups'
    }
    for obj_type in object_types:
        print('[D] working on ', obj_type)
        data = objects[obj_type]
        for entry in data:
            if obj_type == 'hosts':
                fmc.post(json.dumps(entry), object_types[obj_type])
            else:
                post_data = create_object(fmc, entry, obj_type)
                fmc.post(json.dumps(post_data), object_types[obj_type])
            
    

def main():
    asa_file = input('[*] Please enter the path to your ASA config file: ')
    parse = CiscoConfParse(asa_file, syntax='asa')
    objects = parse_objects(parse)
    fmc_url = input('[*] Please enter the FQDN or IP address of the FMC you want to connect to: ')
    fmc_url = 'https://' + fmc_url
    fmc = FMC(fmc_url)
    fmc.connect()
    #fmc.delete_objects()
    insert_objects(fmc, objects)
    

if __name__ == '__main__':
    main()