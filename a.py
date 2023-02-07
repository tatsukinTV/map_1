import folium
from streamlit_folium import folium_static
import streamlit as st
import pandas as pd

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