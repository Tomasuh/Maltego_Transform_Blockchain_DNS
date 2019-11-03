import socket
import sqlite3
from maltego_trx.maltego import UIM_TYPES
from maltego_trx.entities import IPAddress
from maltego_trx.transform import DiscoverableTransform


class Blockchain_DNS_Transform_Domain(DiscoverableTransform):
    """
    Find blockchain domains past and currently resolving IPs
    """
    @classmethod
    def create_entities(cls, request, response):
        domain = request.Value

        conn = sqlite3.connect("export_code/db.sql")
        c = conn.cursor()
        c.execute("SELECT ip FROM domain_ip_rel_current WHERE domain=?", (domain,))
        rows = c.fetchall()

        c.execute("SELECT ip FROM domain_ip_rel_all WHERE domain=?", (domain,))
        rows += c.fetchall()

        to_add = []
        if rows:
            for row in rows:
                try:
                    response.addEntity(IPAddress, row[0])
                except socket.error as e:
                    response.addUIMessage("Error: " + str(e), UIM_TYPES["partial"])