from enum import Enum

from pyproto.protomodel.helpers.data_factory import DataFactory
from annotation_grabber import ReadingAnnotationDetails


class SnapperConfigParseResponse(str, Enum):
    PARSE_OK = "Parse successful"
    ERROR_JSON_UNREADABLE = "Error: Could not parse JSON config file"
    ERROR_NO_SERVER_OPTIONS = "Error: No server options"
    ERROR_NO_DATA_OPTIONS = " Error: No data options"
    ERROR_SERVER_OPTIONS_MISSING = "Error: Server options missing required parameters"
    ERROR_DATA_OPTIONS_MISSING = "Error: Data options missing required parameters"


class SnapperConfigOptions(object):
    class ConfigKeys(str, Enum):
        SERVER_OPTIONS_KEY = "server_options"
        HOST_NAME_KEY = "host_name"
        PORT_NUMBER_KEY = "port_number"
        SERVER_PASSPHRASE_KEY = "server_passphrase"
        DATA_OPTIONS_KEY = "data_options"
        GROW_SYSTEM_ID_KEY = "grow_system_id"
        SENSOR_DETAILS_KEY = "sensor_details"
        SENSOR_ID_KEY = "sensor_id"
        READING_ID_KEY = "reading_id"
        DISPLAY_NAME_KEY = "annotation_label"
        IMAGE_DESTINATION = "image_destination"

    def __init__(self, data_root):
        self.options_parsed = False
        self.data_factory = DataFactory(data_root)

        self.host_name = None
        self.port_number = None
        self.passphrase = None
        self.grow_system_id = None
        self.image_destination = None
        self.sensor_readings = []

    def read_config(self, file_name):
        self.options_parsed = False

        config_dict = self.data_factory.container_from_json_file(file_name=file_name)
        if config_dict is None:
            return SnapperConfigParseResponse.ERROR_JSON_UNREADABLE

        server_options = config_dict.get(SnapperConfigOptions.ConfigKeys.SERVER_OPTIONS_KEY, None)
        if server_options is None:
            return SnapperConfigParseResponse.ERROR_NO_SERVER_OPTIONS

        data_options = config_dict.get(SnapperConfigOptions.ConfigKeys.DATA_OPTIONS_KEY, None)
        if data_options is None:
            return SnapperConfigParseResponse.ERROR_NO_DATA_OPTIONS

        # Check for required options
        server_options_required = [
            SnapperConfigOptions.ConfigKeys.HOST_NAME_KEY,
            SnapperConfigOptions.ConfigKeys.PORT_NUMBER_KEY,
        ]
        data_options_required = [
            SnapperConfigOptions.ConfigKeys.GROW_SYSTEM_ID_KEY,
            SnapperConfigOptions.ConfigKeys.IMAGE_DESTINATION
        ]

        if not all(item in server_options.keys() for item in server_options_required):
            return SnapperConfigParseResponse.ERROR_SERVER_OPTIONS_MISSING

        if not all(item in data_options.keys() for item in data_options_required):
            return SnapperConfigParseResponse.ERROR_DATA_OPTIONS_MISSING

        # Server options
        self.host_name = server_options[SnapperConfigOptions.ConfigKeys.HOST_NAME_KEY]
        self.port_number = server_options[SnapperConfigOptions.ConfigKeys.PORT_NUMBER_KEY]
        self.passphrase = server_options.get(SnapperConfigOptions.ConfigKeys.SERVER_PASSPHRASE_KEY, None)

        # Data options
        self.grow_system_id = data_options[SnapperConfigOptions.ConfigKeys.GROW_SYSTEM_ID_KEY]
        self.image_destination = data_options[SnapperConfigOptions.ConfigKeys.IMAGE_DESTINATION]
        reading_params = data_options.get(SnapperConfigOptions.ConfigKeys.SENSOR_DETAILS_KEY, None)
        if reading_params is not None:
            for reading_param in reading_params:
                sensor_id = reading_param.get(SnapperConfigOptions.ConfigKeys.SENSOR_ID_KEY, None)
                reading_id = reading_param.get(SnapperConfigOptions.ConfigKeys.READING_ID_KEY, None)
                display_name = reading_param.get(SnapperConfigOptions.ConfigKeys.DISPLAY_NAME_KEY, None)

                if sensor_id is not None and reading_id is not None:
                    self.sensor_readings.append(
                        ReadingAnnotationDetails(
                            sensor_id=sensor_id,
                            reading_id=reading_id,
                            display_name=display_name
                        )
                    )

        self.options_parsed = True

        return SnapperConfigParseResponse.PARSE_OK
