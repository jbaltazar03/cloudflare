import os, requests, json, sys, time, csv
import pandas as pd

class Cloudflare():
    def __init__(self, host='https://api.cloudflare.com', api_url='/client/v4'):
        self.host = host
        self.api_url = api_url
        self.authorization = False
        self.content_type = "application/json"
        self.verbose = False
        self._token = None
        self._auth = False

    def _debug(self, msg):
        if self.verbose:
            sys.stderr.write(f"{msg}\n")

    def _verify_token(self):
        url = f"{self.host}{self.api_url}/user/tokens/verify"
        config = {
            "token": os.environ.get('CF_TOKEN'),
            "api_key": os.environ.get('CF_API_KEY'),
            "email":os.environ.get('CF_EMAIL')
        }
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {config["token"]}'}
        r = requests.get(url, headers=headers)
        status = r.json()['result']['status']
        # print(f'Token status: {status}')

        self._token = config["token"]

    def _make_requests(self, url, method='GET', params=None, data=None):
        self._debug("Making requests... ")
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}
        try:
            r = requests.get(url, headers=headers)
            print(r.json())
        except KeyError as err:
            print(f"KeyError: {err}")
        
class Get(Cloudflare):
    def users(self):
        if not self._auth:
            self._verify_token()

        url = f"{self.host}{self.api_url}/user"
        return self._make_requests(url)

    def organizations(self):
        if not self._auth:
            self._verify_token()
        config = {
            "wb_org": os.environ.get('CF_ORG_ID')
        }

        self._debug("Making requests... ")
        url = f"{self.host}{self.api_url}/organizations/{config['wb_org']}"
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}
        members =  []

        try:
            r = requests.get(url, headers=headers)
            members = r.json()['result']['members']
            for member in members:
                print(member['email'])
            print(f'Total member: {len(members)}')
        except KeyError as err:
            print(f"KeyError: {err}")
        return 

    def zones(self):
        if not self._auth:
            self._verify_token()

        self._debug("Making requests... ")
        url = f"{self.host}{self.api_url}/zones"
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}
        members =  []
    
        try:
            r = requests.get(url, headers=headers)
            result_info = r.json()['result_info']['total_pages']
            total_count = r.json()['result_info']['total_count']
            zones_id = []
            page = 1

            with open("io/zone_ids.csv", "w") as f:
                fieldnames = ['cf_id', 'app_name']
                csvwriter = csv.DictWriter(f, fieldnames=fieldnames)
                csvwriter.writeheader()
                while True:
                    if page == result_info + 1:
                        break

                    url = f"{self.host}{self.api_url}/zones?page={page}"
                    r = requests.get(url, headers=headers)
                    zones = r.json()['result']

                    for zone in zones:
                        # print(zone['id'] + ", " + zone['name'])
                        zones_id.append(zone['id'])
                        csvwriter.writerow({'cf_id':zone['id'], 'app_name': zone['name']})
                    page += 1

                else:
                    print("Something goofed")
                print(f'Zone total count: {total_count}')
            
        except KeyError as err:
            print(f"KeyError: {err}")
        
        return zones_id

    def ssl_count(self):
        # if not self._auth:
        #     self._verify_token()

        zones_id = self.zones()
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}
        ssl_count = []

        for zone_id in zones_id:
            url = f"{self.host}{self.api_url}/zones/{zone_id}/ssl/certificate_packs"
            r = requests.get(url, headers=headers)
            ssl_count.append(r.json()['result_info']['total_count'])

        df = pd.read_csv('io/zone_ids.csv')
        df['ssl_count'] = ssl_count
        df.to_csv('output.csv', index=False, mode="w")
  
    def argo_limit(self):
        # if not self._auth:
        #     self._verify_token()

        zones_id = self.zones()
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}
        argo_count = []

        for zone_id in zones_id:
            url = f"{self.host}{self.api_url}/zones/{zone_id}/rate_limits"
            r = requests.get(url, headers=headers)
            argo_count.append(r.json()['result_info']['total_count'])

        df = pd.read_csv('./output.csv')
        df['argo_count'] = argo_count
        df.to_csv('./output.csv', index=False, mode="w")
            
    def dns_zones(self):
        # if not self._auth:
        #     self._verify_token()

        zones_id = self.zones()
        headers = {'Accept': self.content_type, 'Authorization': f'Bearer {self._token}'}
        dns_list = []

        for zone in zones_id:
            url = f'{self.host}{self.api_url}/zones/{zone}/dns_records'
            r = requests.get(url, headers=headers)
            result = r.json()
            dns_list.append([i['name'] for i in result['result']])

        df = pd.read_csv('./output.csv')
        df['dns_zones'] = dns_list
        df.to_csv('./output.csv', index=False, mode="w")