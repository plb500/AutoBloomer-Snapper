import hashlib
from collections import namedtuple
import datetime

import grpc
from google.protobuf import empty_pb2

from pyproto.messages.controller_pb2_grpc import NetworkControllerStub
from pyproto.messages.sensors_pb2 import SensorModuleStatus
from pyproto.protomodel.database.grow_database import GrowDatabase
from pyproto.protomodel.database.grow_database_operation_response import GrowDatabaseOperationResponseType
from pyproto.protomodel.sensors.sensors import SensorData
from pyproto.server.grpc_client_interceptor import PiFeederClientInterceptor
from pyproto.server.grpc_server_auth_interceptor import GrpcServerAuthInterceptor
from src.image_annotator import AnnotationDetails

ReadingDetails = namedtuple("ReadingDetails", "sensor_id reading_id")


class AnnotationGrabber(object):
    EMPTY = empty_pb2.Empty()

    def __init__(self, host, port, passphrase=None):
        self.host = host
        self.port = port
        self.passphrase = passphrase

    def grab_annotations(self, grow_system_id, reading_details=None):
        # Create and hash the auth key if we have one and attach it to a channel interceptor
        interceptor = None
        if self.passphrase is not None:
            m = hashlib.sha256()
            m.update(self.passphrase.encode())
            hash_auth_key = m.digest().hex()
            interceptor = PiFeederClientInterceptor(GrpcServerAuthInterceptor.AUTH_HEADER_KEY, hash_auth_key)

        host_string = "{}:{}".format(self.host, self.port)
        grow_database = None
        annotation_details = None
        sensor_data = {}
        with grpc.insecure_channel(host_string) as channel:
            read_channel = grpc.intercept_channel(channel, interceptor) if interceptor is not None else channel
            stub = NetworkControllerStub(read_channel)

            # Get database
            grow_database_response = stub.GetGrowDatabase(AnnotationGrabber.EMPTY)
            if grow_database_response.statusCode == GrowDatabaseOperationResponseType.OPERATION_OK:
                grow_database = GrowDatabase.from_protobuf(grow_database_response.newGrowDatabase)

            # Get sensor data
            if reading_details is not None and len(reading_details) > 0:
                sensor_snapshot_response = stub.GetSensorSnapshot(AnnotationGrabber.EMPTY)
                if sensor_snapshot_response.moduleStatus == SensorModuleStatus.CONTROLLER_OK:
                    for sensor_data_proto in sensor_snapshot_response.sensorData:
                        sd = (SensorData.from_protobuf(sensor_data_proto))
                        sensor_data[sd.sensor_id] = sd

        if grow_database is not None:
            grow_system = grow_database.get_grow_system(grow_system_id=grow_system_id)
            if grow_system is not None:
                date_now = datetime.date.today()
                age = grow_system.inception_date.get_num_days_from_date(date_now)

                annotation_details = AnnotationDetails(grow_system.name, age)

                if len(sensor_data) > 0:
                    for details in reading_details:
                        d = sensor_data.get(details.sensor_id, None)
                        if d is not None:
                            r = next(filter(lambda rd: rd.description.reading_id == details.reading_id, d.sensor_readings), None)
                            if r is not None:
                                annotation_details.add_sensor_value(
                                    sensor_value=r.value,
                                    sensor_label=r.description.name
                                )

        return annotation_details
