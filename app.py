import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
from matplotlib import font_manager, rc

# font_path = "./fonts/NanumGothic.ttf"
# font = font_manager.FontProperties(fname=font_path).get_name()
# rc('font', family=font)

font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

# plt.rc('font', family='NanumGothic')
# plt.rcParams['axes.unicode_minus'] = False

if __name__ == "__main__":
    # 데이터 로드
    df = pd.read_excel("./data/SR_ROW.xlsx", sheet_name="308명")
    
    # 연령 결측치가 있는 행 제거
    df = df.dropna(subset=['연령'])

    # WORK_ 컬럼 추출
    work_columns = [col for col in df.columns if "(WORK_" in col]

    # 연령대 컬럼 생성 (결측치 행이 제거되었으므로 모든 값이 유효함)
    df['연령대'] = df['연령'].apply(lambda x: f"{int(x//10*10)}대")

    # 연령대별 mean, std 계산
    grouped_stats = df.groupby('연령대')[work_columns].agg(['mean', 'std'])

    # 연령대별 본사/현업 비율 계산
    count_table_age = pd.crosstab(df['연령대'], df['본사/현업'])
    ratio_table = count_table_age.div(count_table_age.sum(axis=1), axis=0)

    # 전체 본사/현업 비율 계산
    count_table_total = df['본사/현업'].value_counts()

    # Streamlit 레이아웃
    st.title("WorkStyle 시각화")

    tab1, tab2 = st.tabs(["Work_Style별 그래프", "본사/현업 비율"])

    with tab1:
        st.header("Work_Style별 그래프")

        selected_work_col = st.selectbox("Work Style을 선택하세요:", options=work_columns)
        selected_ages = st.multiselect("연령대를 선택하세요:", options=df['연령대'].unique())

        if selected_work_col and selected_ages:
            fig_kde = plt.figure(figsize=(10, 6))
            for age_group in selected_ages:
                sns.kdeplot(data=df[df['연령대'] == age_group][selected_work_col], label=f"{age_group}")
            plt.title(f"{selected_work_col} 연령대별 분포(KDE)")
            plt.xlabel(selected_work_col)
            plt.ylabel("Density")
            plt.legend()
            st.pyplot(fig_kde)
        else:
            st.info("상단에서 WORK_ 컬럼과 연령대를 선택해주세요.")

    with tab2:
        st.header("연령대별 본사/현업 비율 및 전체 본사/현업 비율")
        
        ## 연령대별 본사/현업 비율 stacked bar
        fig, ax = plt.subplots(figsize=(10, 6))
        ratio_table.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title("연령대별 본사/현업 비율")
        ax.set_xlabel("연령대")
        ax.set_ylabel("비율")
        ax.legend(title="본사/현업", bbox_to_anchor=(1.05, 1), loc='upper left')
        st.pyplot(fig)

        ## 전체 본사/현업 비율 파이차트
        fig_pie = plt.figure(figsize=(4, 4))
        count_table_total.plot(kind='pie', autopct='%.1f%%', startangle=90)
        plt.title("전체 본사/현업 비율")
        plt.ylabel("")
        st.pyplot(fig_pie)