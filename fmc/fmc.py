import json
import requests
import ipaddress
import urllib3
import getpass
from pprint import pprint

class FMC:
# Class to allow connection to the FMC and run various different operations

    def __init__(self, url):
        self.url = url
        urllib3.disable_warnings()

    def get_auth(self, auth, url):
        # Request headers
        headers = {
                'Content-Type':'application/json',
                'accept':'application/json'
                }
        token_response = requests.post(url, auth=auth, data=None, headers=headers, verify=False)
        if token_response.ok:
            return token_response
        else:
            print('[*] Error: ', token_response.raise_for_status())
            return -1

    def connect(self):
        auth = (input('username: '), getpass.getpass('password: '))
        auth_url = self.url + '/api/fmc_platform/v1/auth/generatetoken'
        print('[*] Connecting to ', auth_url)
        token_response = self.get_auth(auth, auth_url)
        if token_response != -1:
            self.auth_token = token_response.headers['X-auth-access-token']
            self.refresh_token = token_response.headers['X-auth-refresh-token']
            self.domain_uuid = token_response.headers['DOMAIN_UUID']
            print('Auth token: ', self.auth_token)
            print('Refresh token: ', self.refresh_token)
            print('Domain UUID: ', self.domain_uuid)
        else:
            print('[*] Error getting auth token (check credentials)')
        return {
            'auth_token':       self.auth_token,
            'refresh_token':    self.refresh_token,
            'domain_uuid':      self.domain_uuid
        }
    
    def post(self, data, obj_type):
    # Takes in json data and posts it to the FMC at the url passed.
    # Object types currently supported:
    #   - ICMPv4 Objects
    #   - Network groups
    #   - Ranges
    #   - FQDNs
    #   - Ports
    #   - Port groups (including ICMP groups)
    # Access policies and policy rules now supported.

        headers = {
                'Content-Type' : 'application/json',
                'X-auth-access-token' : self.auth_token,
                }
        r = None
        if 'accessrules' in obj_type or obj_type == 'accesspolicies':
            post_url = self.url + '/api/fmc_config/v1/domain/' + self.domain_uuid + '/policy/' + obj_type
        else:
            post_url = self.url + '/api/fmc_config/v1/domain/' + self.domain_uuid + '/object/' + obj_type
        try:
            r = requests.post(post_url, data=data, headers=headers, verify=False)
            print('[*] POST Response: ', r.raise_for_status())
            response_data = json.loads(r.text)
            print('[D] Response text: ')
            pprint(response_data)
            return response_data['id']
        except requests.exceptions.HTTPError as err:
            print('[*] Error in POST operation: ', str(err))
            pprint(json.loads(r.text))
        finally:
            if r: r.close()

    def get(self, object_type):
    # Runs a GET request against the passed URL and returns the collected data
    # Returns None on error
        headers = {
            'Content-Type' : 'application/json',
            'X-auth-access-token' : self.auth_token,
            }
        r = None
        response_data = {}

        try:
            # Entertainingly, the API seems to default to only returing 25 items by default (this is not documented)
            # So - we pass a parameter into the URL saying that we want 65535 entries back (limit=65535)
            if object_type == 'accesspolicies' or object_type == 'accessrules':
                get_url = self.url + '/api/fmc_config/v1/domain/' + self.domain_uuid + '/policy/' + object_type + '?limit=65535'
            elif 'devicerecords' in object_type:
                get_url = self.url + '/api/fmc_config/v1/domain/' + self.domain_uuid + '/devices/' + object_type + '?limit=65535'
            else:
                get_url = self.url + '/api/fmc_config/v1/domain/' + self.domain_uuid + '/object/' + object_type + '?limit=65535'
            print('[*] Gettting data from ', get_url)
            r = requests.get(get_url, headers=headers, verify=False)
            response_data = json.loads(r.content)
            if 'items' in response_data:
                return response_data
            else:
                return None
        except requests.exceptions.HTTPError as err:
            print ('[*] Error in operation: ', str(err))
            return None
        finally:
            if r: r.close()

    def delete_objects(self):
    # ***       WARNING     ***
    # NOT INTENDED FOR PRODUCTION USE
    # EXERCISE EXTREME CAUTION
        headers = {
            'Content-Type' : 'application/json',
            'X-auth-access-token' : self.auth_token,
            }
        r = None
        response_data = {}
        try:
            # Entertainingly, the API seems to default to only returing 25 items by default (this is not documented)
            # So - we pass a parameter into the URL saying that we want 65535 entries back (limit=65535)
            object_types = {'hosts', 'fqdns', 'networkgroups', 'ranges', 'networks', 'portobjectgroups', 'protocolportobjects'}
            for object_type in object_types:
                response_data = self.get(object_type)
                if response_data is not None:
                    print ('[*] GET data returned: \n')
                    pprint(response_data['items'])
                    for record in response_data['items']:
                        delete_url = self.url + '/api/fmc_config/v1/domain/' + self.domain_uuid + '/object/' + object_type + '/' + record['id']
                        print('[*] Deleting object at ', delete_url)
                        r2 = requests.delete(delete_url, headers=headers, verify=False)
        except requests.exceptions.HTTPError as err:
            print ('[*] Error in operation: ', str(err))
        finally:
            if r: r.close()
    
    def get_obj_id(self, value, obj_type):
        # Returns an object id for a specific object
        data = self.get(obj_type)
        print('[D] Checking for ' + value + ' in:')
        pprint(data)
        for entry in data['items']:
            if entry['name'] == value:
                return entry['id']
        return None