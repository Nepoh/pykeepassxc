from .keepassxc import *
from .database import *
from packaging import version

assert version.parse(get_version()) >= version.parse('2.5.4')
