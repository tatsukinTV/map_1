import json
import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

class MyDecoder(json.JSONDecoder):
    def decode(self, s):
        result = super().decode(s)
        return self._decode(result)
    
    def _decode(self, o):
        if isinstance(o, str):            
            try:
                if '.' in o:
                    return float(o)
                return int(o)
            except ValueError:
                return o
        elif isinstance(o, dict):
            return {k: self._decode(v) for k, v in o.items()}
        elif isinstance(o, list):
            return [self._decode(v) for v in o]
        else:
            return o

@st.cache
def load_data():
    response = requests.get("https://ckan.pf-sapporo.jp/api/action/datastore_search?resource_id=f2599ba4-0340-40e1-9735-5516541649f6&limit=3000", verify=False)
    response_json = MyDecoder().decode(response.text)
    df = pd.json_normalize(response_json, record_path=["result", "records"])
    return df


df = load_data().copy() \
        .drop(columns=["名称＿カナ", "方書", "備考", "市町村名", "電話番号", "都道府県名"])

WARD_COLORS = {
    1101: [255, 32, 32, 160],
    1102: [64, 128, 64, 160],
    1103: [32, 128, 255, 160],
    1104: [0, 255, 0, 160],
    1105: [0, 0, 255, 160],
    1106: [255, 0, 255, 160],
    1107: [128, 0, 255, 160],
    1108: [255, 0, 128, 160],
    1109: [255, 128, 0, 160],
    1110: [139, 69, 19, 160],
}
df["ward_color"] = df["区コード"].apply(lambda x: WARD_COLORS[x])


st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/streets-v11',
    initial_view_state=pdk.ViewState(
        latitude=43.05,
        longitude=141.35,
        zoom=10.5,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[経度, 緯度]',
            get_fill_color="ward_color",
            get_radius=100,
        ),
    ],
))


st.pydeck_chart(pdk.Deck(
map_style='mapbox://styles/mapbox/light-v10',
initial_view_state=pdk.ViewState(
    latitude=43.05,
    longitude=141.35,
    zoom=10.5,
    pitch=50,
),
layers=[
    pdk.Layer(
        'HeatmapLayer',
        data=df,
        get_position='[経度, 緯度]',
        radius=200,
        elevation_scale=4,
        elevation_range=[0, 1000]
    )
],
))

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v10',
    initial_view_state=pdk.ViewState(
        latitude=43.05,
        longitude=141.35,
        zoom=10.5,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HeatmapLayer',
            data=df,
            get_position='[経度, 緯度]',
            get_weight="病床数",
            opacity=0.8,
            cell_size_pixels=15,
            elevation_scale=4,
            elevation_range=[0, 1000]
        )
    ],
))