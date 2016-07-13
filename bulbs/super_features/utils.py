from django.apps import apps
from django.conf import settings


def get_data_serializer(name):
    from bulbs.super_features.models import GUIDE_TO_HOMEPAGE, GUIDE_TO_ENTRY
    from bulbs.super_features.data_serializers import (GuideToChildSerializer,
                                                       GuideToParentSerializer)
    serializer = {
        GUIDE_TO_HOMEPAGE: GuideToParentSerializer,
        GUIDE_TO_ENTRY: GuideToChildSerializer
    }.get(name, None)
    if serializer is None:
        raise KeyError('The requested SuperFeature does not have a registered serializer')

    return serializer


def get_superfeature_model():
    from bulbs.super_features.models import BaseSuperFeature

    model_name = getattr(settings, "BULBS_SUPERFEATURE_MODEL", None)
    if model_name is None:
        return BaseSuperFeature
    return apps.get_model(model_name)


def get_superfeature_serializer():
    from bulbs.super_features.serializers import BaseSuperFeatureSerializer

    serializer = getattr(settings, "BULBS_SUPERFEATURE_SERIALIZER", None)
    if serializer is None:
        return BaseSuperFeatureSerializer
    return serializer


def get_superfeature_partial_serializer():
    from bulbs.super_features.serializers import BaseSuperFeaturePartialSerializer

    serializer = getattr(settings, "BULBS_SUPERFEATURE_PARTIAL_SERIALIZER", None)
    if serializer is None:
        return BaseSuperFeaturePartialSerializer
    return serializer


def get_superfeature_metadata():
    from bulbs.super_features.metadata import BaseSuperFeatureMetadata

    metadata = getattr(settings, "BULBS_SUPERFEATURE_METADATA", None)
    if metadata is None:
        return BaseSuperFeatureMetadata
    return metadata


def get_superfeature_choices():
    from bulbs.super_features.models import BASE_CHOICES

    configured_superfeatures = getattr(settings, "BULBS_CUSTOM_SUPERFEATURE_CHOICES", ())
    for sf in configured_superfeatures:
        if type(sf[0]) is not str or type(sf[1]) is not str:
            raise ValueError(
                "Super Feature choices must be a string. {0} is not valid".format(sf)
            )
    return BASE_CHOICES + configured_superfeatures
