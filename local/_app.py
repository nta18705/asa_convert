#! /usr/bin/python3

# Initial test to check whether the data structures I've defined actually work.

import sys
from asa_object import Name, Network, ICMP, Service

def create_name_object(line):
    tokens = line.split(' ')
    if len(tokens) == 3:
        print('[D] Created object: ', tokens[1], ' ', tokens[2])
        obj = Name(tokens[1], tokens[2], None)
    elif len(tokens) > 3:
        description = line.split('description')
        print('[D] Created object: ', tokens[1], ' ', tokens[2], ' ', description[1])
        obj = Name(tokens[1], tokens[2], description[1])
    return(obj)

def create_network_object(line):
    print ('[D] I would have created a network object here')

def create_icmp_object(line):
    print ('[D] I would have created an icmp object here')

def create_service_object(line):
    print ('[D] I would have created a service object here')

def main():
    name_objects = []
    network_objects = []
    icmp_type_objects = []
    service_objects = []
    asa_file = input('[*] Please enter the path to your ASA config file: ')
    with open(asa_file, newline='') as input_file:
        for line in input_file:
            tokens = line.split(' ')
            if tokens[0] == 'name':
                name_objects.append(create_name_object(line))
            elif tokens[0] == 'object-group':
                if tokens[1] == 'network':
                    network_objects.append(create_network_object(line))
                elif tokens[1] == 'icmp-type':
                    icmp_type_objects.append(create_icmp_object(line))
                elif tokens[1] == 'service':
                    service_objects.append(create_service_object(line))


if __name__ == '__main__':
    main()