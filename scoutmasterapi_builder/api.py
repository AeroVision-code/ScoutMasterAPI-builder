from .base import BaseAPI
from .projects import Projects
from .fields import Fields
from .crops import Crops
from .layertypes import LayerTypes
from .layers import Layers
from .files import Files
from .observations import Observations
from .observationsparameters import ObservationsParameters
from .cultivations import Cultivations
from .users import Users
from .subscriptions import Subscriptions
from .services import Services, ResearchCategories
from .researches import Researches
from .reports import Reports
from .invites import Invites
from .environments import Environments
from .benchmarking import Benchmarking
from .webhooks import Webhooks
from .fieldzones import FieldZones
from .layerexclusions import LayerExclusions
from .gddthresholds import GddThresholds
from .eid import Eid


class ScoutMasterAPI(
    BaseAPI,
    Projects,
    Fields,
    Crops,
    Layers,
    LayerTypes,
    Files,
    Observations,
    ObservationsParameters,
    Cultivations,
    Users,
    Subscriptions,
    Services,
    ResearchCategories,
    Researches,
    Reports,
    Invites,
    Environments,
    Benchmarking,
    Webhooks,
    FieldZones,
    LayerExclusions,
    GddThresholds,
    Eid,
):
    """Aggregates all topic classes into a single API object"""
    pass
