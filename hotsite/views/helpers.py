from django.core import serializers
import json


def create_optional_dict(optional, remove_fields):
    
    optional_obj_as_json = serializers.serialize('json', [optional, ])
    optional_obj = json.loads(optional_obj_as_json)
    optional_obj = optional_obj[0]
    optional_obj = optional_obj['fields']
    optional_obj['id'] = optional.pk

    for field in remove_fields:
        del optional_obj[field]

    return optional_obj
