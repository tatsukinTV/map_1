import folium
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import json
import requests
import time

pages = ['range', 'scatter', 'bar_graph', 'scatter&heat']

selector = st.sidebar.selectbox('ページ選択', pages)

if selector == 'range':
    # サンプル用の緯度経度データを作成する
    sales_office = pd.DataFrame(
        data=[[32.0,131.1],
            [33.1,131.2],
            [34.2,131.3]],
        index=["本社","A営業所","B営業所"],
        columns=["x","y"]
    )

    # データを地図に渡す関数を作成する
    def AreaMarker(df,m):
        for index, r in df.iterrows(): 

            # ピンをおく
            folium.Marker(
                location=[r.x, r.y],
                popup=index,
            ).add_to(m)

            # 円を重ねる
            folium.Circle(
                radius=rad*1000,
                location=[r.x, r.y],
                popup=index,
                color="yellow",
                fill=True,
                fill_opacity=0.07
            ).add_to(m)

    # ------------------------画面作成------------------------

    st.title("サンプル地図") # タイトル
    rad = st.slider('拠点を中心とした円の半径（km）',
                    value=40,min_value=5, max_value=50) # スライダーをつける
    st.subheader("各拠点からの距離{:,}km".format(rad)) # 半径の距離を表示
    m = folium.Map(location=[33.1,131.0], zoom_start=7) # 地図の初期設定
    AreaMarker(sales_office,m) # データを地図渡す
    folium_static(m) # 地図情報を表示


elif selector == 'scatter':
    """
    # 初めての Streamlit
    データフレームを表として出力できます:
    """

    df = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
    })


    """
    # グラフ描画の例
    """

    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])

    st.line_chart(chart_data)


    """
    # 地図を描画
    """

    map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [35.68109, 139.76719],
    columns=['lat', 'lon'])

    st.map(map_data)


    """
    # ウィジェットの例
    """

    if st.checkbox("チェックボックス"):
        st.write("チェックが入りました。")

        selection = st.selectbox("セレクトボックス", ["1", "2", "3"])
        st.write(f"{selection} を選択")

    """
    ## プログレスバーとボタン
    """

    if st.button("ダウンロード"):
        text = st.empty()
        bar = st.progress(0)

        for i in range(100):
            text.text(f"ダウンロード中 {i + 1}/100")
            bar.progress(i + 1)
            time.sleep(0.01)


elif selector == 'bar_graph':
    # SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
    st.title('Osaka Precipitation')

    # LOAD DATA ONCE
    @st.experimental_singleton
    def load_data():
        data = pd.read_csv(
            "./c_map_data.csv",
            nrows=825,
            names=[
                "lat",
                "lon"
            ],
            skiprows=1, # コメント行をスキップ
            usecols=[2, 3],  # 3、4列目を使用する
        )
        return data


    # FUNCTION FOR AIRPORT MAPS
    def map(data, lat, lon, zoom):
        st.write(
            pdk.Deck(
                map_style="mapbox://styles/mapbox/light-v8",
                initial_view_state={
                    "latitude": lat,
                    "longitude": lon,
                    "zoom": zoom,
                    "pitch": 10,
                },
                layers=[
                    pdk.Layer(
                        'HexagonLayer',
                        data=data,
                        get_position='[lon, lat]',
                        radius=750,
                        elevation_scale=4,
                        elevation_range=[0, 5000],
                        pickable=True,
                        extruded=True,
                    ),
                ],
            )
        )


    # CALCULATE MIDPOINT FOR GIVEN SET OF DATA
    @st.experimental_memo
    def mpoint(lat, lon):
        return np.average(lat), np.average(lon)


    # STREAMLIT APP LAYOUT
    data = load_data()

    # SETTING THE ZOOM LOCATIONS FOR THE AIRPORTS
    zoom_level = 12
    midpoint = mpoint(data["lat"], data["lon"])
    map(data, midpoint[0], midpoint[1], 8.5)


elif selector == 'scatter&heat':
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
