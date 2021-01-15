import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import altair as alt
from vega_datasets import data

st.write("# Analysis of McDonalds Locations in the United States: ")

#df = pd.read_csv(DataFile)
DataFile = "mcdonalds"
df = pd.read_json(DataFile + ".json")

numLocations = len(df)

longitudes = []
latitudes = []
coordinates = []
for i in range(0, numLocations):
    coordinates_temp = []
    longitudes.append(df["X"][i])
    latitudes.append(df["X"][i])
    coordinates_temp.append(df["X"][i])
    coordinates_temp.append(df["Y"][i])
    coordinates.append(coordinates_temp)

df["coordinates"] = coordinates
df["setRadius"] = [30] * numLocations

st.write("## A table of all McDonalds Locations in the US: ")
df

st.write("## Map All McDonalds Restaurants ")

# Define a layer to display on a map
layer = pdk.Layer(
    type="ScatterplotLayer",
    data=df,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=6,
    radius_min_pixels=1,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_position="coordinates",
    get_radius="setRadius",
    get_fill_color=[255, 140, 0],
    get_line_color=[0, 0, 0]
)

# Set the viewport location at center of US
view_state = pdk.ViewState(latitude=38.00, longitude=-97.00, zoom=3, bearing=0, pitch=0)
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{address}"})
st.pydeck_chart(r)

st.write("## Compare the number of McDonalds outlets in any 5 States")
statesInput = st.text_input("Enter the 5 states to compare", "MA CT VT NH NY")
states = statesInput.split()

num1 = 0
num2 = 0
num3 = 0
num4 = 0
num5 = 0
numStores=[]
for i in range(0, numLocations):
    if (df["state"][i] == states[0]):
        num1 +=1
    if (df["state"][i] == states[1]):
        num2 +=1
    if (df["state"][i] == states[2]):
        num3 +=1
    if (df["state"][i] == states[3]):
        num4 +=1
    if (df["state"][i] == states[4]):
        num5 +=1

numStores.append(num1)
numStores.append(num2)
numStores.append(num3)
numStores.append(num4)
numStores.append(num5)

df2 = pd.DataFrame({
    'states': states,
    'NumberOutlets': numStores
    })

df2 = df2.set_index('states')
df2
st.line_chart(df2)

st.write(f"All the McDonalds in the first State you entered, {states[0]}")
queryString = "state == '" + states[0] + "'"
df4 = df.query(queryString)
df4
midpoint = (np.average(df4['X']), np.average(df4['Y']))

# Define a layer to display on a map
layer = pdk.Layer(
    type="ScatterplotLayer",
    data=df4,
    pickable=True,
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=6,
    radius_min_pixels=1,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_position="coordinates",
    get_radius="setRadius",
    get_fill_color=[255, 140, 0],
    get_line_color=[0, 0, 0]
)

# Set the viewport location
view_state = pdk.ViewState(latitude=midpoint[1], longitude=midpoint[0], zoom=5, bearing=0, pitch=0)
r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{address}"})
st.pydeck_chart(r)

st.write("## Count the number of McDonalds outlets by States and Cities")
df = df.set_index('state')
countByState = df.groupby(['state'])[['address']].count()
st.write("### Count by State")
countByState
st.line_chart(countByState)

st.write("### The 4 Cities that have most McDonalds Locations")

# note that we need to use state in the 'group by' because the same city name can be used in multiple states
countByCity = df.groupby(['city', 'state'])[['address']].count()

# sort in decending value and get the top 4 cities
countByCity.sort_values(by=['address'], inplace=True, ascending=False)
topCities = countByCity.head(4)
topCities

# Using the altair library here to map the lines between the 4 cities

DataFile = "mcdonalds.json"
df = pd.read_json(DataFile)

city = topCities.index.values[0][0]
state = topCities.index.values[0][1]
queryString = 'city == "' + city + '" and state == "' + state + '"'
cities = df.query(queryString).head(1)
#cities
city = topCities.index.values[1][0]
state = topCities.index.values[1][1]
queryString = 'city == "' + city + '" and state == "' + state + '"'
city2 = df.query(queryString).head(1)
cities = cities.append(city2, ignore_index=True)

city = topCities.index.values[2][0]
state = topCities.index.values[2][1]
queryString = 'city == "' + city + '" and state == "' + state + '"'
city3 = df.query(queryString).head(1)
cities = cities.append(city3, ignore_index=True)

city = topCities.index.values[3][0]
state = topCities.index.values[3][1]
queryString = 'city == "' + city + '" and state == "' + state + '"'
city4 = df.query(queryString).head(1)
cities = cities.append(city4, ignore_index=True)
#cities

st.write("### Choose the order you want to travel to the 4 cities that have most McDonalds Restaurants")
orderInput = st.text_input(f"1:{cities['city'][0]} 2:{cities['city'][1]} 3:{cities['city'][2]} 4:{cities['city'][3]}", "1 2 3 4")
order = orderInput.split()

# add a column to capture the order
cities['order'] = order
#cities

states = alt.topo_feature(data.us_10m.url, feature='states')

# plot a line between locations
background = alt.Chart(states).mark_geoshape(
    fill='lightgray',
    stroke='white'
).properties(
    width=800,
    height=500
).project('albersUsa')

point_path = line_path = alt.Chart(cities).mark_circle().encode(
    longitude="X:Q",
    latitude="Y:Q",
    size=alt.value(100)
)

line_path = alt.Chart(cities).mark_line().encode(
    longitude="X:Q",
    latitude="Y:Q",
    order='order:O'
)

st.altair_chart((background + point_path + line_path))

# find nearest location
st.write("## Find McDonalds Restaurant Closest To Me")
myLat = st.number_input("Enter your location in Latitude (e.g. 42.272)")
myLon = st.number_input("Enter your location in Longtitude (e.g. -71.228)")

numLocations = len(df)
locationNum = 1
dist = 1000
for i in range(0, numLocations):
    toLat = df["Y"][i]
    toLon = df["X"][i]
    distanceLat = abs(abs(myLat) - abs(toLat))
    distanceLon = abs(abs(myLon) - abs(toLon))
    # use pythagoren calc to get the straight-line distance between the two points
    newDist = np.sqrt(np.square(distanceLat) + np.square(distanceLon))
    if newDist < dist:
        dist = newDist 
        locationNum = i

closestAddress = df['address'][locationNum]
closestCity = df['city'][locationNum]
closestState = df['state'][locationNum]
st.write(f"Closest location is {closestAddress}, {closestCity}, {closestState}")

st.write("# End of Analysis ")
