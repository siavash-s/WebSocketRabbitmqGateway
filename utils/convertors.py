import json
import logging
from json import JSONDecodeError
from logging import getLogger
from typing import Callable
from marshmallow import ValidationError


def json_deserializer_factory(input_schema_class: Callable) -> Callable:
    """Creates json deserializer function that accepts data, deserialize it, and return the deserialized data

    :param input_schema_class: the marshmallow Schema class to be used for data deserialization
    :returns: a function that accepts and returns data, to be used as a config hook
    """
    def f(data):
        schema_obj = input_schema_class()
        try:
            dict_data = schema_obj.loads(data)
        except ValidationError as e:
            getLogger().error("json data '{}', cannot be deserialized, sending empty data".format(data))
            logging.exception(e)
            return {}
        except JSONDecodeError as e:
            getLogger().error("json data '{}', cannot be deserialized, sending empty data".format(data))
            logging.exception(e)
            return {}
        except Exception as e:
            getLogger().error("json data '{}', cannot be deserialized".format(data))
            logging.exception(e)
            return {}
        else:
            return dict_data
    return f


def convert_to_json_or_empty(data):
    """Convector function that tries to deserialize data from rabbit into dict, otherwise empty dict in cas of error"""
    try:
        return json.loads(data)
    except JSONDecodeError as e:
        getLogger().error("json data '{}', cannot be deserialized".format(data))
        logging.exception(e)
        return {}
    except Exception as e:
        getLogger().error("json data '{}', cannot be deserialized".format(data))
        logging.exception(e)
        return {}
