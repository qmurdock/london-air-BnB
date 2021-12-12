"""
Name: Quinn Murdock
CS230: Section 4 FA21
Data: LondonAirBnBSep2021.csv
URL:
Description:
This program allows the user to view data obout AirBnB rentals in London. There is a map that shows the location,
property name, and room type. There is a chart to show average listing price. The user inputs their criteria for what
they will see on the map and chart on a sidebar.
"""

import pandas as pd
import pydeck as pdk
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


# function to read in data
def read_data():
    return pd.read_csv("LondonAirBnBSep2021.csv").set_index("id")


# function to create a list of all the neighbourhoods sorted alphabetically
def all_neighbourhoods():
    df = read_data()
    neighbourhoodsList = []
    for ind, row in df.iterrows():
        if row["neighbourhood"] not in neighbourhoodsList:
            neighbourhoodsList.append(row["neighbourhood"])
    neighbourhoodsList.sort()
    return neighbourhoodsList


def filter_data(selected_neighbourhoods, max_price, min_availability):
    df = read_data()
    df = df.loc[df["neighbourhood"].isin(selected_neighbourhoods)]
    df = df.loc[df["price"] < max_price]
    df = df.loc[df["availability_365"] > min_availability]
    return df


def count_neighbourhoods(neighbourhoods, df):
    return [df.loc[df["neighbourhood"].isin([neighbourhood])].shape[0] for neighbourhood in neighbourhoods]


def neighbourhood_prices(df):
    prices = [row['price'] for ind, row in df.iterrows()]
    neighbourhoods = [row['neighbourhood'] for ind, row in df.iterrows()]
    dict = {}
    for neighbourhood in neighbourhoods:
        dict[neighbourhood] = []

    for i in range(len(prices)):
        dict[neighbourhoods[i]].append(prices[i])

    return dict


def neighbourhood_avg_prices(dict_prices):
    dict = {}
    for key in dict_prices.keys():
        dict[key] = np.mean(dict_prices[key])
    return dict


def bar_chart_avg_prices(dict_averages):
    plt.figure()
    x = dict_averages.keys()
    y = dict_averages.values()
    plt.bar(x, y)
    plt.xticks(rotation=90)
    plt.ylabel("Avg Price")
    plt.xlabel("Neighbourhoods")
    plt.title("Average Nightly Price by London Neighbourhood")
    return plt


def map_maker(df):
    df_bnb = df[['name', 'room_type', 'neighbourhood', 'latitude', 'longitude', 'room_type']]
    name_clean = df_bnb['name'].str.encode('ascii', 'ignore').str.decode('ascii')
    df_clean = df_bnb.copy()
    del df_clean["name"]
    df_clean["name"] = name_clean
    first_view = pdk.ViewState(
        latitude=df_bnb["latitude"].mean(),
        longitude=df_bnb["longitude"].mean(),
        zoom=9)
    tool_tip = {'html': "Property Name: <br/> {name} <br/> Room Type: <br/> <i>{room_type}<i>",
                'style': {"backgroundColor": 'white',
                          "color": 'black'}
                }
    layer = pdk.Layer('ScatterplotLayer',
                      data=df_bnb,
                      get_position='[longitude,latitude]',
                      pickable=True,
                      get_radius=100,
                      get_color=[0, 0, 200]
                      )
    london_map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                          layers=[layer],
                          initial_view_state=first_view,
                          tooltip=tool_tip)

    st.pydeck_chart(london_map)


def main():
    st.title('London AirBnBs')
    st.sidebar.write("Please select your view")

    neighbourhoods = st.sidebar.multiselect("Select the neighbourhoods you would like to see: ", all_neighbourhoods())
    max_price = st.sidebar.slider("Choose your maximum price: ", 0, 400)
    min_availability = st.sidebar.slider("Check the availability of each property: ", 0, 365)

    data = filter_data(neighbourhoods, max_price, min_availability)
    series = count_neighbourhoods(neighbourhoods, data)

    if len(neighbourhoods) > 0 and max_price > 0 and min_availability > 0:
        st.write("View a map of listings")
        map_maker(data)

        st.write("View a bar chart of average prices")
        st.pyplot(bar_chart_avg_prices(neighbourhood_avg_prices(neighbourhood_prices(data))))
        st.write("Select a column header to sort", data[['neighbourhood', 'name', 'price']])

    else:
        st.write("Begin by selecting options on the sidebar")
        st.image("https://lp-cms-production.imgix.net/news/2017/08/London.jpg?auto=format&fit=crop&sharp=10&vib=20&ixlib=react-8.6.4&w=850")

main()

data = read_data()
prices = neighbourhood_prices(data)
averages = neighbourhood_avg_prices(prices)
