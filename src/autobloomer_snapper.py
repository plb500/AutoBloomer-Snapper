import datetime
import hashlib
import os
import sys

import grpc

from google.protobuf import empty_pb2

from pyproto.server.grpc_client_interceptor import PiFeederClientInterceptor
from pyproto.server.grpc_server_auth_interceptor import GrpcServerAuthInterceptor
from pyproto.protomodel.database.grow_database_operation_response import GrowDatabaseOperationResponseType
from pyproto.protomodel.database.grow_database import GrowDatabase
from pyproto.messages.controller_pb2_grpc import NetworkControllerStub
from snapper_config import SnapperConfigOptions, SnapperConfigParseResponse

EMPTY = empty_pb2.Empty()
CONFIG_FILE = "autobloomer_snapper_cfg.json"
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))


# Read config
config_parser = SnapperConfigOptions(SCRIPT_PATH)
config_response = config_parser.read_config("autobloomer_snapper_cfg.json")
if config_response != SnapperConfigParseResponse.PARSE_OK:
    print("Could not obtain snapper config: {}".format(config_response))
    sys.exit()

# Create and hash the auth key if we have one and attach it to a channel interceptor
interceptor = None
if config_parser.passphrase is not None:
    m = hashlib.sha256()
    m.update(config_parser.passphrase.encode())
    hash_auth_key = m.digest().hex()
    interceptor = PiFeederClientInterceptor(GrpcServerAuthInterceptor.AUTH_HEADER_KEY, hash_auth_key)

host_string = "{}:{}".format(config_parser.host_name, config_parser.port_number)
with grpc.insecure_channel(host_string) as channel:
    read_channel = grpc.intercept_channel(channel, interceptor) if interceptor is not None else channel
    stub = NetworkControllerStub(read_channel)

    # Get database
    grow_database_response = stub.GetGrowDatabase(EMPTY)
    if grow_database_response.statusCode == GrowDatabaseOperationResponseType.OPERATION_OK:
        grow_database = GrowDatabase.from_protobuf(grow_database_response.newGrowDatabase)
        grow_system = grow_database.get_grow_system(grow_system_id=config_parser.grow_system_id)
        if grow_system is not None:
            date_now = datetime.date.today()
            age = grow_system.inception_date.get_num_days_from_date(date_now)
            print("Grow system name: {}".format(grow_system.name))
            print(" Grow system age: {}".format(age))
