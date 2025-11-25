from .base import BaseAPI
from .projects import Projects
from .fields import Fields
from .crops import Crops
from .layertypes import LayerTypes
from .layers import Layers
from .files import Files

class ScoutMasterAPI(BaseAPI, Projects, Fields, Crops, Layers, LayerTypes, Files):
    """Aggregates all topic classes into a single API object"""
    pass
