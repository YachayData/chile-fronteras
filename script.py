import geopandas as gpd
from matplotlib import pyplot as plt
import requests
import pandas as pd
import numpy as np
import asyncio
import json
import aiohttp

df_map = gpd.read_file('V3.1_Limite_Internacional_50K/V3.1_Limite_Internacional.shp', driver='SHP',encoding='utf-8')
df = df_map[df_map['pais_c'].isin(['Argentina','Bolivia'])]


# script for returning elevation from lat, long, based on open elevation data
# which in turn is based on SRTM
def get_elevation(lat, long):
    query = ('https://api.open-elevation.com/api/v1/lookup'
             f'?locations={lat},{long}')
    r = grequests.get(query).json()  # json object, various ways you can extract value
    # one approach is to use pandas json functionality:
    elevation = pd.io.json.json_normalize(r, 'results')['elevation'].values[0]
    return elevation

arg0 = df['geometry'][0]
arg1 = df['geometry'][1]

x0, y0 = arg0[0].xy
xx0, yy0 = arg0[1].xy
x1, y1 = arg1.xy

x0 = np.array(x0)
xx0 = np.array(xx0)
x1 = np.array(x1)

y0 = np.array(y0)
yy0 = np.array(yy0)
y1 = np.array(y1)

x = np.append(x0, xx0)
x = np.append(x, x1)

y = np.append(y0, yy0)
y = np.append(y, y1)

#for i in range(x.shape[0]):
#	z[i] = get_elevation(y[i], x[i])
#	print(i / x.shape[0], z[i])

#z = [get_elevation(x[i], y[i]) for i in range(x.shape[0])]
query = [('https://api.open-elevation.com/api/v1/lookup'
         f'?locations={lat},{longi}') for (lat, longi) in zip(y,x)]

#r = requests.get(query).json()  # json object, various ways you can extract value
# one approach is to use pandas json functionality:
#elevation = pd.io.json.json_normalize(r, 'results')['elevation'].values[0]

resp_list = []
async def get(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            resp = resp.decode('utf-8')
            resp_list.append(json.loads(resp)['results'][0]['elevation'])
            print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def main(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get(url, session) for url in urls])
    print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))
    

asyncio.run(main(query))
z = np.array(resp_list)


