class Name:

# This class represents a name object in the ASA config
# name objects can be considered as an alias for an IP address that can be used later in the config
# e.g. name test-name 1.1.1.1
# Names in ASA are analogous to Hosts in FMC
    
    def __init__(self, line):
        tokens = line.split(' ')
        self.description = 'None'
        self.name = tokens[2]
        self.ip = tokens[1]
        if len(tokens) > 3:
            desc = line.split('description ')
            self.description = desc[1]
    
    def to_dict(self):
        return {
            'type': 'Host',
            'name': self.name,
            'description': self.description,
            'value': self.ip
        }

    def __str__(self):
        return (self.name + ' (' + self.description + '): ' + self.ip)
