import json
import requests
import re
import ipaddress

from settings import e_url, e_rpc_user, e_rpc_password

class Export_Emercoin:

    def __init__(self):
        self.url = e_url
        self.headers = {'content-type': "application/json", 'cache-control': "no-cache"}
        self.rpc_user= e_rpc_user
        self.rpc_password= e_rpc_password

    def get_ip_from_value(self, string):
        if not string.startswith("A="):
            return None

        potential_ip = string.split("|")[0][2:]
        try:
            ipaddress.ip_address(potential_ip)
        except ValueError:
            return None

        return potential_ip

    def download_nvs(self, start="", rate=1000):
        payload = json.dumps({"method": "name_scan", "params": [start, rate]})
        response = requests.request("POST", self.url, data=payload, headers=self.headers, auth=(self.rpc_user, self.rpc_password))
        return json.loads(response.text)

    # Only for domain names starting with dns:
    # Current IP is voluntarily, if included, it will be dropped from the returned list
    def download_name_history(self, name, current_ip=None):
        payload = json.dumps({"method": "name_history", "params": [name, True, "string"]})
        response = requests.request("POST", self.url, data=payload, headers=self.headers, auth=(self.rpc_user, self.rpc_password))
        res = json.loads(response.text)
        if not res["result"]:
            print("Failed to view history for {}".format(name))
            return []
        ips = []
        for data in res["result"]:
            if data["operation"] not in ["name_update", "name_new"]:
                continue
            ip = self.get_ip_from_value(data["value"])
            if ip:
                ips.append(ip)

        if current_ip:
            ips.remove(current_ip)
        return ips

    def download_all(self):
        end_res = []
        start_next_fetch_from = ""
        while True:
            res = self.download_nvs(start_next_fetch_from, 50000)
            for name_d in res["result"]:
                name = name_d["name"]
                
                if not name.startswith("dns:"):
                    continue

                value = name_d["value"]
                current_ip = self.get_ip_from_value(value)
                if not current_ip:
                    current_ip = ""

                historical_ips = self.download_name_history(name, current_ip)

                if current_ip == "" and not historical_ips:
                    continue

                expire = int(name_d["expires_in"])
                if "expired" in name_d and name_d["expired"]:
                    expired = True
                else:
                    expired = False

                end_dict = {"name": name[4:], "current_ip": current_ip, "historical_ips": historical_ips, "expire_time": expire, "expired": expired}
                end_res.append(end_dict)

            # Are we done?
            if start_next_fetch_from == res["result"][-1]["name"]:
                break

            start_next_fetch_from = res["result"][-1]["name"]

        return end_res
