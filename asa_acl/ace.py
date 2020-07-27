import ipaddress
import json
from pprint import pprint

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
    'isakmp': '500',
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
    'ntp':  '123',
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
    'syslog': '514',
    'ssh': '22',
    'sunrpc': '111',
    'tacacs': '49',
    'talk': '517',
    'telnet': '23',
    'uucp': '540',
    'whois': '43',
    'www': '80'
}

class ACE:
# In ASA, each ACE represents one line of an ACL.  

    def __init__(self, text):
        tokens = text.split(' ')
        self.remark = None
        self.dst_port = 'any'
        if tokens[2] == 'remark':
            remark = text.split('remark')
            self.remark = remark[1]
            self.action = None
            self.src = None
            self.src_mask = None
            self.dst = None
            self.dst_mask = None
            self.src_port = None
            self.dst_port = None
            self.proto = None
            self.logging = False
            return
        self.action = tokens[3]
        self.proto = tokens[4]
        if tokens[5] == 'host':
            self.src = tokens[6]
            self.src_mask = '255.255.255.255'
        elif tokens[5] == 'any':
            self.src = 'any'
            self.src_mask = None
        elif self.is_ip_addr(tokens[5]) is not None and self.is_ip_addr(tokens[6]) is not None:
            self.src = tokens[5]
            self.src_mask = tokens[6]
        elif tokens[5] == 'object-group':
            self.src = tokens[6]
            self.src_mask = None
        else:
            self.src = tokens[6]
            self.src_mask = tokens[7]
        if tokens[6] == 'host':
            self.dst = tokens[7]
            self.dst_mask = '255.255.255.255'
        elif tokens[7] == 'host':
            self.dst = tokens[8]
            self.dst_mask = '255.255.255.255'
        elif tokens[6] == 'any' or tokens[7] == 'any':
            self.dst = 'any'
            self.dst_mask = None
        elif self.is_ip_addr(tokens[7]) is not None and self.is_ip_addr(tokens[8]) is not None:
            self.dst = tokens[7]
            self.dst_mask = tokens[8]
        elif tokens[6] == 'object-group':
            self.dst = tokens[7]
            self.dst_mask = None
        elif tokens[7] == 'object-group':
            self.dst = tokens[8]
            self.dst_mask = None
        else:
            self.dst = tokens[7]
            self.dst_mask = tokens[8]
        if len(tokens) > 9:
            if tokens[9] == 'eq':
                if self.test_numeral(tokens[10]):
                    self.dst_port = tokens[10]
                else:
                    self.dst_port = ASA_PORT_MAP[tokens[10]]
            elif tokens[9] == 'range':
                if self.test_numeral(tokens[10]):
                    self.dst_port = tokens[10] + '-' + tokens[11]
                else:
                    self.dst_port = ASA_PORT_MAP[tokens[10]] + '-' + ASA_PORT_MAP[tokens[11]]
            elif tokens[9] == 'object-group':
                self.dst_port = tokens[10]
        if tokens[len(tokens) - 1] == 'log':
            self.logging = True
        else:
            self.logging = False
        self.convert_action

    def convert_action(self):
        if self.action == 'permit':
            self.action = 'ALLOW'
        else:
            self.action = 'BLOCK'
      
    def to_dict(self):
        return {
            'remark':       self.remark,
            'action':       self.action,
            'src':          self.src,
            'src_mask:':    self.src_mask,
            'dst':          self.dst,
            'dst_mask':     self.dst_mask,
            'dst_port':     {'objects': [
                                self.dst_port,
                            ]},
            'proto':        self.proto,
            'logging':      self.logging
        }
    
    def __str__(self):
        return json.loads(self.to_dict)

    def is_ip_addr(self, ip):
        try:
            answer = ipaddress.ip_address(ip)
            return answer
        except ValueError:
            return None
    
    def test_numeral(self, string):
        try:
            int(str(string))
            return True
        except ValueError:
            return False