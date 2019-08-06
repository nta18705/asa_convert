#! /usr/bin/python3

from ciscoconfparse import CiscoConfParse
from asa_object import Name, Network, ICMP, Service

def process_obj(object_list, obj_type):
    obj_list = []
    if obj_type == 'Name':
        for obj in object_list:
            name_obj = Name(obj.text)
            obj_list.append(name_obj.to_dict())
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

def main():
    asa_file = input('[*] Please enter the path to your ASA config file: ')
    parse = CiscoConfParse(asa_file, syntax='asa')
    names = parse.find_objects(r'^name ')
    name_list = process_obj(names, 'Name')
    print('[D] Names created: ', name_list)
    network_objects = parse.find_objects(r'^object-group network')
    network_list = process_obj(network_objects, 'Network')
    print('[D] Networks created: ', network_list)
    icmp_type_objects = parse.find_objects(r'^object-group icmp-type')
    icmp_list = process_obj(icmp_type_objects, 'ICMP')
    print('[D] ICMP Types created: ', icmp_list)
    service_objects = parse.find_objects(r'^object-group service')
    service_list = process_obj(service_objects, 'Service')
    print('[D] Services created: ', service_list)

if __name__ == '__main__':
    main()