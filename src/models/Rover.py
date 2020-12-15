from .Environment import Environment
from .Inventory import Inventory

class Rover:

    Inventory=Inventory()
    battery=10
    size=10
    Environment=Environment()
    position=dict()
    state="mobile"

