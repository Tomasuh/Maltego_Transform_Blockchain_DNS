import json
import requests
import re
import ipaddress
import socket
import dns.resolver
from multiprocessing import Pool

from settings import n_url, n_rpc_user, n_rpc_password

class Export_Namecoin:
    def __init__(self):
        self.url = n_url
        self.headers = {'content-type': "application/json", 'cache-control': "no-cache"}
        self.rpc_user= n_rpc_user
        self.rpc_password= n_rpc_password

        self.count = 0

    def get_ips(self, ip_str_or_list):
        if type(ip_str_or_list) == str:
            return [ip_str_or_list]
        else:
            ips = [ip for ip in ip_str_or_list]
            if ips == []:
                ips.append("")
            return ips

    # Resolve IP of name servers with default DNS
    def resolve_domain(self, domain):
        try:
            return socket.gethostbyname(domain)
        except UnicodeError:
            return
        except socket.gaierror:
            return

    # Perform DNS lookup towards DNS specified in the name netry
    def nslookup(self, domain, nameservers):
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.timeout = 2.0
        ns_resolved = []
        for ns in nameservers:
            ret = self.resolve_domain(ns)
            if ret:
                ns_resolved.append(ret)
                # Enough with one of the ns, for time optimization 
                break

        try:
            dns.resolver.default_resolver.nameservers = ns_resolved
            answers = dns.resolver.query(domain, 'PTR')
        except dns.resolver.NoNameservers:
            return
        except dns.resolver.NoAnswer:
            return
        except dns.exception.Timeout:
            return
        except dns.resolver.NXDOMAIN:
            return
        except dns.name.LabelTooLong:
            return
        for rdata in answers:
            return (rdata)

    def download_nvs(self, start="", rate=1):
        payload = json.dumps({"method": "name_scan", "params": [start, rate]})
        response = requests.request("POST", self.url, data=payload, headers=self.headers, auth=(self.rpc_user, self.rpc_password))
        return json.loads(response.text)

    # Current IP is voluntarily, if included, it will be dropped from the returned list
    def download_name_history(self, name, current_ip=None):
        payload = json.dumps({"method": "name_history", "params": [name]})
        response = requests.request("POST", self.url, data=payload, headers=self.headers, auth=(self.rpc_user, self.rpc_password))
        try:
            res = json.loads(response.text)
        except:
            #print("Failed to view history for {}".format(name))
            return []
        if not res["result"]:
            #print("Failed to view history for {}".format(name))
            return []
        ips = []

        for entry in res["result"]:
            if not "value" in entry or entry["value"] == '':
                continue
            try:
                v_parsed = json.loads(entry["value"])
            except:
                #print("Failed to parse {}".format(entry["value"]))
                continue
            if type(v_parsed) != dict:
                continue

            if "ip" in v_parsed:
                for ip in self.get_ips(v_parsed["ip"]):
                    ips.append(ip)

        if current_ip:
            ips.remove(current_ip)

        return ips

    def lookup_domain(self, name_d):
        if "value_error" in name_d or "name_error" in name_d:
            return None
        
        if "name" not in name_d:
            return None

        if (not name_d["name"].startswith("d/") or
            not re.search("^[a-z]([a-z0-9-]{0,62}[a-z0-9])?$",name_d["name"][2:])):
            return None

        name = name_d["name"]
        value = name_d["value"]

        if value == '':
            return None
        try:
            v_dict = json.loads(value)
        except json.decoder.JSONDecodeError:
            return None

        if type(v_dict) != dict:
            return None

        historical_ips = self.download_name_history(name)

        if not ("ip" in v_dict or "ns" in v_dict) and not historical_ips:
            return None
        
        name = name_d["name"][2:]
        current_ip = None

        if "ip" in v_dict:
            current_ip = self.get_ips(v_dict["ip"])[0]
        elif "ns" in v_dict:
            current_ip = self.nslookup(name, v_dict["ns"])

        if not current_ip:
            current_ip=''

        if not name.endswith(".bit"):
            name = name + ".bit"

        if current_ip and current_ip!='':
            historical_ips.remove(current_ip)

        end_dict = {"name": name, "current_ip": current_ip, "historical_ips": historical_ips}

        return end_dict

    def download_all(self):
        start_next_fetch_from = ""
        all_data = []

        # Loop over all domain entries
        while True:
            res = self.download_nvs(start_next_fetch_from, 150000)
            all_data += res["result"]

            nr_backwards = -1
            while "value_error" in res["result"][nr_backwards] or "name_error" in res["result"][nr_backwards]:
                nr_backwards -= 1

            if start_next_fetch_from == res["result"][nr_backwards]["name"]:
                break

            start_next_fetch_from = res["result"][nr_backwards]["name"]
            print("Fetching domains with start from {}".format(start_next_fetch_from))

        # Threading for extraction of data about each domain 
        print("Starting threads....")
        with Pool(150) as p:
            end_res = p.map(self.lookup_domain, all_data)

        end_res = [res for res in end_res if res != None]
        return end_res
