class Network:

# A network object is a type of object group containing network objects, i.e. subnet and host objects
# Example:
# object-group network my-object

        def __init__(self, line):
                tokens = line.split(' ')
                self.name = 'MNK-PORTAL_' + tokens[2]
                self.description = 'None'
                self.internal_objects = []
        
        def add_host_object(self, ip):
                host_object = Host_Object(ip)
                self.internal_objects.append(host_object)
        
        def add_subnet_object(self, ip, mask):
                subnet_object = Subnet_Object(ip, mask)
                self.internal_objects.append(subnet_object)
        
        def add_child(self, line):
                tokens = line.split(' ')
                if tokens[2] == 'host':
                        self.add_host_object(tokens[3])
                elif tokens[1] == 'description':
                        desc = line.split('description ')
                        self.description = desc[1]
                else:
                        self.add_subnet_object(tokens[2], tokens[3])
        
        def get_children(self):
        # Iterates through the object-group children and returns a list of children as dicts
                children = []
                obj = {}
                for child in self.internal_objects:
                        obj = child.to_dict()
                        children.append(obj)
                return children
        
        def to_dict(self):
        # Converts the object-group to a dict
                children = self.get_children()
                return {
                        'Type': 'NetworkGroup',
                        'Name': self.name,
                        'Description': self.description,
                        'Children': children
                }

        def __str__(self):
                string = self.name + ' (' + self.description + '): '
                for obj in self.internal_objects:
                        string += str(obj) + ', '
                return string

class Host_Object(Network):

# A host object is used within object groups to map a /32 IP address into the object group
# Example:
# object-group network my-object
#   network-object host 10.1.1.1

        def __init__(self, ip):
                self.ip = ip
        
        def __str__(self):
                return (str(self.ip))
        
        def to_dict(self):
                return {
                        'Type': 'host',
                        'IP':   self.ip
                }


class Subnet_Object(Network):

# Subnet objects are used within object groups to define a subnet that should be mapped into the object-group
# Example:
# object-group network my-object
#   network-object 192.168.0.0 255.255.0.0

        def __init__(self, ip, mask):
                self.ip = ip
                self.mask = mask

        def __str__(self):
                return (self.ip + ', ' + self.mask)
        
        def to_dict(self):
                return {
                        'Type': 'subnet',
                        'Subnet': self.ip,
                        'Mask': self.mask
                }