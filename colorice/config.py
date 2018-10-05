"""Providers module

Module defining basic available ``ConfigProvider`` s that are needed
for ``Config`` service to parse ConfigFiles given their extensions

Note
----
You can define your own providers and registers them in the ``Config``
service, but every custom provider should inherit from the abstract
``ConfigProvider`` defined below.
"""
import yaml

import glob
import re
import os
import logging
from typing import Optional, Union, List, Any

from colorice.settings import CONFIG_PATHS
from colorice.utils import import_mod_part


class ConfigProvider:
    """Abstract ConfigProvider

    Each custom defined and registered ConfigProvider should inherit
    from this class
    """


    def parse(self, path: str) -> dict:
        """Abstract parse method

        Parses a given config file by its corresponding path

        Parameters
        ----------
        path
            Path to the given config file

        Raises
        ------
        NotImplementedeError
        """
        raise NotImplementedError("{} does not implement parse\
                method.".format(self.__class__.__name__))


    def parse_str(self, res: str) -> dict:
        """Abstract parse method

        Parses a given string resource

        Parameters
        ----------
        res
            String resource

        Raises
        ------
        NotImplementedeError
        """
        raise NotImplementedError("{} does not implement parse_str "
                "method.".format(self.__class__.__name__))


class YamlConfigProvider(ConfigProvider):
    """
    Parses yaml config files
    """


    def parse(self, path: str) -> dict:
        """
        Parses a given yaml config file by its corresponding path

        Parameters
        ----------
        path
            Path to the given config file

        Returns
        -------
        config
            Config file represented as dictionary
        """
        with open(path, 'r') as res:
            return yaml.load(res)


    def parse_str(self, res: str) -> dict:
        """
        Parses a given string resource

        Parameters
        ----------
        res
            String resource

        Returns
        -------
        config
            String resource represented as dictionary
        """
        return yaml.load(res)




class ConfigFile:
    """Config file wrapper

    Class used as a wrapper around the config file for
    better manipulation and attribute getting

    Attributes
    ----------
    raw_dict : :obj:`dict`
        Target raw dictionary parsed from a
        config file
    path : :obj:`str`
        Path to the given config file

    Todo
    ----
    Implement magic methods like __dict__ __getitem__ etc.
    """


    def __init__(self, path: str, raw_dict: dict) -> None:
        if not os.path.exists(path):
            raise ValueError("Config file {} doesn't exist.".format(path))

        self.raw_dict = raw_dict
        self.path = path


    def get(self, key: str, fallback: Any = None) -> Any:
        """Gets a given key

        Gets a given key by its dotted notation if it exists within the
        ``raw_dict`` otherwise fallback will be yielded

        Parameters
        ----------
        key
            Identifier of wanted value by its dotted notation
        fallback
            Default value to return when there won't be any value
            satisfying wanted key
        """
        try:
            tmp = self.raw_dict
            for fragment in key.split('.'):
                tmp = tmp[fragment]
            if isinstance(tmp, str):
                match = re.search(r'%(.+)%', tmp)
                if match is not None:
                    return self.get(match.group(1), fallback)

            return tmp
        except KeyError:
            return fallback


class Config:
    """Config service

    Simple wrapper around config providers and config parsing

    Note
    ----
    It is recommended to import the global instance of this class instead
    of creating new ones.

    Attributes
    ----------
    provider_pool : :obj:`dict`
        Provider configuration dictionary, used to register a provider
        for target extensions
        Default being::
            {
                'yaml, yml': 'audiodb.config.provider.YamlConfigProvider'
            }

    Parameters
    ----------
    providel_pool : optional
        Custom providers pool used for registering own providers
        outside of config package.
        Format example::
            {
                'yaml, yml': 'audiodb.config.provider.YamlConfigProvider',
                'ini': 'custom_package.module.MyIniConfigProvider'
            }
    """


    _available_providers = {
        'yaml, yml': 'colorice.config.YamlConfigProvider'
    }


    def __init__(self, provider_pool: dict = None, logger: logging.Logger = None) -> None:
        self.logger = logger if logger is not None else logging.getLogger(__name__)
        self.provider_pool = provider_pool if provider_pool is not None \
                else self._available_providers
        self._cached_providers = dict()
        self._available_extensions = self._get_available_extensions()


    def load_configuration(self, config_path: Optional[Union[List[str], str]] = None) -> Optional[ConfigFile]:
        """Configuration load

        Tries to load configuration given some lookup paths,
        which consists of the ones provided by user and predefined ones
        (which are stored in ``settings`` module)

        Parameters
        ----------
        config_path : :obj:`list` of :obj:`str` or :obj:`str`, optional
            Custom config lookup path(s)

        Returns
        -------
        config
            Parsed config file if found and there has been an
            available provider given its extension, otherwise None
        """
        lookup_paths = list()
        if config_path is not None:
            config_path = [config_path]
            lookup_paths.extend(config_path)

        lookup_paths.extend(CONFIG_PATHS)

        for path in lookup_paths:
            for res in glob.glob('{}*'.format(path)):
                ext = res.rsplit('.', 1)[-1]

                # If there is any provider that can parse
                # such extension
                if ext in self._available_extensions:
                    self.logger.info("Loading configuration from '{}'...".format(res))
                    return self.parse_config_file(res)

                self.logger.warning("Skipping configuration defined in "
                                    "'{}' since there isn't any provider"
                                    " that could parse this filetype.".format(res))

        return None


    def parse_config_file(self, path: str) -> Optional[ConfigFile]:
        """
        Parse given config file by its path

        Parameters
        ----------
        path
            Path to the wanted config file

        Raises
        ------
        ValueError
            Raised when there isn't any provider that could handle
            the given extension
        """
        ext = path.rsplit('.', 1)[-1]
        if ext not in self._available_extensions:
            raise ValueError("There isn't any ConfigFileProvider that \
                    could parse file '{}'.".format(path))

        provider_cls = self._available_extensions[ext]
        if provider_cls in self._cached_providers:
            provider = self._cached_providers[provider_cls]
        else:
            TargetProvider = import_mod_part(provider_cls)
            provider = TargetProvider()
            self._cached_providers[provider_cls] = provider

        raw = provider.parse(path)
        return ConfigFile(path, raw)


    def _get_available_extensions(self) -> dict:
        """
        Preprocceses the provider_pool for better manipulation

        Returns
        ------
        parsed : dict
            parsed provider pool
            example: {
                'yaml, yml': 'audiodb.config.provider.YamlConfigProvider',
                'ini': 'custom_package.module.MyIniConfigProvider'
            } => {
                'yaml': 'audiodb.config.provider.YamlConfigProvider',
                'yml': 'audiodb.config.provider.YamlConfigProvider',
                'ini': 'custom_package.module.MyIniConfigProvider'
            }
        """
        parsed = dict()
        for extensions, provider in self.provider_pool.items():
            for ext in extensions.split(', '):
                parsed[ext] = provider

        return parsed


config = Config()
""":obj:`Config`: global instance of the Config class"""
