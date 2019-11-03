import sqlite3
import os

db_path = "db.sql"

class DB_Helper:
    def __init__(self):
        self.conn = sqlite3.connect(db_path)
        self.c = self.conn.cursor()

        # One table for currently resolving
        sql = "CREATE TABLE IF NOT EXISTS s (domain TEXT, ip TEXT)"
        self.c.execute(sql)

        # And one for historical
        sql = "CREATE TABLE IF NOT EXISTS domain_ip_rel_all (domain TEXT, ip TEXT)"
        self.c.execute(sql)
        self.conn.commit()

    def reset_database(self):
        sql = "DELETE FROM domain_ip_rel_current"
        self.c.execute(sql)
        sql = "DELETE FROM domain_ip_rel_all"
        self.c.execute(sql)
        self.conn.commit()

    def add_domain_ip_all_relation(self, domain, ip):
        if domain == '' or ip == '':
            return
        sql = "INSERT INTO domain_ip_rel_all VALUES (?,?)"
        self.c.execute(sql, (domain, ip))
        self.conn.commit()


    def add_domain_ip_current_relation(self, domain, ip):
        if domain == '' or ip == '':
            return
        sql = "INSERT INTO domain_ip_rel_current VALUES (?,?)"
        self.c.execute(sql, (domain, ip))
        self.conn.commit()


    def get_domain_rel_current(self, domain):
        return self.get_matching_rows("domain_ip_rel_current", "ip", "domain", domain)

    def get_ip_rel_current(self, ip):
        return self.get_matching_rows("domain_ip_rel_current", "domain", "ip", ip)

    def get_domain_rel_all(self, domain):
        return self.get_matching_rows("domain_ip_rel_all", "ip", "domain", domain)

    def get_ip_rel_all(self, ip):
        return self.get_matching_rows("domain_ip_rel_all", "domain", "ip", ip)

    # Get matching result in a list
    def get_matching_rows(self,
                         table_name,
                         column_name,
                         where_field_str,
                         where_field_should_equal):
        sql = "SELECT {} FROM {} WHERE {}=?".format(
            column_name, table_name, where_field_str)

        self.c.execute(sql, (where_field_should_equal,))

        rows = self.c.fetchall()
        print(rows)
        res = []
        if not rows:
            return res

        for row in rows:
            res.append(row[0])

        return res
