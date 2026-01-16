import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import platform
import os
from matplotlib import font_manager, rc

# 1. 한글 폰트 강제 설정 (NanumGothic.ttf 사용)
@st.cache_resource
def setup_font():
    font_file = "NanumGothic.ttf"
    
    # 1순위: 같은 폴더에 NanumGothic.ttf가 있는지 확인
    if os.path.exists(font_file):
        font_name = font_manager.FontProperties(fname=font_file).get_name()
        rc('font', family=font_name)
    else:
        # 2순위: 파일이 없을 경우 OS별 기본 한글 폰트 사용
        if platform.system() == 'Windows':
            rc('font', family='Malgun Gothic')
        elif platform.system() == 'Darwin': # Mac
            rc('font', family='AppleGothic')
        else: # Linux/Streamlit Cloud
            rc('font', family='NanumGothic')
            
    plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

setup_font()

st.set_page_config(page_title="국세청 근로소득 분석기", layout="wide")
st.title("📊 국세청 근로소득 데이터 분석기")

# 데이터 불러오기
file_path = "과학기술정보통신부_이공계인력실태조사_박사 근로소득 통계_20101231.csv"

# 2. 인코딩 에러 방지를 위한 다중 로드 시도
def load_data(path):
    # 'utf-8-sig'를 가장 먼저 시도 (이미지에서 성공했던 인코딩)
    encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']
    for encoding in encodings:
        try:
            df = pd.read_csv(path, encoding=encoding)
            # 컬럼명 앞뒤 공백 제거 (매우 중요)
            df.columns = df.columns.str.strip()
            return df, encoding
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return None, None

try:
    df, used_encoding = load_data(file_path)

    if df is not None:
        st.success(f"✅ 데이터를 성공적으로 불러왔습니다! (인코딩: {used_encoding})")

        # 상단 요약 정보 (Metrics)
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("전체 데이터 수", f"{len(df):,}")
        col_m2.metric("분석 가능 항목 수", len(df.select_dtypes(include=[np.number]).columns))

        # 데이터 미리 보기
        with st.expander("📝 데이터 원본 보기", expanded=False):
            st.dataframe(df, use_container_width=True)

        st.divider()

        # 3. 데이터 시각화 섹션
        st.subheader("📈 항목별 분포 시각화")
        
        # 수치형 데이터만 추출
        numeric_columns = df.select_dtypes(include=['number']).columns.tolist()

        if numeric_columns:
            # 설정 레이아웃
            c1, c2 = st.columns([1, 3])
            
            with c1:
                st.info("그래프 설정을 조절하세요.")
                selected_col = st.selectbox("분석할 항목 선택:", numeric_columns)
                bins = st.slider("막대 세밀도(Bins):", 5, 100, 30)
                graph_color = st.color_picker("그래프 색상:", "#6C63FF")
                show_kde = st.checkbox("밀도 곡선(KDE) 표시", value=True)

            with c2:
                # 그래프 그리기
                fig, ax = plt.subplots(figsize=(10, 6))
                # NaN 값이 있을 경우 히스토그램에서 에러가 날 수 있으므로 dropna() 적용
                sns.histplot(df[selected_col].dropna(), bins=bins, kde=show_kde, ax=ax, color=graph_color)
                
                ax.set_title(f"<{selected_col}> 분포도", fontsize=16, pad=20)
                ax.set_xlabel(selected_col, fontsize=12)
                ax.set_ylabel("빈도수", fontsize=12)
                st.pyplot(fig)
        else:
            st.warning("분석할 수 있는 숫자형 데이터가 없습니다.")

    else:
        st.error(f"❌ '{file_path}' 파일을 찾을 수 없거나 인코딩이 맞지 않습니다.")

except Exception as e:
    st.error(f"❌ 예기치 못한 에러가 발생했습니다: {e}")