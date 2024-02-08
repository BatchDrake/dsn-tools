#!/usr/bin/env python3
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

zInc = 50

def plot_locations(
  ax,
  tt,
  az,
  el,
  color = 'white',
  text_color = None,
  bbox = False,
  prefix = None,
  shift_x = 0,
  start = None,
  align = 'left'):

  global zInc

  if len(az) == 0:
    return
  
  dAz = 0
  dEl = 0
  
  if text_color is None:
    text_color = color
  
  # Plot locations
  ax.scatter(az, el, color = color, zorder = 50 + zInc)
  zInc += 1
  
  # Tag them
  if start is None:
    start = tt[0]

  
  for i in range(len(az)):
    curr = tt[i]

    ellapsed = curr - start

    suffix = ''
    if ellapsed.days > 0:
      suffix = fr' (+{ellapsed.days} days)'
    elif start.day != curr.day:
      suffix = fr' (day after)'
    
    if prefix is None:
      prefix = '   '

    tEl = np.abs(el[i])
    tAz = az[i]
    
    if shift_x != 0:
      x = (90 - tEl) * np.cos(tAz) + shift_x
      y = (90 - tEl) * np.sin(tAz)

      tAz  = np.arctan2(y, x)
      tEl  = 90 - np.sqrt(x ** 2 + y ** 2)
      
    t = ax.text(
	    tAz,
	    tEl,
	    fr'{prefix}{tt[i].strftime("%H:%M:%S")}{suffix}',
	    color = text_color,
	    horizontalalignment = align,
            verticalalignment = 'center_baseline',
	    fontfamily = 'Helvetica',
      zorder = 50 + zInc)

    zInc += 1
    
    if bbox:
      t.set_bbox(dict(facecolor='black', edgecolor = text_color, boxstyle = 'round'))
    

if len(sys.argv) != 2:
    print(fr'Usage: {sys.argv[0]} PROBE')
    sys.exit(1)

OBJECT = sys.argv[1]
WHEN   = datetime.now()

forecast = Forecast()

try:
  print(fr'{sys.argv[0]}: Querying JPL Horizons...')
  tt, az, el, R, dRdt, vis = forecast.query(OBJECT, start = WHEN)
except Exception as e:
  print(fr'{sys.argv[0]}: failed to acquire ephemeris: {e}')
  sys.exit(1)

print(fr'{sys.argv[0]}: Done. Processing data...')

azRad = np.deg2rad(az)
elRad = np.deg2rad(el)

with plt.rc_context(style):
  fig, ax = plt.subplots(subplot_kw = {'projection': 'polar'})
  ax.set_rlim(bottom = 90, top = 0)

  visible = (el > 0) & (vis == True)
  notvis  = ~visible

  elVis = el.copy()
  elVis[notvis] = np.nan

  elOcc = el.copy()
  elOcc[visible] = np.nan
  
  # Plot path in the sky
  ax.plot(azRad, elVis, color = PATH_COLOR, zorder = 30)
  

  ax.plot(azRad, elOcc, color = LOS_COLOR, zorder = 30)
  ax.plot(azRad, -elOcc, color = LOS_COLOR, zorder = 30, linestyle = 'dotted', alpha = .25)
  
  diff    = np.array([0.] + np.diff(visible.astype('float')).tolist())

  aos     = diff > 0
  los     = diff < 0
  
  Nvis    = len(el[visible])
  step    = Nvis // N_DATE_STEPS
  
  dateAz  = azRad[visible][::step]
  dateEl  = el[visible][::step]
  ttVis   = np.array(tt)[visible][::step]
  plot_locations(
    ax,
    ttVis,
    dateAz,
    dateEl,
    color = PATH_COLOR,
    text_color = 'white',
    start = tt[0])

  aosAz   = azRad[aos]
  aosEl   = el[aos]
  aosTT   = np.array(tt)[aos]
  plot_locations(
    ax,
    aosTT,
    aosAz,
    aosEl,
    color = AOS_COLOR,
    bbox = True,
    prefix = 'AOS: ',
    start = tt[0],
    shift_x = -5,
    align = 'right')

  losAz   = azRad[los]
  losEl   = el[los]
  losTT   = np.array(tt)[los]
  plot_locations(
    ax,
    losTT,
    losAz,
    losEl,
    color = LOS_COLOR,
    bbox = True,
    prefix = 'LOS: ',
    shift_x = -5,
    align = 'right')

  ax.set_facecolor(style['figure.facecolor'])
  ax.grid(color = GRID_COLOR, linestyle = 'dashed')
  
  if el[0] > 0:
    plot_locations(
      ax,
      [tt[0]],
      azRad[0:1],
      el[0:1],
      color = '#00ffff',
      prefix = 'VISIBLE NOW: ',
      bbox = True,
      shift_x = -5,
      align = 'right')

  ax.set_theta_direction(-1)
  
  tticks = np.linspace(2 * np.pi * (AZTICKS - 1) / (AZTICKS), 0, AZTICKS)
  ax.set_xticks(tticks)
  fig.suptitle(
    fr'Ephemeris for $\bf{{{OBJECT}}}$ ({WHEN.strftime("%Y-%m-%d %H:%M:%S")} localtime)',
    color = 'yellow',
    fontweight = 'bold')

  ax.set_xlabel('Azimuth')
  ax.set_ylabel('Elevation')

plt.tight_layout()
plt.show()
