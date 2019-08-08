from pprint import pprint
import ipaddress

def is_ip_addr(ip, mask):
    try:
        if mask is None:  
                answer = ipaddress.ip_address(ip)
                return answer
        else:
                answer = ipaddress.ip_network(ip + '/' + mask)
                return answer
    except ValueError:
                return None

class NetworkGroup():

# Nested objects and those that have multiple entires need to either have those values stored as UUIDs (if the already)
# exist) or as literals
#
# We start off by getting a list of relevant entities from the FMC to check against

    def __init__(self, data, fmc):
        self.literals = []
        self.objects = []
        for child in data['Children']:
            if child['Type'] == 'host':
                value = is_ip_addr(child['IP'], None)
                if value is not None:
                    literal_data = {
                        'type':     'Host',
                        'value':    child['IP']
                    }
                    print('[D] Created a new host literal: ', literal_data)
                    self.literals.append(literal_data)
                else:
                    obj_id = fmc.get_obj_id(child['IP'], 'hosts')
                    if obj_id is not None:
                        obj_data = {
                            'type': 'Host',
                            'id':   obj_id
                        }
                        self.objects.append(obj_data)
                    else:
                        print('[E] Predefined object identified but can\'t be found on FMC!')
                        return None
            elif child['Type'] == 'subnet':
                value = is_ip_addr(child['Subnet'], child['Mask'])
                if value is not None :
                    literal_data = {
                        'type': 'Network',
                        'value': value.with_prefixlen
                    }
                    print('[D] Created a new subnet literal: ', literal_data)
                    self.literals.append(literal_data)
                else:
                    if child['Mask'] == '255.255.255.255':
                        obj_id = fmc.get_obj_id(child['Subnet'], 'hosts')
                    else:
                        obj_id = fmc.get_obj_id(child['Subnet'], 'subnets')
                    if obj_id is not None:
                        obj_data = {
                            'type': 'Network',
                            'id':   obj_id
                        }
                        self.objects.append(obj_data)
                    else:
                        print('[E] Predefined object identified but can\'t be found on FMC!')
                        return None
        self.obj = {
            'name':         data['Name'],
            'description':  data['Description'],
            'literals':     self.literals,
            'objects':      self.objects,
            'type':         'NetworkGroup'
        }
        print('[D] Created new NetGroup object: ')
        pprint(self.obj)

        
class PortGroup:
# Port groups represent collections of services bound to specific ports in a given protocol.  Unlike the ASA,
# ICMP groups are simply treated as Port Groups on FMC.

    def __init__(self, data, fmc):
        self.objects = []
        self.fmc = fmc
        for child in data['Children']:
            if child['Type'] == 'port-object':
                obj_id = self.create_port_object(data['Name'], data['Protocol'], child['Port'])
            elif child['Type'] == 'service-object':
                obj_id = self.create_port_object(data['Name'], child['Protocol'], child['Port'])
            elif child['Type'] == 'range-object':
                port = child['Start'] + '-' + child['End']
                obj_id = self.create_port_object(data['Name'], child['Protocol'], port)
            elif child['Type'] == 'group-object':
                print('[E] nested objects not yet implemented!')
            object_data = {
                'type': 'ProtocolPortObject',
                'id':   obj_id
            }
            self.objects.append(object_data)
        self.obj = {
            'name':         data['Name'],
            'description':  data['Description'],
            'objects':      self.objects,
            'type':         'PortObjectGroup'
        }
        print('[D] Created new PortObjectGroup object: ')
        pprint(self.obj)

    def convert_to_int(self, port):
        if '-' in port:
            return port
        else:
            try:
                r = int(str(port))
                return r
            except ValueError:
                return port


    def create_port_object(self, name, protocol, port):
        obj_port = self.convert_to_int(port)
        post_data = {
            'name':     str(name) + '_' + str(protocol) + '_' + str(port),
            'port':     obj_port,
            'protocol': protocol.upper(),
            'type':     'ProtocolPortObject',
        }
        ident = self.fmc.post(post_data, 'protocolportobjects')
        print('[D] Created a new PortProtocol object with ID ', ident)
        pprint(post_data)
        return ident

class ICMPGroup(PortGroup):

    def __init__(self, data, fmc):
        print('Not yet implemented')