#
# plotobject.py: Plot a forecast of an object visibility with a day
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

from AmateurDSN import Forecast
import matplotlib.pyplot as plt
import sys
from datetime import datetime
import numpy as np

style = {
  'axes.edgecolor':   '#00ff00',
  'xtick.color':      'green',
  'ytick.color':      'green',
  'font.family':      'Helvetica',
  'figure.facecolor': 'black'
}

PATH_COLOR   = '#ffff00'
AOS_COLOR    = '#00ff00'
LOS_COLOR    = '#ff0000'
GRID_COLOR   = '#3f3f3f'
N_DATE_STEPS = 5
AZTICKS      = 12

def plot_locations(
  ax,
  tt,
  az,
  el,
  color = 'white',
  text_color = None,
  bbox = False,
  prefix = None):

  if text_color is None:
    text_color = color
  
  # Plot locations
  ax.scatter(az, 90 - el, color = color)

  # Tag them
  start = tt[0]
  
  for i in range(len(az)):
    curr = tt[i]

    ellapsed = curr - start

    suffix = ''
    if ellapsed.days > 0:
      suffix = fr' (+{ellapsed.days} days)'

    if prefix is None:
      prefix = '   '

    t = ax.text(
	    az[i],
	    90 - el[i],
	    fr'{prefix}{tt[i].strftime("%H:%M:%S")}{suffix}',
	    color = text_color,
	    horizontalalignment = "left",
      verticalalignment = "center_baseline" if bbox else 'center',
	    fontfamily = 'Helvetica',
      zorder = 50)
    
    if bbox:
      t.set_bbox(dict(facecolor='black', edgecolor = text_color, boxstyle = 'round'))
    

if len(sys.argv) != 2:
    print(fr'Usage: {sys.argv[0]} PROBE')
    sys.exit(1)

OBJECT = sys.argv[1]
WHEN   = datetime.now()

forecast = Forecast()

try:
  tt, az, el, R, dRdt = forecast.query(OBJECT, start = WHEN)
except Exception as e:
  print(fr'{sys.argv[0]}: failed to acquire ephemeris: {e}')
  sys.exit(1)

azRad = np.deg2rad(az)
elRad = np.deg2rad(el)

with plt.rc_context(style):
  fig, ax = plt.subplots(subplot_kw = {'projection': 'polar'})

  # Plot path in the sky
  ax.plot(azRad, 90 - el, color = PATH_COLOR, zorder = 30)
  ax.plot(azRad, 90 + el, color = PATH_COLOR, zorder = 30, linestyle = 'dotted', alpha = .25)
  
  visible = el > 0
  diff    = np.array([0.] + np.diff(np.sign(el)).tolist())
  
  aos     = diff > 0
  los     = diff < 0
  
  Nvis    = len(el[visible])
  step    = Nvis // N_DATE_STEPS
  
  dateAz  = azRad[visible][::step]
  dateEl  = el[visible][::step]
  ttVis   = np.array(tt)[visible][::step]
  plot_locations(ax, ttVis, dateAz, dateEl, color = PATH_COLOR, text_color = 'white')

  aosAz   = azRad[aos]
  aosEl   = el[aos]
  aosTT   = np.array(tt)[aos]
  plot_locations(ax, aosTT, aosAz, aosEl, color = AOS_COLOR, bbox = True, prefix = 'AOS: ')

  losAz   = azRad[los]
  losEl   = el[los]
  losTT   = np.array(tt)[los]
  plot_locations(ax, losTT, losAz, losEl, color = LOS_COLOR, bbox = True, prefix = 'LOS: ')

  ax.set_facecolor(style['figure.facecolor'])
  ax.grid(color = GRID_COLOR, linestyle = 'dashed')
  
  if el[0] > 0:
    plot_locations(ax, [tt[0]], azRad[0:1], el[0:1], color = '#00ffff', prefix = 'VISIBLE NOW: ', bbox = True)

  ax.set_theta_direction(-1)
  
  tticks = np.linspace(2 * np.pi * (AZTICKS - 1) / (AZTICKS), 0, AZTICKS)
  ax.set_xticks(tticks)
  ax.set_rmax(90)
  ax.set_rmin(0)
  ax.set_title(fr'Ephemeris for {OBJECT} ({WHEN} localtime)', color = 'yellow', fontfamily = 'Helvetica')

  ax.set_xlabel('Azimuth')
  ax.set_ylabel('Elevation')

plt.show()
