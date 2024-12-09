import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
from matplotlib import font_manager, rc

# 로컬 또는 서버 환경에서 폰트 경로 설정
try:
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # 서버 환경
except FileNotFoundError:
    font_path = "./fonts/NanumGothic.ttf"

font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams['axes.unicode_minus'] = False


# 데이터 로드
df = pd.read_excel("./data/SR_ROW.xlsx", sheet_name="308명")

# 연령 결측치가 있는 행 제거
df = df.dropna(subset=['연령'])

# WORK_ 컬럼 추출
work_columns = [col for col in df.columns if "(WORK_" in col]

# 연령대 컬럼 생성
df['연령대'] = df['연령'].apply(lambda x: f"{int(x//10*10)}대")

# 연령대별 mean, std 계산
grouped_stats = df.groupby('연령대')[work_columns].agg(['mean', 'std'])

# 연령대별 본사/현업 비율 계산
count_table_age = pd.crosstab(df['연령대'], df['본사/현업'])
ratio_table = count_table_age.div(count_table_age.sum(axis=1), axis=0)

# 전체 본사/현업 비율 계산
count_table_total = df['본사/현업'].value_counts()

# mean 값만 추출 (Radar Chart용)
mean_values = grouped_stats.xs('mean', level=1, axis=1)  # (연령대 x work_style) 형태

# Streamlit 레이아웃
st.title("WorkStyle 시각화")

tab1, tab2, tab3 = st.tabs(["Work_Style별 그래프", "본사/현업 비율", "연령대별 Work_Style 레이더 차트"])

with tab1:
    st.header("Work_Style별 그래프")

    selected_work_col = st.selectbox("Work Style을 선택하세요:", options=work_columns)
    
    # 모든 연령대를 기본 선택값으로 설정
    all_ages = df['연령대'].unique().tolist()
    selected_ages = st.multiselect("연령대를 선택하세요:", options=all_ages, default=all_ages)
    
    if selected_work_col and selected_ages:
        fig_kde = plt.figure(figsize=(10, 6))
        for age_group in selected_ages:
            sns.kdeplot(data=df[df['연령대'] == age_group][selected_work_col], label=f"{age_group}")
        plt.title(f"{selected_work_col} 연령대별 분포(KDE)")
        plt.xlabel(selected_work_col)
        plt.ylabel("Density")
        plt.legend()
        st.pyplot(fig_kde)

        # 선택한 work style에 대한 연령대별 mean/std 표 출력
        stats_for_selection = grouped_stats[selected_work_col].loc[selected_ages, :]
        st.write("### 연령대별 Mean / STD")
        st.table(stats_for_selection)

    else:
        st.info("상단에서 WORK_ 컬럼과 연령대를 선택해주세요.")

with tab2:
    st.header("연령대별 본사/현업 비율 및 전체 본사/현업 비율")
    
    # 연령대별 본사/현업 비율 stacked bar
    fig, ax = plt.subplots(figsize=(10, 6))
    ratio_table.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title("연령대별 본사/현업 비율")
    ax.set_xlabel("연령대")
    ax.set_ylabel("비율")
    ax.legend(title="본사/현업", bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig)

    # 전체 본사/현업 비율 파이차트
    fig_pie = plt.figure(figsize=(4, 4))
    count_table_total.plot(kind='pie', autopct='%.1f%%', startangle=90)
    plt.title("전체 본사/현업 비율")
    plt.ylabel("")
    st.pyplot(fig_pie)


with tab3:
    st.header("연령대별 Work_Style 레이더 차트")

    # 레이더 차트를 위해 연령대 선택 (기본적으로 모두 선택)
    radar_selected_ages = st.multiselect("레이더 차트에서 비교할 연령대를 선택하세요:", options=all_ages, default=all_ages)

    if len(radar_selected_ages) > 0:
        # 레이더 차트용 데이터 준비
        categories = work_columns
        N = len(categories)

        # 각 카테고리에 대응하는 각도 계산
        angles = np.linspace(0, 2*np.pi, N, endpoint=False)

        fig_radar = plt.figure(figsize=(8,8))
        ax = plt.subplot(111, polar=True)

        # 레이더 차트 그리기
        for age in radar_selected_ages:
            values = mean_values.loc[age, :].values
            # 시작점과 끝점 연결 위해 첫 값 다시 append
            values = np.append(values, values[0])
            angle_for_plot = np.append(angles, angles[0])

            ax.plot(angle_for_plot, values, label=age)
            ax.fill(angle_for_plot, values, alpha=0.1)

        ax.set_xticks(angles)
        ax.set_xticklabels(categories, fontsize=10)

        # y축 라벨 제거(필요시 조정)
        ax.set_yticklabels([])

        # 범례
        plt.legend(bbox_to_anchor=(1.1, 1.1))
        plt.title("연령대별 Work_Style 평균 레이더 차트", y=1.1)
        st.pyplot(fig_radar)
    else:
        st.info("비교할 연령대를 하나 이상 선택해주세요.")
