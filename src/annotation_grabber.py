import hashlib
from collections import namedtuple
import datetime

import grpc
from google.protobuf import empty_pb2

from pyproto.messages.controller_pb2_grpc import NetworkControllerStub
from pyproto.messages.sensors_pb2 import SensorModuleStatus
from pyproto.protomodel.database.grow_database import GrowDatabase
from pyproto.protomodel.database.grow_database_operation_response import GrowDatabaseOperationResponseType
from pyproto.protomodel.sensors.sensor_display import SensorDisplayMetadata
from pyproto.protomodel.sensors.sensors import SensorData
from pyproto.server.grpc_client_interceptor import PiFeederClientInterceptor
from pyproto.server.grpc_server_auth_interceptor import GrpcServerAuthInterceptor
from image_annotator import AnnotationDetails

ReadingAnnotationDetails = namedtuple("ReadingAnnotationDetails", "sensor_id reading_id display_name")


class AnnotationGrabber(object):
    EMPTY = empty_pb2.Empty()

    def __init__(self, host, port, passphrase=None):
        self.host = host
        self.port = port
        self.passphrase = passphrase

    @staticmethod
    def _add_reading_annotations(sensor_annotation_descriptions, sensor_data, annotation_details):
        if sensor_annotation_descriptions is None or len(sensor_annotation_descriptions) == 0:
            return

        if sensor_data is None or len(sensor_data) == 0:
            return

        if annotation_details is None:
            return

        for annotation_description in sensor_annotation_descriptions:
            sensor = sensor_data.get(annotation_description.sensor_id, None)
            if not sensor:
                continue

            reading = next((x for x in sensor.sensor_readings if x.name == annotation_description.reading_id), None)
            if not reading:
                continue

            label = annotation_description.display_name if annotation_description.display_name else reading.name
            annotation_details.add_sensor_value(
                sensor_value=reading.value,
                sensor_label=label
            )

    def grab_annotations(self, grow_system_id, sensor_annotation_descriptions=None):
        annotation_details = None

        # Create and hash the auth key if we have one and attach it to a channel interceptor
        interceptor = None
        if self.passphrase is not None:
            m = hashlib.sha256()
            m.update(self.passphrase.encode())
            hash_auth_key = m.digest().hex()
            interceptor = PiFeederClientInterceptor(GrpcServerAuthInterceptor.AUTH_HEADER_KEY, hash_auth_key)

        # Connect to host
        host_string = "{}:{}".format(self.host, self.port)
        grow_database = None
        sensor_data = {}
        display_params = {}
        with grpc.insecure_channel(host_string) as channel:
            read_channel = grpc.intercept_channel(channel, interceptor) if interceptor is not None else channel
            stub = NetworkControllerStub(read_channel)

            # Get database
            grow_database_response = stub.GetGrowDatabase(AnnotationGrabber.EMPTY)
            if grow_database_response.statusCode == GrowDatabaseOperationResponseType.OPERATION_OK:
                grow_database = GrowDatabase.from_protobuf(grow_database_response.newGrowDatabase)

            # Get sensor data
            sensor_snapshot_response = stub.GetSensorSnapshot(AnnotationGrabber.EMPTY)
            if sensor_snapshot_response.moduleStatus == SensorModuleStatus.CONNECTED:
                for sensor_data_proto in sensor_snapshot_response.sensorData:
                    sd = (SensorData.from_protobuf(sensor_data_proto))
                    sensor_data[sd.sensor_id] = sd

                for display_params_proto in sensor_snapshot_response.displayParameters:
                    display_params[display_params_proto.sensorID] = SensorDisplayMetadata.from_protobuf(display_params_proto)

        if grow_database is not None:
            grow_system = grow_database.get_grow_system(grow_system_id=grow_system_id)
            if grow_system is not None:
                date_now = datetime.date.today()
                age = grow_system.inception_date.get_num_days_from_date(date_now)

                annotation_details = AnnotationDetails(grow_system.name, age)

                AnnotationGrabber._add_reading_annotations(
                    sensor_annotation_descriptions=sensor_annotation_descriptions,
                    sensor_data=sensor_data,
                    annotation_details=annotation_details
                )

        return annotation_details
