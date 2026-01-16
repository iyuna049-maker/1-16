import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import platform
import os
from matplotlib import font_manager, rc

# -----------------------------------------------------------------------------
# [1] 폰트 설정 (가장 강력한 방법으로 수정)
# -----------------------------------------------------------------------------
@st.cache_resource
def setup_font():
    # 폰트 파일 이름이 정확한지(대소문자 구분) 꼭 확인하세요!
    font_file = "NanumGothic.ttf" 
    
    if os.path.exists(font_file):
        # 1. 폰트 매니저에 파일 경로를 직접 추가 (이게 핵심입니다!)
        font_manager.fontManager.addfont(font_file)
        # 2. 추가된 폰트의 '패밀리 이름'을 가져옴
        custom_font_name = font_manager.FontProperties(fname=font_file).get_name()
        # 3. rc에 적용
        rc('font', family=custom_font_name)
        print(f"✅ 폰트 파일 로드 성공: {custom_font_name}")
    else:
        # 파일이 없을 경우 OS 기본 폰트 사용
        print("⚠️ NanumGothic.ttf 파일을 찾을 수 없어 기본 폰트를 사용합니다.")
        if platform.system() == 'Windows':
            rc('font', family='Malgun Gothic')
        elif platform.system() == 'Darwin': # Mac
            rc('font', family='AppleGothic')
        else: # Linux/Streamlit Cloud
            rc('font', family='NanumGothic')
            
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

setup_font()

# -----------------------------------------------------------------------------
# [2] 페이지 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="박사 근로소득 통계 분석", layout="wide")
st.title("📊 이공계 박사 근로소득 데이터 분석기")

file_path = "과학기술정보통신부_이공계인력실태조사_박사 근로소득 통계_20101231.csv"

# -----------------------------------------------------------------------------
# [3] 데이터 로드 (인코딩 순서 변경이 핵심!)
# -----------------------------------------------------------------------------
def load_data(path):
    # 중요!! 공공데이터(csv)는 99%가 'cp949'입니다.
    # utf-8을 먼저 시도하면, 깨진 채로 읽히는 경우가 많으니 'cp949'를 1순위로 둡니다.
    encodings = ['cp949', 'euc-kr', 'utf-8-sig', 'utf-8']
    
    for encoding in encodings:
        try:
            df = pd.read_csv(path, encoding=encoding)
            # 컬럼명 앞뒤 공백 제거
            df.columns = df.columns.str.strip()
            return df, encoding
        except Exception:
            continue
    return None, None

try:
    df, used_encoding = load_data(file_path)

    if df is not None:
        st.success(f"✅ 데이터 로드 성공! (적용된 인코딩: {used_encoding})")

        # 데이터 정보 표시
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("전체 데이터 수", f"{len(df):,}개")
        col_m2.metric("컬럼 수", f"{len(df.columns)}개")

        # 데이터 미리 보기
        with st.expander("📝 데이터 원본 보기", expanded=True):
            st.dataframe(df.head(10), use_container_width=True)

        st.divider()

        # [4] 시각화 섹션
        st.subheader("📈 항목별 분포 시각화")
        
        # 숫자형 데이터만 추출
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

        if numeric_columns:
            c1, c2 = st.columns([1, 3])
            
            with c1:
                selected_col = st.selectbox("분석할 항목 선택:", numeric_columns)
                bins = st.slider("막대 개수(Bins):", 5, 50, 20)
                graph_color = st.color_picker("그래프 색상:", "#6C63FF")
                show_kde = st.checkbox("부드러운 곡선(KDE) 보기", value=True)

            with c2:
                # 그래프 그리기
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # 데이터가 비어있지 않은지 확인 후 그리기
                plot_data = df[selected_col].dropna()
                
                sns.histplot(plot_data, bins=bins, kde=show_kde, ax=ax, color=graph_color)
                
                ax.set_title(f"[{selected_col}] 분포도", fontsize=16, pad=20)
                ax.set_xlabel(selected_col)
                ax.set_ylabel("빈도수")
                
                st.pyplot(fig)
        else:
            st.warning("⚠️ 그래프를 그릴 수 있는 숫자 데이터가 없습니다. (데이터가 모두 문자로 인식되었을 수 있습니다.)")

    else:
        st.error(f"❌ '{file_path}' 파일을 읽을 수 없습니다. 파일이 폴더에 있는지 확인해주세요.")

except Exception as e:
    st.error(f"❌ 오류가 발생했습니다: {e}")