#
# SiteConfig.py: load current site config
# Copyright (c) 2024 Gonzalo José Carracedo Carballal
#
# dsn-tools is free software: you can redistribute it and/or modify it under the 
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later 
# version.
#
# dsn-tools is distributed in the hope that it will be useful, but WITHOUT ANY 
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR 
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with 
# dsn-tools. If not, see <https://www.gnu.org/licenses/>.
#

from .Singleton import Singleton
import os
import configparser

SITE_FILE = 'site.ini'

class SiteConfig(metaclass = Singleton):
  def __init__(self):
    self._config_dir = os.path.dirname(__file__) + "/../config"
    
    self._config = configparser.ConfigParser(
      comment_prefixes=(';','#',),
      inline_comment_prefixes=(';','#',))
    
    path = self._config_dir + "/" + SITE_FILE
    self._config.read(path)

    try:
      self._lat       = float(self._config['site']['latitude'])
      self._lon       = float(self._config['site']['longitude'])
      self._elevation = float(self._config['site']['elevation'])

    except configparser.Error as e:
      raise RuntimeError(fr'Failed to read site file: {e}')
    except KeyError as e:
      raise RuntimeError(fr'Some key elements in site config are missing')
    except ValueError as e:
      raise RuntimeError(fr'Some of the site config keys is invalid: {e}')
  
  def latitude(self) -> float:
    return self._lat

  def longitude(self) -> float:
    return self._lon

  def elevation(self) -> float:
    return self._elevation
  
  