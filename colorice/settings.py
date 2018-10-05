import os
import platform

__version__ = 'v0.1.0'

HOME = os.getenv('HOME', os.getenv('USERPROFILE'))
MODULE_DIR = os.path.dirname(__file__)
CONFIG_PATHS = (
    '{}/.config/colorice/config.yaml'.format(HOME),
)
