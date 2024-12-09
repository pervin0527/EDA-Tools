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

# Streamlit 레이아웃
st.title("WorkStyle 시각화")

tab1, tab2, tab3 = st.tabs(["Work_Style별 그래프", "본사/현업 비율", "연령대별 Work_Style 레이더 차트"])

with tab1:
    st.header("Work_Style별 그래프")

    selected_work_col = st.selectbox("Work Style을 선택하세요:", options=work_columns)
    
    # 모든 연령대를 기본 선택값으로 설정
    all_ages = df['연령대'].unique().tolist()
    selected_ages = st.multiselect("연령대를 선택하세요:", options=all_ages, default=all_ages)

    # 본사/현업 필터링 옵션 추가
    all_positions = df['본사/현업'].unique().tolist()
    selected_positions = st.multiselect("본사/현업을 선택하세요:", options=all_positions, default=all_positions)

    # 필터 적용
    filtered_df = df[df['연령대'].isin(selected_ages) & df['본사/현업'].isin(selected_positions)]

    if selected_work_col and len(filtered_df) > 0:
        # 연령대별 mean, std 재계산(필터 적용 후)
        if len(filtered_df['연령대'].unique()) > 0:
            filtered_grouped_stats = filtered_df.groupby('연령대')[selected_work_col].agg(['mean', 'std'])
        else:
            filtered_grouped_stats = pd.DataFrame()

        # KDE 플롯
        fig_kde = plt.figure(figsize=(10, 6))
        for age_group in filtered_df['연령대'].unique():
            age_group_data = filtered_df[filtered_df['연령대'] == age_group][selected_work_col]
            if len(age_group_data) > 0:
                sns.kdeplot(data=age_group_data, label=f"{age_group}")
        plt.title(f"{selected_work_col} 연령대별 분포(KDE)")
        plt.xlabel(selected_work_col)
        plt.ylabel("Density")
        plt.legend()
        st.pyplot(fig_kde)

        # 연령대별 Mean/STD 표 출력 (필터 후 데이터 기준)
        if not filtered_grouped_stats.empty:
            st.write("### 연령대별 Mean / STD (필터 적용)")
            st.table(filtered_grouped_stats)
        else:
            st.info("해당 조건에 맞는 데이터가 없습니다.")
    else:
        st.info("상단에서 WORK_ 컬럼과 연령대, 본사/현업을 선택해주세요.")


with tab2:
    st.header("연령대별 Work_Style 레이더 차트")

    # 레이더 차트에서 비교할 연령대 선택
    radar_selected_ages = st.multiselect("레이더 차트에서 비교할 연령대를 선택하세요:", options=all_ages, default=all_ages)

    if len(radar_selected_ages) > 0:
        categories = work_columns
        N = len(categories)

        angles = np.linspace(0, 2*np.pi, N, endpoint=False)

        fig_radar = plt.figure(figsize=(8,8))
        ax = plt.subplot(111, polar=True)

        for age in radar_selected_ages:
            # mean_values에서 해당 연령대 값 추출
            if age not in mean_values.index:
                continue
            values = mean_values.loc[age, :].values
            values = np.append(values, values[0])
            angle_for_plot = np.append(angles, angles[0])

            ax.plot(angle_for_plot, values, label=age)
            ax.fill(angle_for_plot, values, alpha=0.1)

        # 기본적인 라벨 설정
        ax.set_xticks(angles)
        ax.set_xticklabels(categories, fontsize=9)  # 폰트 사이즈 줄이기

        # 라벨 회전 및 패딩 조정
        # 각 라벨을 각도에 맞춰서 회전시켜 가독성 향상
        for label, angle in zip(ax.get_xticklabels(), angles):
            angle_deg = angle * 180/np.pi
            # 만약 텍스트가 뒤집히는 구간(180도 주변)에서 반전시켜 읽기 쉽게 함
            if angle_deg > 90 and angle_deg < 270:
                angle_deg = angle_deg + 180
                label.set_rotation(180)
            label.set_rotation(angle_deg)
            label.set_verticalalignment('center')
            label.set_horizontalalignment('center')

        # y축 라벨 제거(필요시 유지 가능)
        ax.set_yticklabels([])

        # 라벨과 중심 사이 거리 패딩 (tick_params 사용)
        ax.tick_params(axis='x', pad=15)

        plt.legend(bbox_to_anchor=(1.1, 1.1))
        plt.title("연령대별 Work_Style 평균 레이더 차트", y=1.1)
        st.pyplot(fig_radar)
    else:
        st.info("비교할 연령대를 하나 이상 선택해주세요.")

with tab3:
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