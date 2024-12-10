import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

from scipy.stats import norm
from collections import Counter
from matplotlib import font_manager, rc
from function import create_styled_bar_chart, CATEGORIES, QUESTIONS, analyze_categorical_responses, load_data

## 폰트 설정
try:
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # 서버 환경
except FileNotFoundError:
    font_path = "./fonts/NanumGothic.ttf"

font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = font_manager.FontProperties(fname=font_path).get_name()
plt.rcParams['axes.unicode_minus'] = False

## 데이터 로드
df = pd.read_excel("./data/SR_ROW.xlsx", sheet_name="308명")
df = df.dropna(subset=['연령']) # 결측치 제거

work_columns = [col for col in df.columns if "(WORK_" in col] # WORK_ 컬럼 추출
df['연령대'] = df['연령'].apply(lambda x: f"{int(x//10*10)}대") # 연령대 컬럼 생성

# 전체 데이터 기반 mean, std 계산(기본용)
grouped_stats = df.groupby('연령대')[work_columns].agg(['mean', 'std'])

# mean 값(기본)
mean_values = grouped_stats.xs('mean', level=1, axis=1)

# 연령대별 본사/현업 비율 계산
count_table_age = pd.crosstab(df['연령대'], df['본사/현업'])
ratio_table = count_table_age.div(count_table_age.sum(axis=1), axis=0)

# 전체 본사/현업 비율 계산
count_table_total = df['본사/현업'].value_counts()

# 라벨 정제
categories = [c.split("(WORK_")[1].replace(")", "") for c in work_columns]

st.title("WorkStyle 시각화")
tab1, tab2, tab3 = st.tabs(["Work_Style별 그래프", "연령대별 Work_Style 레이더 차트", "카테고리별 응답 분석"])

# 근속년수 필터를 위해 mapping 정의
tenure_options = {
    "1년 미만": 1,
    "3년 미만": 3,
    "5년 미만": 5,
    "10년 미만": 10,
    "15년 미만": 15,
    "20년 미만": 20
}

with tab1:
    st.header("Work_Style별 그래프")

    selected_work_col = st.selectbox("Work Style을 선택하세요:", options=work_columns)
    
    # 연령대 필터
    all_ages = df['연령대'].unique().tolist()
    selected_ages = st.multiselect("연령대를 선택하세요:", options=all_ages, default=all_ages)

    # 본사/현업 필터
    all_positions = df['본사/현업'].unique().tolist()
    selected_positions = st.multiselect("본사/현업을 선택하세요:", options=all_positions, default=all_positions)

    # 근속년수 필터
    selected_tenure_label = st.selectbox("근속년수 기준을 선택하세요:", options=list(tenure_options.keys()))
    selected_tenure = tenure_options[selected_tenure_label]

    # 필터 적용
    filtered_df = df[
        df['연령대'].isin(selected_ages) &
        df['본사/현업'].isin(selected_positions) &
        (df['근속년수'] < selected_tenure)
    ]

    if selected_work_col and len(filtered_df) > 0:
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
        st.info("상단에서 WORK_ 컬럼, 연령대, 본사/현업, 근속년수 필터를 선택해주세요.")

# 한글 라벨만 추출: '(' 문자 앞부분을 추출
# 예: "업무프로세스(WORK_PROCESS)" -> "업무프로세스"
categories_kor = [c.split("(")[0].strip() for c in work_columns]

with tab2:
    st.header("연령대별 Work_Style 레이더 차트")

    # 레이더 차트 필터
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

    # 근속년수 필터 (레이더 차트용)
    radar_selected_tenure_label = st.selectbox("근속년수 기준을 선택하세요:(레이더)", options=list(tenure_options.keys()), key="radar_tenure")
    radar_selected_tenure = tenure_options[radar_selected_tenure_label]

    # 레이더 차트용 필터 적용
    radar_filtered_df = df[
        df['연령대'].isin(radar_selected_ages) &
        df['본사/현업'].isin(radar_selected_positions) &
        (df['근속년수'] < radar_selected_tenure)
    ]

    if len(radar_filtered_df) > 0 and len(radar_selected_ages) > 0:
        # 필터링된 데이터로 mean 재계산
        radar_grouped_stats = radar_filtered_df.groupby('연령대')[work_columns].mean()

        # 레이더 차트 그리기
        N = len(categories_kor)
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

        # 축 라벨 설정: 정제된 한글 categories_kor 사용
        ax.set_xticks(angles)
        ax.set_xticklabels(categories_kor, fontsize=9)

        # 라벨 회전 및 패딩
        for label, angle in zip(ax.get_xticklabels(), angles):
            angle_deg = angle * 180/np.pi
            if 90 < angle_deg < 270:
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
        st.info("비교할 연령대, 본사/현업, 근속년수 기준을 선택하고 해당하는 데이터가 있어야 합니다.")

with tab3:
    # 메인 화면에 선택 옵션 배치
    st.title('SR 조직문화 설문조사 분석 대시보드')
    
    try:
        # df = load_data()
        df = pd.read_excel("./data/SR_질문_목록_데이터_병합결과.xlsx")
        
        selected_category = st.selectbox(
            '카테고리 선택',
            CATEGORIES,
            index=0
        )
        
        stats = analyze_categorical_responses(df, selected_category)
        
        if stats is not None:
            st.subheader(f'{selected_category} 분석 결과')
            st.dataframe(stats.style.format("{:.2f}"), use_container_width=True)
            
            if len(stats) > 1:
                # 평균 컬럼만 선택하여 시각화
                avg_cols = [col for col in stats.columns if col[1] == '평균']
                avg_data = stats[avg_cols].mean(axis=1)  # 각 카테고리의 평균값 계산
                

    except Exception as e:
        st.error(f'데이터 분석 중 오류 발생: {str(e)}')