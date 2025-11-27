from .base import BaseAPI
from .projects import Projects
from .fields import Fields
from .crops import Crops
from .layertypes import LayerTypes
from .layers import Layers
from .files import Files
from .observations import Observations
from .cultivations import Cultivations
from .users import Users

class ScoutMasterAPI(BaseAPI, Projects, Fields, Crops, Layers, LayerTypes, Files, Observations, Cultivations, Users):
    """Aggregates all topic classes into a single API object"""
    pass
