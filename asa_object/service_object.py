class Service:

# A service object represents a network service or port. Confusingly, service objects can either be a service, where each port or range has a specified
# protocol, or consists of port-objects.  If the service is composed of port-objects, the protocol is specified when creating the service object.  
# Example 1:
# object-group service my-service tcp
#   port-object eq http
#
# Example 2:
# object-group service my-service2
#   service-object tcp eq http
#   service-object udp range 40000-50000

    ASA_PORT_MAP = {
            'aol': '5120',
            'bgp': '179',
            'chargen': '19',
            'cifs': '3020',
            'citrix-ica': '1494',
            'cmd': '514',
            'ctiqbe': '2748',
            'daytime': '13',
            'discard': '9',
            'domain': '53',
            'echo': '7',
            'exec': '512',
            'finger': '79',
            'ftp': '21',
            'ftp-data': '20',
            'gopher': '70',
            'h323': '1720',
            'hostname': '101',
            'http': '80',
            'https': '443',
            'ident': '113',
            'imap4': '143',
            'irc': '194',
            'kerberos': '88',
            'klogin': '543',
            'kshell': '544',
            'ldap': '389',
            'ldaps': '636',
            'login': '513',
            'lotusnotes': '1352',
            'lpd': '515',
            'netbios-ssn': '139',
            'nfs': '2049',
            'nntp': '119',
            'pcanywhere-data': '5631',
            'pim-auto-rp': '496',
            'pop2': '109',
            'pop3': '110',
            'pptp': '1723',
            'rsh': '514',
            'rtsp': '554',
            'sip': ' 5060',
            'smtp': '25',
            'sqlnet': '1522',
            'ssh': '22',
            'sunrpc': '111',
            'tacacs': '49',
            'talk': '517',
            'telnet': '23',
            'uucp': '540',
            'whois': '43',
            'www': '80'
        }

    def __init__(self, line):
        tokens = line.split(' ')
        self.proto = None
        self.name = tokens[2]
        if len(tokens) > 3:
            self.proto = tokens[3]
        self.description = None
        self.internal_objects = []

    def test_numeral(self, string):
        try:
            int(str(string))
            return True
        except ValueError:
            return False
    
    def add_port_object(self, port):
        if self.test_numeral(port):
            port_object = Port_Object(port)
        else:
            port_object = Port_Object(self.ASA_PORT_MAP[str(port)])
        self.internal_objects.append(port_object)

    def add_range_object(self, proto, start_port, end_port):
        range_object = Range_Object(proto, start_port, end_port)
        self.internal_objects.append(range_object)

    def add_group_object(self, group_object):
    # It's possible to nest objects together
        group = Group_Object(group_object)
        self.internal_objects.append(group)

    def add_service_child(self, proto, port):
        if self.test_numeral(port) or proto == 'icmp':
            service_child = Service_Child(proto, port)
        else:
            service_child = Service_Child(proto, self.ASA_PORT_MAP[str(port)])  
        self.internal_objects.append(service_child)
    
    def add_child(self, line):
        tokens = line.split(' ')
        if tokens[0] == 'description':
            desc = line.split('description ')
            self.description = desc[1]
        elif tokens[1] == 'group-object':
            self.add_group_object(tokens[2])
        elif tokens[1] == 'port-object':
            self.add_port_object(tokens[3])
        elif tokens[1] == 'service-object' and tokens[3] == 'range':
            self.add_range_object(tokens[2], tokens[4], tokens[5])
        elif tokens[2] == 'ip':
            print('[E] IP not supported in port or service groups')
        elif tokens[2] =='icmp':
            self.add_service_child(tokens[2], tokens[3])
        elif tokens[1] == 'service-object':
            self.add_service_child(tokens[2], tokens[4])

    def get_children(self):
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
            'Type':         'service-group',
            'Name':         self.name,
            'Description':  self.description,
            'Protocol':     self.proto,
            'Children':     children
        }

    def __str__(self):
        string = self.name + ' (' + self.description + '): '
        for obj in self.internal_objects:
            string += str(obj) + ', '
        return string


class Port_Object(Service):
# Sub-class to define port objects as children
    
    def __init__(self, port):
        self.port = port
    
    def __str__(self):
        return(self.port)

    def to_dict(self):
        return {
            'Type': 'port-object',
            'Port': self.port
        }

class Range_Object(Service):
# Sub-class to define range objects as children

    def __init__(self, proto, start_port, end_port):
        self.proto = proto
        self.start_port = start_port
        self.end_port = end_port

    def __str__(self):
        return(self.proto + ': ' + self.start_port + '-' + self.end_port)
    
    def to_dict(self):
        return {
            'Type':     'range-object',
            'Protocol': self.proto,
            'Start':    self.start_port,
            'End':      self.end_port
        }

class Service_Child(Service):
# Sub-class to defince service objects as children

    def __init__(self, proto, port):
        self.proto = proto
        self.port = port
    
    def __str__(self):
        return(self.proto + '/' + self.port)
    
    def to_dict(self):
        return {
            'Type':     'service-object',
            'Protocol': self.proto,
            'Port':     self.port
        }

class Group_Object(Service):
# Sub class to represent group objects.  Group objects are simply nested groups, so all we do here is record the name

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return(self.name)
    
    def to_dict(self):
        return {
            'Type': 'group-object',
            'Name': self.name
        }