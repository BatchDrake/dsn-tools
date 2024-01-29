#
# Forecast.py: make visibility forecasts for a given object
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

from astroquery.jplhorizons import Horizons
from astropy.time import Time
import astropy.units as u
from .SiteConfig import SiteConfig
from datetime import datetime, timedelta
import numpy as np

SIDEREAL_DAY = 23.9344696 # hours

class Forecast:
  def __init__(self):
    self._config = SiteConfig()

    self._loc = {
      'lon':       self._config.longitude(),
      'lat':       self._config.latitude(),
      'elevation': self._config.elevation(),
      'body':      '399'
    }

  @staticmethod  
  def date2jd(date: datetime):
    t = Time(date, scale='utc')
    return t.jd1 + t.jd2

  def query(
    self, 
    obj: str,
    start: datetime = None,
    stop: datetime = None,
    step_mins: int = 5):

    if start is None:
      start = datetime.now()

    if stop is None:
      stop = start + timedelta(hours = SIDEREAL_DAY)
    
    epochs = {
      'start' : fr'JD {self.date2jd(start)}',
      'stop'  : fr'JD {self.date2jd(stop)}',
      'step'  : fr'{step_mins}m'
    }

    jpl = Horizons(id = obj, location = self._loc, epochs = epochs)
    eph = jpl.ephemerides()
    
    tt = list(
      map(
        lambda x: Time(x, format = 'jd', scale = 'utc').to_datetime(),
        eph['datetime_jd'].tolist()))
    
    az   = np.array(eph['AZ'])
    el   = np.array(eph['EL'])
    R    = np.array(eph['r'])
    dRdt = np.array(eph['r_rate'])
    vis  = np.array(eph['sat_vis']) == '*'
    
    return tt, az, el, R, dRdt, vis


  
