import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter
import re

# 상수 정의
CULTURE_PROGRAMS = [
    'CEO의 릴레이 소통 활동',
    '최고관리자 특강',
    '신입사원 입사 CEO 특강',
    '리버스멘토링(Reverse Mentoring)',
    '소통,공감 워크숍',
    '체육행사',
    '가정기념일 축하 \'사랑한데이\'',
    '출산선물',
    '노사 공동 혁신위원회',
    '노사관계 인식 설문조사',
    '직무가치기반 임금체계 설명회',
    '찾아가는 인사소통회',
    '여성 경력개발 코칭 프로그램',
    '조직문화 활성화 교육',
    '저출생 극복 추진위원회',
    '육아기 지원제도 개선'
]

CULTURE_PROBLEMS = [
    '불공정/차별 (철피아, 철수저, 차별대우 등)',
    '수직적/권위적 (상명하복, 군대문화, 권위주의, 경직성 등)',
    '소통부재 (의사소통 불통, 불통 조직, 소통부재 등)',
    '개인주의 (이기적, 각자도생 등)',
    '갈등관계 (직렬갈등, 끼리끼리, 직종별 단합, 소속간 갈등 등)',
    '승진적체 (승진차별, 현장승진 어려움, 진급체계 문제 등)',
    '본사위주 (본사중심, 현장무시, 본사와 현업 분리 등)'
]

CATEGORIES = ['전체', '인사하위영역', '본사/현업', '사원하위그룹', 
    '정규직/비정규직', '권한', '연령', '성별', 
    '직위', '직급']

QUESTIONS = [
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

def load_data():
    df = pd.read_excel('./data/SR_질문_목록_데이터_병합결과.xlsx')
    
    def clean_score(text):
        if isinstance(text, str):
            score = text.split('점')[0]
            try:
                return int(score)
            except ValueError:
                return None
        return text
    
    score_columns = [q for q in QUESTIONS if q not in QUESTIONS[-2:]]
    
    for col in score_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_score)
    
    return df

def create_styled_bar_chart(data, title, x_label, y_label, color_sequence=None):
    # 데이터프레임을 일반 시리즈로 변환
    if isinstance(data.index, pd.MultiIndex):
        data = data.reset_index(level=1, drop=True)
    
    fig = px.bar(
        data,
        title=title,
        labels={'value': y_label, 'index': x_label},
        color_discrete_sequence=color_sequence or px.colors.sequential.Viridis,
        template='plotly_white'
    )
    
    fig.update_layout(
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, family="Malgun Gothic", color="#2F4F4F")
        },
        plot_bgcolor='rgba(240,240,240,0.2)',
        paper_bgcolor='white',
        showlegend=False,
        margin=dict(t=100, l=50, r=50, b=50),
        height=500
    )
    
    fig.update_traces(
        marker=dict(line=dict(width=1, color='rgba(0,0,0,0.3)')),
        opacity=0.85
    )
    
    fig.update_xaxes(
        title=None,
        tickangle=45,
        tickfont=dict(size=12, color="#2F4F4F")
    )
    
    fig.update_yaxes(
        title=y_label,
        tickfont=dict(size=12, color="#2F4F4F")
    )
    
    return fig

def analyze_categorical_responses(df, category):
    try:
        # 다중선택 문항 제외한 질문들만 선택
        score_questions = [q for q in QUESTIONS if q not in QUESTIONS[-2:]]
        
        def calculate_stats_by_category(data, questions):
            result = {}
            for question in questions:
                question_data = data[question].dropna()
                result[question] = {
                    '평균': round(question_data.mean(), 2) if not question_data.empty else 0.0,
                    '표준편차': round(question_data.std(), 2) if len(question_data) > 1 else 0.0
                }
            return result
        
        # 카테고리가 '전체'인 경우와 아닌 경우 분리
        if category == '전체':
            # 전체 통계만 계산
            stats_data = {'전체': calculate_stats_by_category(df, score_questions)}
            index = ['전체']
        else:
            # 전체 통계 계산
            stats_data = {'전체': calculate_stats_by_category(df, score_questions)}
            
            # 카테고리별 통계 계산 (None 값 제외)
            for cat in df[category].unique():
                if pd.notna(cat):  # None 값 제외
                    cat_data = df[df[category] == cat]
                    stats_data[cat] = calculate_stats_by_category(cat_data, score_questions)
            
            index = ['전체'] + [cat for cat in df[category].unique() if pd.notna(cat)]
        
        # 데이터프레임 생성을 위한 데이터 준비
        result_data = []
        
        for idx in index:
            row_data = []
            stats = stats_data[idx]
            
            for question in score_questions:
                row_data.extend([
                    stats[question]['평균'],
                    stats[question]['표준편차']
                ])
            
            result_data.append(row_data)
        
        # 멀티인덱스 컬럼 생성
        metric_columns = ['평균', '표준편차']
        column_tuples = [(f'{i+1}번', metric) for i, _ in enumerate(score_questions) for metric in metric_columns]
        columns = pd.MultiIndex.from_tuples(column_tuples)
        
        # 데이터프레임 생성
        stats = pd.DataFrame(result_data, index=index, columns=columns)
        return stats

    except Exception as e:
        st.error(f"응답 분석 중 오류 발생: {str(e)}")
        return None
    
def main():
    st.set_page_config(layout="wide")
    
    st.title('SR 조직문화 설문조사 분석 대시보드')
    
    try:
        df = load_data()
        
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


if __name__ == '__main__':
    main()