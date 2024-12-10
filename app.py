import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

from scipy.stats import norm
from collections import Counter
from matplotlib import font_manager, rc
from function import create_styled_bar_chart, create_styled_donut_chart, create_styled_heatmap, create_wordcloud, preprocess_text, CATEGORIES, QUESTIONS, analyze_categorical_responses, load_data

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

# 라벨 정제
categories = [c.split("(WORK_")[1].replace(")", "") for c in work_columns]

st.title("WorkStyle 시각화")

tab1, tab2, tab3, tab4 = st.tabs(["Work_Style별 그래프", "연령대별 Work_Style 레이더 차트", "test", "카테고리별 응답 분석"])

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

with tab4:
    df_sub = load_data()
    st.header('카테고리별 응답 분석')
    
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox('카테고리 선택', CATEGORIES)
    with col2:
        selected_question = st.selectbox('질문 선택', QUESTIONS)
    
    means, dist = analyze_categorical_responses(df_sub, selected_question, selected_category)
    
    if means is not None:
        if selected_question in QUESTIONS[-2:]:  # 다중 선택 문항
            st.subheader('다중 선택 항목 분석')
            fig3 = create_styled_heatmap(
                means,
                f'{selected_category}별 응답 분포'
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            st.subheader('상세 데이터')
            st.dataframe(means.round(2), use_container_width=True)
        
        else:  # 일반 점수 문항
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader('카테고리별 평균 점수')
                fig1 = create_styled_bar_chart(
                    means,
                    f'{selected_category}별 평균 점수',
                    selected_category,
                    '평균 점수'
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.subheader('카테고리별 응답 분포')
                fig2 = create_styled_donut_chart(
                    dist,
                    f'{selected_category}별 응답 분포'
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            st.subheader('상세 데이터')
            st.dataframe(dist.round(2), use_container_width=True)


with tab3:
    t3_df = pd.read_excel("./data/SR_질문_목록_데이터_병합결과.xlsx")
    question_cols = [
        '우리 조직은 정기적, 비정기적으로 경영진 및 상급자들과 원활한 소통이 이루어지고 있다.',
        '우리 조직은 직급과 관계없이 자유롭게 의견을 제시하고 토의할 수 있는 분위기이다.',
        '우리 조직의 리더들은 구성원들을 인정하고 격려하며 동기부여한다.',
        '우리 회사의 구성원들은 서로 상호간 믿음과 친밀도가 높은 편이다.',
        '우리 조직은 목표 달성에 필요한 적임자를 선정하고 승진시킨다.',
        '우리 조직의 리더들은 개인의 이해에 치우치지 않고 공정한 업무추진을 하고 있다.',
        '우리 회사의 경영진은 시장에서의 변화(기술변화, 경쟁사의 움직임)에 빠르게 반응하기 위해 많은 노력을 하고 있다.',
        '우리 회사는 변화와 혁신에 대한 공감대와 대응자세를 갖추고 있다.',
        '우리 회사 조직문화의 단점이라고 생각하는 것을 모두 선택해주세요.',
        '2024년 시행한 조직문화 프로그램 중 아는 것을 모두 선택해주세요.'
    ]

    # 점수 칼럼들을 숫자로 변환 (예: "5점" -> 5)
    for col in question_cols:
        t3_df[col] = t3_df[col].str.replace('점', '', regex=False).astype(float)

    st.title("조직문화 설문 시각화")

    # 카테고리 선택: "전체", "연령대별", "본사/현업별"
    category = st.selectbox("카테고리 선택", ["전체", "연령대별", "본사/현업별"])

    # "전체" 평균 점수
    overall_mean = t3_df[question_cols].mean()

    if category == "전체":
        st.subheader("전체 평균 점수")
        # 전체 평균 막대 그래프
        st.bar_chart(overall_mean)

    elif category == "연령대별":
        st.subheader("연령대별 평균 점수")
        # 연령대별 평균 구하기
        # 가령 '연령' 컬럼이 '30대', '40대' 등으로 표기되어 있다고 가정
        age_group_mean = t3_df.groupby('연령')[question_cols].mean().T
        # T로 전치하여 질문을 인덱스로, 연령대를 컬럼으로 하여 그래프화
        st.dataframe(age_group_mean)
        
        # 특정 연령대를 선택해볼 수 있도록 selectbox 추가
        selected_age = st.selectbox("연령대 선택", ["전체"] + list(age_group_mean.columns))
        if selected_age == "전체":
            # 전체 연령대별 평균(각 연령대 막대그래프를 그룹으로 표시)
            st.line_chart(age_group_mean)
        else:
            # 개별 연령대 선택 시 해당 연령대 점수만 시각화
            st.bar_chart(age_group_mean[selected_age])

    elif category == "본사/현업별":
        st.subheader("본사/현업별 평균 점수")
        # 가령 '본사/현업' 컬럼이 '본사', '현업' 으로 표시되어 있다고 가정
        hq_ops_mean = t3_df.groupby('본사/현업')[question_cols].mean().T
        st.dataframe(hq_ops_mean)

        # 본사/현업 선택
        selected_site = st.selectbox("본사/현업 선택", ["전체"] + list(hq_ops_mean.columns))
        if selected_site == "전체":
            st.line_chart(hq_ops_mean)
        else:
            st.bar_chart(hq_ops_mean[selected_site])