from db_helper import DB_Helper
from export_emercoin import Export_Emercoin
from export_namecoin import Export_Namecoin
import sqlite3


print("Initialising DB")
db_handler = DB_Helper()
db_handler.reset_database()

print("Fetching Emercoin domain history")
export_e = Export_Emercoin()
export_data_e = export_e.download_all()

print("Fetching Namecoin domain history")

export_n = Export_Namecoin()
export_data_n = export_n.download_all()

print("Exported {} Namecoin domain entries".format(len(export_data_n)))


print("Adding entries to the database")

for entry in export_data_e + export_data_n:
    domain = entry["name"]
    current_ip = entry["current_ip"]
    past_ips = entry["historical_ips"]

    if current_ip:
        try:
            db_handler.add_domain_ip_current_relation(domain, current_ip)
        except sqlite3.InterfaceError:
            print("Failed: to add {} {}".format(domain, current_ip))

    for past_ip in past_ips:
        try:
            db_handler.add_domain_ip_all_relation(domain, past_ip)
        except sqlite3.InterfaceError:
            print("Failed: to add {} {}".format(domain, past_ip))


print("Done")