from fmc import FMC

class ACL:
# An ACL is a collection of ACEs.  An ACL has an associated name, direction (in or out) and interface
# In Firepower, ACLs also have source and destination zones that we will need to figure out.  Foe now
# we will simply assume that the source zone is the interface and destination zone is 'any'

    def __init__(self, fmc, name, direction, interface):
        self.fmc = fmc
        self.name = name
        print('[D} ACL Created: ', self.name)
        self.dir = direction
        self.interface = interface
        self.aces = []
        self.src_zone = self.get_int_zone(self.interface)
        self.dst_zone = 'any'

    def get_int_zone(self, interface):
    # This helper method looks up the interface on the FMC and returns the id and name for the
    # associated zone.
        zones = self.fmc.get('securityzones')
        for zone in zones:
            for z_interface in zone['interfaces']:
                if z_interface['name'] == interface:
                    zone_name = zone['name']
                    zone_id = zone['id']
        zone_obj = {
            'name': zone_name,
            'id':   zone_id
        }
        return zone_obj   