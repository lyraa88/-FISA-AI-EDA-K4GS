import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# CSV 데이터 불러오기
df = pd.read_csv("2024_price.csv")

# 물건금액 범위 동적으로 계산
min_price_val = df["물건금액"].min()
max_price_val = df["물건금액"].max()

# 고정값 세팅
building_year_categories = ['2020년대', '2010년대', '2000년대', '1990년대', '1980년대', '1979년 이하']
building_types = ["연립다세대", "아파트", "오피스텔", "단독다가구"]
floor_options = ['05층이하', '10층이하', '15층이하', '20층이하', '00층 이하', '30층이하', '40층이하', '50층이하']
area_options = ['10평 미만', '10평대', '20평대', '50평대', '30평대', '60평대 이상', '40평대']

# 서울 구 좌표
seoul_gu_coords = {
    "종로구": [37.572950, 126.979357], "중구": [37.563757, 126.997730], "용산구": [37.532600, 126.990860],
    "성동구": [37.563680, 127.036580], "광진구": [37.538420, 127.082550], "동대문구": [37.574400, 127.039390],
    "중랑구": [37.606570, 127.092720], "성북구": [37.589910, 127.016900], "강북구": [37.639970, 127.025980],
    "도봉구": [37.668530, 127.047980], "노원구": [37.654290, 127.056950], "은평구": [37.602570, 126.929620],
    "서대문구": [37.579680, 126.936880], "마포구": [37.566680, 126.901450], "양천구": [37.516340, 126.866940],
    "강서구": [37.550940, 126.849530], "구로구": [37.495650, 126.887770], "금천구": [37.456430, 126.895160],
    "영등포구": [37.526640, 126.896210], "동작구": [37.512650, 126.939930], "관악구": [37.478090, 126.951590],
    "서초구": [37.483570, 127.032660], "강남구": [37.517200, 127.047320], "송파구": [37.514560, 127.105570],
    "강동구": [37.530130, 127.123820],
}

# 특정 건물 위경도 정보
apartment_coords = {
    "송파호반베르디움더퍼스트": [37.5083, 127.1056],
    "송파파크데일1단지": [37.498914, 127.159191],
    "송파파크데일2단지": [37.4963394415, 127.1581638948],
    "위례신도시송파푸르지오": [37.4699015, 127.151302167],
}

gu_options = ["전체"] + list(seoul_gu_coords.keys())

floor_map = {
    '00층 이하': 0, '05층이하': 5, '10층이하': 10, '15층이하': 15,
    '20층이하': 20, '30층이하': 30, '40층이하': 40, '50층이하': 50,
}

st.set_page_config(page_title="부동산 대시보드", layout="wide")
st.title("🏙️ 서울 부동산 필터링 + 지도")

st.sidebar.header("🔎 필터 조건 선택")

selected_gu = st.sidebar.selectbox("서울의 구 선택", gu_options)
selected_year_category = st.sidebar.selectbox("건축년도 구분", building_year_categories, index=2)
selected_building_type = st.sidebar.selectbox("건물 종류", building_types)
selected_area = st.sidebar.selectbox("면적 (평)", area_options)
selected_floor = st.sidebar.selectbox("건물 층수", floor_options)

selected_price = st.sidebar.slider(
    "예산 (억 단위 기준)",
    min_value=float(min_price_val),
    max_value=float(max_price_val),
    value=float(max_price_val),
    step=0.1,
    format="%.2f"
)

max_floor = floor_map.get(selected_floor, 50)

# 예산 기준 +-1억 허용
min_budget = max(0, selected_price - 1)
max_budget = selected_price + 1

filtered_df = df[
    (df["건축년도구분"] == selected_year_category) &
    (df["건물용도"] == selected_building_type) &
    (df["건물면적구분"] == selected_area) &
    (df["층"].fillna(0) <= max_floor) &
    (df["물건금액"] <= max_budget)
]

if selected_gu != "전체":
    filtered_df = filtered_df[filtered_df["자치구명"] == selected_gu]

# 지도 중심 설정
default_center = [37.5665, 126.9780]
map_center = seoul_gu_coords.get(selected_gu, default_center)

m = folium.Map(location=map_center, zoom_start=13 if selected_gu != "전체" else 11)

if selected_gu == "전체":
    for gu, coords in seoul_gu_coords.items():
        folium.Marker(location=coords, popup=gu, tooltip=gu,
                      icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)
else:
    folium.Marker(location=map_center, popup=selected_gu, tooltip=selected_gu,
                  icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)

# 🔍 필터링된 결과에 특정 건물이 있다면 지도에 마커 추가
for apt_name, coords in apartment_coords.items():
    matching = filtered_df[filtered_df["건물명"].str.contains(apt_name, na=False)]
    if not matching.empty:
        folium.Marker(
            location=coords,
            popup=f"{apt_name} (필터 매칭됨)",
            tooltip=apt_name,
            icon=folium.Icon(color='red', icon='home')
        ).add_to(m)

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📌 선택한 구 지도 표시")
    st_folium(m, width=700, height=600)

with col2:
    st.subheader("🎯 현재 선택된 필터")
    st.markdown(f"""
    - **건축년도 구분**: {selected_year_category}  
    - **건물 종류**: {selected_building_type}  
    - **면적**: {selected_area}  
    - **건물 층수**: {selected_floor} (최대 {max_floor}층 이하)  
    - **예산**: {selected_price}억 ± 1억 (범위: {min_budget} ~ {max_budget})  
    - **선택한 구**: {selected_gu}
    """)
    st.write(f"🔎 매물 수: {len(filtered_df)}건")

# 매물 목록 출력
with st.expander("🏠 조건에 맞는 집 목록 보기 (모든 컬럼)"):
    st.dataframe(filtered_df.reset_index(drop=True))