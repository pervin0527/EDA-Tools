import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt


def col_filter_graph(df, selected_column, selected_filters):
    """
    주어진 데이터프레임에서 선택된 컬럼(selected_column)과 필터(selected_filters)를 기반으로
    서브플롯에 각각의 필터를 KDE 그래프로 시각화합니다.

    Parameters:
    df (pd.DataFrame): 데이터프레임
    selected_column (str): 그룹화에 사용할 컬럼
    selected_filters (list): 분석할 필터(숫자형 컬럼)의 리스트
    """
    if not selected_filters:
        st.warning("필터를 하나 이상 선택해야 합니다.")
        return

    # 서브플롯 행과 열 계산
    num_filters = len(selected_filters)
    rows = (num_filters + 2) // 3  # 한 행에 최대 3개의 서브플롯 배치
    cols = min(3, num_filters)

    # 큰 플롯 생성
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    axes = axes.flatten()  # axes를 1차원 리스트로 변환하여 인덱싱 가능하게 함

    # 각 필터에 대해 서브플롯 생성
    for idx, filter_name in enumerate(selected_filters):
        ax = axes[idx]  # 현재 서브플롯 선택
        for value in df[selected_column].unique():
            filtered_data = df[df[selected_column] == value][filter_name]
            sns.kdeplot(filtered_data, ax=ax, label=f"{value}", fill=True, alpha=0.3)

        # 서브플롯 설정
        ax.set_title(f"{selected_column}별 {filter_name}")
        ax.set_xlabel(filter_name)
        ax.set_ylabel("Density")
        ax.legend(title=selected_column)

    # 남은 빈 서브플롯 제거
    for idx in range(len(selected_filters), len(axes)):
        fig.delaxes(axes[idx])

    # 레이아웃 조정 및 Streamlit에 그래프 출력
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
