from fmc import FMC
from .ace import ACE
import json

class ACL:
# An ACL is a collection of ACEs.  An ACL has an associated name, direction (in or out) and interface
# In Firepower, ACLs also have source and destination zones that we will need to figure out.  Foe now
# we will simply assume that the source zone is the interface and destination zone is 'any'

    def __init__(self, line):
        tokens = line.split(' ')
        #self.fmc = fmc
        self.name = tokens[1]
        print('[D} ACL Created: ', self.name)
        self.dir = tokens[2]
        self.interface = tokens[4]
        self.aces = []
        #self.src_zone = self.get_int_zone(self.interface)
        #self.dst_zone = 'any'

    def to_dict(self):
        return {
            'name':         self.name,
            'direction':    self.dir,
            'interface':    self.interface,
            'aces':         self.aces
        }

    def __str__ (self):
        return (self.name + ': ' + self.dir + ', ' + self.interface)

    def get_int_zone(self, fmc, dev_name):
    # This helper method looks up the interface on the FMC and returns the id and name for the
    # associated zone.
        zones = {
            'MNK-PORTAL-OUTER-HA':  {
                'outside':  'MNK-PORTAL_Outside',
                'inside':   'MNK-PORTAL_Outer_DMZ',
                'dmz1':     'MNK-PORTAL_DMZ1',
            },
            'MNK-PORTAL-INNER-HA':  {
                'outside':  'MNK-PORTAL_Outer_DMZ',
                'inside':   'MNK-PORTAL_Inside',
                'dmz1':     'MNK-PORTAL_DMZ1'
            }
        }
        return zones[dev_name][self.interface]
        # devices = json.loads(fmc.get('devicerecords'))
        # for device in devices:
        #     if device['name'] == dev_name:
        #         dev_id = device['id']
        #         print('[D] Found device - ', dev_id)
        # zones = json.loads(fmc.get('devicerecords/' + dev_id + '/physicalinterfaces'))
        # for zone in zones:
        #     for z_interface in zone['interfaces']:
        #         if z_interface['ifname'] == self.interface:
        #             zone_id = zone['securityZone']['id']
        # zone_obj = {
        #     'name': zone_name,
        #     'id':   zone_id
        # }
        # return zone_obj   

    def add_ace(self, text):
        self.aces.append(ACE(text))