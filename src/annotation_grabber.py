import hashlib
import json
import os.path
from collections import namedtuple
import datetime
from typing import Dict

import grpc
from google.protobuf import empty_pb2

from pyproto.messages.controller_pb2_grpc import NetworkControllerStub
from pyproto.messages.sensors_pb2 import SensorModuleStatus
from pyproto.protomodel.database.grow_database import GrowDatabase
from pyproto.protomodel.sensors.sensors import SensorData
from pyproto.server.grpc_client_interceptor import PiFeederClientInterceptor
from pyproto.server.grpc_server_auth_interceptor import GrpcServerAuthInterceptor
from image_annotator import AnnotationDetails

ReadingAnnotationDetails = namedtuple("ReadingAnnotationDetails", "sensor_id reading_id display_name")


class AnnotationGrabber(object):
    EMPTY = empty_pb2.Empty()
    CACHE_FILE = 'snapper_cache.json'
    GROW_DATABASE_CACHE_KEY = "grow_database"
    SENSOR_DATA_CACHE_KEY = "sensor_data"

    def __init__(self, cache_path, host, port, passphrase=None):
        self.cache_path = cache_path
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
        grow_database = None
        sensor_data = {}

        # Grab stuff from cache
        cached_data = self._get_cached_data()
        if cached_data is not None:
            grow_database = cached_data[0]
            sensor_data = cached_data[1]

        # Create and hash the auth key if we have one and attach it to a channel interceptor
        interceptor = None
        if self.passphrase is not None:
            m = hashlib.sha256()
            m.update(self.passphrase.encode())
            hash_auth_key = m.digest().hex()
            interceptor = PiFeederClientInterceptor(GrpcServerAuthInterceptor.AUTH_HEADER_KEY, hash_auth_key)

        # Connect to host
        host_string = "{}:{}".format(self.host, self.port)
        with grpc.insecure_channel(host_string) as channel:
            read_channel = grpc.intercept_channel(channel, interceptor) if interceptor is not None else channel
            stub = NetworkControllerStub(read_channel)

            tmp_grow_database = None
            tmp_sensor_data = {}

            # Get database
            grow_database_response = stub.GetGrowDatabase(AnnotationGrabber.EMPTY)
            if grow_database_response.statusCode == GrowDatabase.OperationResponse.ResponseType.OPERATION_OK:
                tmp_grow_database = GrowDatabase.from_protobuf(grow_database_response.newGrowDatabase)

            # Get sensor data
            sensor_snapshot_response = stub.GetSensorSnapshot(AnnotationGrabber.EMPTY)
            if sensor_snapshot_response.moduleStatus == SensorModuleStatus.CONNECTED:

                for sensor_data_proto in sensor_snapshot_response.sensorData:
                    sd = (SensorData.from_protobuf(sensor_data_proto))
                    tmp_sensor_data[sd.sensor_id] = sd

        if (
            (tmp_grow_database is not None) and
            (tmp_sensor_data is not None)
        ):
            grow_database = tmp_grow_database
            sensor_data = tmp_sensor_data

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

        self._write_cached_data(
            grow_database=grow_database,
            sensor_data=sensor_data
        )

        return annotation_details

    def _get_cached_data(self):
        cache_file = os.path.join(self.cache_path, AnnotationGrabber.CACHE_FILE)

        try:
            with open(cache_file) as json_file:
                cached_data = json.load(json_file)

                grow_database = GrowDatabase.from_dict(cached_data[AnnotationGrabber.GROW_DATABASE_CACHE_KEY])
                sensor_data = dict(map(lambda x: (x[0], SensorData.from_dict(x[1])), cached_data[AnnotationGrabber.SENSOR_DATA_CACHE_KEY].items()))
                return grow_database, sensor_data
        except FileNotFoundError:
            return None

    def _write_cached_data(self, grow_database, sensor_data: Dict):
        cached_data = {
            AnnotationGrabber.GROW_DATABASE_CACHE_KEY: grow_database.to_dict(),
            AnnotationGrabber.SENSOR_DATA_CACHE_KEY: dict(map(lambda x: (x[0], x[1].to_dict()), sensor_data.items()))
        }

        cache_file = os.path.join(self.cache_path, AnnotationGrabber.CACHE_FILE)

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f, ensure_ascii=False, indent=4)
