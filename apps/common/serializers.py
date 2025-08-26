"""
Module for handling Django model serialization/deserialization with cache
"""
import json
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.db import models


def serialize_model(model_instance):
    """
    Serialize a Django model instance for Redis storage
    
    Args:
        model_instance: Django model instance
        
    Returns:
        str: Serialized model data
    """
    if isinstance(model_instance, QuerySet):
        # For querysets, use Django's built-in serializer
        serialized_data = serializers.serialize('json', model_instance)
        return {'type': 'queryset', 'model': model_instance.model.__name__, 'data': serialized_data}
    elif isinstance(model_instance, models.Model):
        # For individual model instances
        serialized_data = serializers.serialize('json', [model_instance])
        return {'type': 'model', 'model': model_instance.__class__.__name__, 'data': serialized_data}
    else:
        # For primitive types, just return as is
        return {'type': 'primitive', 'data': model_instance}


def deserialize_model(serialized_data):
    """
    Deserialize model data from Redis
    
    Args:
        serialized_data: Data previously serialized with serialize_model
        
    Returns:
        Model instance or queryset
    """
    if not isinstance(serialized_data, dict) or 'type' not in serialized_data:
        # This wasn't serialized by our system, just return it
        return serialized_data
    
    if serialized_data['type'] == 'primitive':
        return serialized_data['data']
    
    # For models or querysets
    model_data = serialized_data['data']
    objects = list(serializers.deserialize('json', model_data))
    
    if serialized_data['type'] == 'model':
        # Return the actual model instance
        if objects:
            return objects[0].object
        return None
    else:
        # Return the list of model instances
        return [obj.object for obj in objects]
