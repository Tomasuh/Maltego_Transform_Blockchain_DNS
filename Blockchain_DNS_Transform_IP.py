import socket
import sqlite3
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.entities import IPAddress, Domain
from maltego_trx.transform import DiscoverableTransform


class Blockchain_DNS_Transform_IP(DiscoverableTransform):
    """
    Find blockchain domains which has pointed, or is point towards the IP
    """
    @classmethod
    def create_entities(cls, request, response):
        ip_address = request.Value

        conn = sqlite3.connect("export_code/db.sql")
        c = conn.cursor()
        c.execute("SELECT domain FROM domain_ip_rel_current WHERE ip=?", (ip_address,))
        rows = c.fetchall()

        c.execute("SELECT domain FROM domain_ip_rel_all WHERE ip=?", (ip_address,))
        rows += c.fetchall()

        to_add = []
        if rows:
            for row in rows:
                try:
                    response.addEntity(Domain, row[0])
                except socket.error as e:
                    response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])