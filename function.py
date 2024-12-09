import streamlit as st
import pandas as pd
from wordcloud import WordCloud
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

# 카테고리와 질문 리스트 정의
CATEGORIES = [
    '인사하위영역', '본사/현업', '사원하위그룹', 
    '정규직/비정규직', '권한', '연령', '성별', 
    '직위', '직급'
]

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
    # 엑셀 파일 로드
    df = pd.read_excel('SR_질문_목록_데이터_병합결과.xlsx')
    
    # 점수 컬럼 전처리 함수
    def clean_score(text):
        if isinstance(text, str):
            # '점' 문자로 분리하고 첫 번째 숫자만 추출
            score = text.split('점')[0]
            try:
                return int(score)
            except ValueError:
                return None
        return text
    
    # 객관식 문항 컬럼 리스트
    score_columns = [q for q in QUESTIONS if q not in QUESTIONS[-2:]]
    
    # 각 점수 컬럼에 대해 전처리 적용
    for col in score_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_score)
    
    return df

def preprocess_text(text):
    if not isinstance(text, str):
        return ''
    # 특수문자 제거 및 공백 처리
    text = re.sub(r'[^\w\s가-힣]', '', text)
    return text.strip()

def create_wordcloud(text_data):
    try:
        font_path = "C:/Windows/Fonts/malgun.ttf"
        
        # 텍스트 전처리
        processed_words = [preprocess_text(word) for word in text_data]
        processed_words = [word for word in processed_words if word]
        
        if not processed_words:
            st.warning("처리할 텍스트 데이터가 없습니다.")
            return None
        
        # 단어 빈도수 계산
        word_counts = Counter(processed_words)
        
        # 워드클라우드 객체 생성
        wordcloud = WordCloud(
            font_path=font_path,
            width=800,
            height=400,
            background_color='white',
            prefer_horizontal=1.0,
            min_font_size=10,
            max_font_size=100,
            random_state=42,
            repeat=False,
            min_word_length=2
        )
        
        # 워드클라우드 생성
        wordcloud.generate_from_frequencies(dict(word_counts))
        
        return wordcloud
        
    except Exception as e:
        st.error(f"워드클라우드 생성 중 오류 발생: {str(e)}")
        return None
    
def create_styled_bar_chart(data, title, x_label, y_label, color_sequence=None):
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
        showlegend=False,  # 범례 제거
        margin=dict(t=100, l=50, r=50, b=50),
        height=500  # 그래프 높이 지정
    )
    
    fig.update_traces(
        marker=dict(
            line=dict(width=1, color='rgba(0,0,0,0.3)')
        ),
        opacity=0.85
    )
    
    fig.update_xaxes(
        title=None,  # x축 제목 제거
        tickangle=45,
        tickfont=dict(size=12, color="#2F4F4F")
    )
    
    fig.update_yaxes(
        title=y_label,
        tickfont=dict(size=12, color="#2F4F4F")
    )
    
    return fig

def create_styled_donut_chart(data, title):
    # 데이터 평균 계산
    data_mean = data.mean()
    
    fig = px.pie(
        values=data_mean,
        names=data_mean.index,
        title=title,
        hole=0.6,  # 도넛 차트로 만들기
        template='plotly_white',
        color_discrete_sequence=px.colors.qualitative.Set2
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
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color="#2F4F4F")
        ),
        margin=dict(t=100, l=50, r=50, b=100),
        height=500  # 그래프 높이 지정
    )
    
    # 가운데 텍스트 추가
    fig.add_annotation(
        text='응답<br>분포',
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=20, color="#2F4F4F")
    )
    
    return fig

def create_styled_heatmap(data, title):
    # 데이터를 2D 형태로 변환
    if isinstance(data, pd.Series):
        data = data.unstack()  # Series를 DataFrame으로 변환
    
    fig = px.imshow(
        data,
        title=title,
        color_continuous_scale='RdBu_r',
        aspect='auto',
        labels=dict(color="응답률 (%)")
    )
    
    fig.update_layout(
        title={
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, family="Malgun Gothic", color="#2F4F4F")
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=100, l=50, r=50, b=50),
        height=500
    )
    
    # x축과 y축 레이블 스타일링
    fig.update_xaxes(
        title=None,
        tickangle=45,
        tickfont=dict(size=10, color="#2F4F4F")
    )
    
    fig.update_yaxes(
        title=None,
        tickfont=dict(size=10, color="#2F4F4F")
    )
    
    return fig

def analyze_categorical_responses(df, question_col, category_col):
    try:
        # 결측치 제거
        df_clean = df[[category_col, question_col]].dropna()
        
        # 다중 선택 문항인 경우
        if question_col in ['우리 회사 조직문화의 단점이라고 생각하는 것을 모두 선택해주세요.',
                          '2024년 시행한 조직문화 프로그램 중 아는 것을 모두 선택해주세요.']:
            choices = CULTURE_PROBLEMS if '단점' in question_col else CULTURE_PROGRAMS
            
            # 각 카테고리별로 선택지의 응답 비율을 계산
            result_data = []
            for category in df_clean[category_col].unique():
                category_data = df_clean[df_clean[category_col] == category]
                choice_percentages = analyze_multiple_choice(category_data, question_col, choices)
                result_data.append(choice_percentages)
            
            # 결과를 DataFrame으로 변환
            result_df = pd.DataFrame(result_data, index=df_clean[category_col].unique())
            return result_df, None
        
        # 일반 점수 문항인 경우
        else:
            # 카테고리별 평균 점수 계산
            category_means = df_clean.groupby(category_col)[question_col].mean().round(2)
            
            # 카테고리별 응답 분포 계산
            response_dist = df_clean.groupby([category_col, question_col]).size().unstack(fill_value=0)
            response_dist_pct = response_dist.div(response_dist.sum(axis=1), axis=0) * 100
            
            return category_means, response_dist_pct
        
    except Exception as e:
        st.error(f"응답 분석 중 오류 발생: {str(e)}")
        return None, None

def analyze_multiple_choice(df, column, choices):
    total_responses = len(df)
    choice_counts = {choice: 0 for choice in choices}
    
    for response in df[column].dropna():
        if isinstance(response, str):
            for choice in choices:
                if choice in response:
                    choice_counts[choice] += 1
    
    choice_percentages = {k: (v/total_responses)*100 for k, v in choice_counts.items()}
    return pd.Series(choice_percentages)