import sys
from Blockchain_DNS_Transform_IP import Blockchain_DNS_Transform_IP
from Blockchain_DNS_Transform_Domain import Blockchain_DNS_Transform_Domain

from maltego_trx.registry import register_transform_function, register_transform_classes
from maltego_trx.server import app, application
from maltego_trx.handler import handle_run

register_transform_function(Blockchain_DNS_Transform_IP)
register_transform_function(Blockchain_DNS_Transform_Domain)

handle_run(__name__, sys.argv, app)
