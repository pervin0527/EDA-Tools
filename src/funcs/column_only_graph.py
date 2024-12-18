import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt

def single_col_visualize(df, selected_column, selected_graph):
    """
    선택한 컬럼을 기반으로 시각화하는 함수
    """
    # 선택된 컬럼의 데이터가 실수형인지 확인
    if df[selected_column].dtype in ['float64', 'float32']:
        # 소수점 둘째 자리까지 반올림
        df[selected_column] = df[selected_column].round(2)

    # 고유값 추출 (반올림 후)
    unique_values = df[selected_column].unique()
    
    # 막대 그래프 선택
    if selected_graph == 'bar':
        fig = plt.figure(figsize=(12, 3))
        ax = plt.axes()
        
        # hue를 사용하고 legend 제외
        sns.countplot(data=df,
                     x=selected_column,
                     hue=selected_column,
                     legend=False)
        
        plt.xticks(rotation=90)
        plt.title(f"{selected_column} 값 분포")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        
    else:
        st.error("지원되지 않는 그래프 타입입니다.")
