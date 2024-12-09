import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import norm
from matplotlib import font_manager, rc

# 폰트 설정
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

# 전체 데이터 기반 mean, std 계산(기본용)
grouped_stats = df.groupby('연령대')[work_columns].agg(['mean', 'std'])

# mean 값(기본)
mean_values = grouped_stats.xs('mean', level=1, axis=1)

# 연령대별 본사/현업 비율 계산
count_table_age = pd.crosstab(df['연령대'], df['본사/현업'])
ratio_table = count_table_age.div(count_table_age.sum(axis=1), axis=0)

# 전체 본사/현업 비율 계산
count_table_total = df['본사/현업'].value_counts()

# 라벨 정제: "ABC(WORK_XXX)" 형태에서 "WORK_XXX"만 추출
# 예: "SOMETHING (WORK_PROCESS)" -> "PROCESS"
# split("(WORK_")[1].replace(")", "") 로 WORK_ 이후 부분만 추출
categories = [c.split("(WORK_")[1].replace(")", "") for c in work_columns]

st.title("WorkStyle 시각화")

# tab1, tab2, tab3 = st.tabs(["Work_Style별 그래프", "연령대별 Work_Style 레이더 차트", "본사/현업 비율"])
tab1, tab2 = st.tabs(["Work_Style별 그래프", "연령대별 Work_Style 레이더 차트"])

with tab1:
    st.header("Work_Style별 그래프")

    selected_work_col = st.selectbox("Work Style을 선택하세요:", options=work_columns)
    
    # 모든 연령대를 기본 선택값으로 설정
    all_ages = df['연령대'].unique().tolist()
    selected_ages = st.multiselect("연령대를 선택하세요:", options=all_ages, default=all_ages)

    # 본사/현업 필터링 옵션
    all_positions = df['본사/현업'].unique().tolist()
    selected_positions = st.multiselect("본사/현업을 선택하세요:", options=all_positions, default=all_positions)

    # 필터 적용
    filtered_df = df[df['연령대'].isin(selected_ages) & df['본사/현업'].isin(selected_positions)]

    if selected_work_col and len(filtered_df) > 0:
        # 필터된 데이터에 대한 mean/std 재계산
        if len(filtered_df['연령대'].unique()) > 0:
            filtered_grouped_stats = filtered_df.groupby('연령대')[selected_work_col].agg(['mean', 'std'])
        else:
            filtered_grouped_stats = pd.DataFrame()

        # KDE 플롯
        fig_kde = plt.figure(figsize=(10, 6))
        unique_ages_in_filtered = filtered_df['연령대'].unique()
        for age_group in unique_ages_in_filtered:
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

    # 레이더 차트에서도 본사/현업 필터 추가
    # key 파라미터를 추가하여 중복 ID 에러 방지
    radar_selected_ages = st.multiselect(
        "레이더 차트에서 비교할 연령대를 선택하세요:", 
        options=df['연령대'].unique(), 
        default=df['연령대'].unique(),
        key="radar_ages"
    )
    radar_selected_positions = st.multiselect(
        "본사/현업을 선택하세요:", 
        options=df['본사/현업'].unique().tolist(), 
        default=df['본사/현업'].unique().tolist(),
        key="radar_positions"
    )

    # 레이더 차트용 필터 적용
    radar_filtered_df = df[df['연령대'].isin(radar_selected_ages) & df['본사/현업'].isin(radar_selected_positions)]

    if len(radar_filtered_df) > 0 and len(radar_selected_ages) > 0:
        # 필터링된 데이터로 mean 재계산
        radar_grouped_stats = radar_filtered_df.groupby('연령대')[work_columns].mean()

        # 레이더 차트 그리기
        N = len(categories)
        angles = np.linspace(0, 2*np.pi, N, endpoint=False)

        fig_radar = plt.figure(figsize=(8,8))
        ax = plt.subplot(111, polar=True)

        for age in radar_selected_ages:
            if age in radar_grouped_stats.index:
                values = radar_grouped_stats.loc[age, :].values
                values = np.append(values, values[0])
                angle_for_plot = np.append(angles, angles[0])

                ax.plot(angle_for_plot, values, label=age)
                ax.fill(angle_for_plot, values, alpha=0.1)

        # 축 라벨 설정: 정제된 categories 사용
        ax.set_xticks(angles)
        ax.set_xticklabels(categories, fontsize=9)

        # 라벨 회전 및 패딩
        for label, angle in zip(ax.get_xticklabels(), angles):
            angle_deg = angle * 180/np.pi
            if angle_deg > 90 and angle_deg < 270:
                angle_deg = angle_deg + 180
                label.set_rotation(180)
            label.set_rotation(angle_deg)
            label.set_verticalalignment('center')
            label.set_horizontalalignment('center')

        ax.set_yticklabels([])
        ax.tick_params(axis='x', pad=15)

        plt.legend(bbox_to_anchor=(1.1, 1.1))
        plt.title("연령대별 Work_Style 평균 레이더 차트 (필터 적용)", y=1.1)
        st.pyplot(fig_radar)
    else:
        st.info("비교할 연령대 및 본사/현업을 하나 이상 선택하고 해당하는 데이터가 있어야 합니다.")


# with tab3:
#     st.header("연령대별 본사/현업 비율 및 전체 본사/현업 비율")
    
#     # 연령대별 본사/현업 비율 stacked bar
#     fig, ax = plt.subplots(figsize=(10, 6))
#     ratio_table.plot(kind='bar', stacked=True, ax=ax)
#     ax.set_title("연령대별 본사/현업 비율")
#     ax.set_xlabel("연령대")
#     ax.set_ylabel("비율")
#     ax.legend(title="본사/현업", bbox_to_anchor=(1.05, 1), loc='upper left')
#     st.pyplot(fig)

#     # 전체 본사/현업 비율 파이차트
#     fig_pie = plt.figure(figsize=(4, 4))
#     count_table_total.plot(kind='pie', autopct='%.1f%%', startangle=90)
#     plt.title("전체 본사/현업 비율")
#     plt.ylabel("")
#     st.pyplot(fig_pie)
