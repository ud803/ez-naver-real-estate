import streamlit as st
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "authority": "new.land.naver.com",
    "method": "GET",
    "path": "/api/articles?cortarNo=1126010100&order=rank&realEstateType=DDDGG&tradeType=B2&tag=%3ATWOROOM%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0&rentPriceMax=900000000&priceMin=0&priceMax=5000&areaMin=15&areaMax=236&oldBuildYears=25&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount&showArticle=false&sameAddressGroup=true&minMaintenanceCost&maxMaintenanceCost&priceType=RETAIL&directions=&page=1&articleState",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "authorization": os.getenv("NAVER_AUTHORIZATION"),
    "cookie": os.getenv("NAVER_COOKIE"),
    "priority": "u=1, i",
    "referer": "https://new.land.naver.com/houses?ms=37.5722735,127.0901325,17&a=DDDGG&b=B2&e=RETAIL&g=5000&h=15&i=236&j=25&q=TWOROOM&ad=true",
    "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
    "sec-ch-ua-mobile": "?0", 
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors", 
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}

cortar_map = {
    '군자역(북)~중곡역': 1121510100
    ,'군자역(남서)': 1121510900
    ,'군자역(남동)': 1121510200
    ,'아차산~구의': 1121510300
    ,'장한평(북)': 1123010600
    ,'장한평(남)~답십리(남)': 1120012200
    ,'답십리(북)': 1123010500
    ,'광나루': 1121510400
    ,'건대입구(북)': 1121510700
    ,'건대입구(남)': 1121510500
    ,'성수역': 1120011500
    ,'뚝섬역': 1120011400
}

import requests

def get_real_estate_data(params):
    url = f"https://new.land.naver.com/api/articles"

    session = requests.Session()
    articles = []

    with st.spinner(f"데이터 불러오는 중..."):
        while True:
            response = session.get(url, headers=headers, params=params)

            if response.status_code == 200:
                try:
                    data = response.json()
                    articles += data['articleList']
                    if data['isMoreData']:
                        params['page'] += 1
                    else:
                        break

                except Exception as e:
                    st.warning("JSON 파싱 실패:", e)
            else:
                st.warning("요청 실패, 상태 코드:", response.status_code)
                break

            time.sleep(1)
        st.info(f"{params['cortarNo']}에서 총 {len(articles)}개의 데이터를 불러왔습니다.")
    return articles


def render_real_estate_list():

    _, col = st.columns([8, 3])

    with st.form(key='estate_form'):
        area_name = st.selectbox("지역 선택", sorted(cortar_map.keys()))

        col2, col3 = st.columns([2, 1])

        with col2:
            estate_type = st.multiselect("부동산 종류", ["아파트", "오피스텔", "원룸", "빌라/연립", "단독/다가구", "전원주택", "상가주택", "한옥주택"], placeholder="복수 선택")
            estate_map = {
                "아파트": "APT"
                ,"오피스텔": "OPST"
                ,"원룸": "OR"
                ,"빌라/연립": "VL"
                ,"단독/다가구": "DDDGG"
                ,"전원주택": "JWJT"
                ,"상가주택": "SGJT"
                ,"한옥주택": "HOJT"
            }
            estate_type = ':'.join([estate_map[i] for i in estate_type])
        with col3:
            trade_type = st.multiselect("거래 종류", ["월세", "전세", "매매"], placeholder="복수 선택")
            trade_map = {
                "월세": "B2"
                ,"전세": "B1"
                ,"매매": "A1"
            }
            trade_type = ':'.join([trade_map[i] for i in trade_type])

        warrant_price = st.slider("보증금(만원)", value=(0, 5500), min_value=0, max_value=100000, step=100)
        rent_price = st.slider("월세(만원)", value=(0, 65), min_value=0, max_value=500, step=10)
        min_area = st.slider("최소 전용면적(㎡)", value=27, min_value=0, max_value=100, step=1)

        col1, col2 = st.columns(2)

        with col1:
            exclude_floors = st.multiselect("제외 층수", options=['B1', '1', '2', '저'])
        with col2:
            exclude_tags = st.multiselect("제외 태그", options=[
                '25년이상'
                , '25년이내'
            ])

        pre_params = {
            "realEstateType": estate_type
            ,"tradeType": trade_type
            ,"priceMin": warrant_price[0]
            ,"priceMax": warrant_price[1]
            ,"rentPriceMin": rent_price[0]
            ,"rentPriceMax": rent_price[1]
            ,"order": "rank"
            ,"page": 1
        }

        if st.form_submit_button("네이버 부동산 검색"):
            articles = []

            pre_params["cortarNo"] = cortar_map[area_name]
            data = get_real_estate_data(pre_params)
            articles += data

            df = pd.DataFrame.from_dict(data)

            cond_1 = df['area2'] >= min_area
            cond_2 = ~df["floorInfo"].apply(lambda x: x.split('/')[0]).isin(exclude_floors)
            cond_3 = ~df["tagList"].apply(lambda x: any([tag in x for tag in exclude_tags])) 

            df = df[cond_1 & cond_2 & cond_3]

            st.info(f"총 매물 {len(articles)}개.. 조건에 맞는 매물 {len(df)}개")

            column_map = {
                "articleNo": "articleNo"
                # ,"articleStatus":
                # ,"realEstateTypeName": "중분류"
                ,"articleName": "소분류"
                ,"tradeTypeName": "거래유형"
                ,"floorInfo": "층수"
                ,"dealOrWarrantPrc": "보증금"
                ,"rentPrc"  : "월세"
                # ,"priceChangeState" : "가격변동"
                ,"area1": "공용면적"
                ,"area2": "전용면적"
                ,"direction": "방향"
                ,"articleFeatureDesc": "특징"
                ,"tagList": "태그"
                # ,"sameAddrMaxPrc": "동일주소 최고가"
                # ,"sameAddrMinPrc": "동일주소 최저가"
                ,"cpName": "출처"
                ,"cpPcArticleUrl": "링크"
                ,"latitude": "latitude"
                ,"longitude": "longitude"
                ,"articleConfirmYmd": "확인일자"
                ,"realtorName": "부동산"
                ,"tradeCheckedByOwner": "집주인확인"
            }

            df = df[[i for i in column_map.keys() if i in df.columns]]
            df = df.rename(columns=column_map)

            df["latitude"] = df["latitude"].astype(float)
            df["longitude"] = df["longitude"].astype(float)

            st.session_state['real_estate_df'] = df
    
    if 'real_estate_df' in st.session_state:
        st.dataframe(st.session_state['real_estate_df'])

        col1, col2 = st.columns([8, 2])

        with col1:
            selected_house = st.selectbox("매물 선택", st.session_state['real_estate_df']["articleNo"].tolist())
        with col2:
            st.markdown(f"[매물 바로가기](https://new.land.naver.com/houses?articleNo={selected_house})")
        selected_house_df = st.session_state['real_estate_df'][st.session_state['real_estate_df']["articleNo"] == selected_house]
        st.map(selected_house_df, latitude='latitude', longitude='longitude', size=20, zoom=16)


st.title('EZ 네이버 부동산')
render_real_estate_list()