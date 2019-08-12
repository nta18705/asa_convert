class ICMP:

# This class represents an ICMP type object in an ASA config
# ICMP type objects consist of groups of ICMP types that are given a name and can be used later in the config for example, ACLs.
# Example:
#   object-group icmp-type My_ICMP_Type
#       icmp-object echo-reply
#       icmp-object time-exceeded

    def __init__(self, line):
        tokens = line.split(' ')
        self.name = tokens[2]
        self.internal_objects = []
        self.description = None
    
    def add_child(self, line):
        tokens = line.split(' ')
        if tokens[1] == 'group-object':
            icmp_object = ICMP_Group(tokens[2])
        else:
            icmp_object = ICMP_Object(tokens[2])
        self.internal_objects.append(icmp_object)
    
    def add_group_object(self, group_object):
    # It's possible to nest objects together :/
        group = ICMP_Group(group_object)
        self.internal_objects.append(group)

    def get_children(self):
        children = []
        obj = {}
        for child in self.internal_objects:
            obj = child.to_dict()
            children.append(obj)
        return(children)
    
    def to_dict(self):
    # Converts the object-group to a dict
        children = self.get_children()
        return {
            'Type':         'icmp-group',
            'Name':         self.name,
            'Description':  self.description,
            'Children':     children
        }

    def __str__(self):
        string = self.name + ': '
        for obj in self.internal_objects:
            string += str(obj) + ', '
        return string   


class ICMP_Object(ICMP):
    def __init__(self, icmp_type):
        self.icmp_type = icmp_type
    
    def __str__(self):
        return(str(self.icmp_type))
    
    def to_dict(self):
        return {
            'Type': 'icmp-object',
            'Protocol': self.icmp_type
        }

class ICMP_Group(ICMP):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return(self.name)

    def to_dict(self):
        return {
            'Type': 'icmp-group-object',
            'Name': self.name
        }