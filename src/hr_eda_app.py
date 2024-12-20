import copy
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

from utils.file import load_data
from utils.font import get_font_path
from funcs.column_only_graph import single_col_visualize
from funcs.column_filter_graph import col_filter_graph


font_path = get_font_path()
if font_path:
    try:
        font_manager.fontManager.addfont(font_path)
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=font_path).get_name()
        plt.rcParams['axes.unicode_minus'] = False
    except Exception as e:
        st.warning(f"폰트 설정 중 오류 발생: {str(e)}")


def main():
    st.set_page_config(page_title="EDA Dashboard", layout="wide")
    st.sidebar.title("Options")

    uploaded_file = st.sidebar.file_uploader("Upload File", type=['csv', 'xlsx'])
    df = load_data(uploaded_file)

    if df is not None:
        columns = df.columns.tolist()

        st.sidebar.subheader("Target Column Options")
        selected_column = st.sidebar.selectbox("Target Column", columns)
        selected_graph = st.sidebar.selectbox("Graph Type", ["bar"])

        st.sidebar.subheader("Filter Options")
        sub_columns = copy.deepcopy(columns)
        sub_columns.remove(selected_column)
        selected_filters = st.sidebar.multiselect("Filters", sub_columns)

        st.title("Dashbord")
        st.subheader("데이터 구성")
        st.write(df.head())

        st.subheader(f"[{selected_column}] EDA")
        col1, col2, col3 = st.columns([0.5, 0.5, 3])  # 1:2 비율로 분할

        with col1:
            st.markdown("##### 기본 통계")
            st.write(df[selected_column].describe())

        with col2:
            st.markdown("##### 고유값 분포")
            value_counts = df[selected_column].value_counts()
            st.write(value_counts)

        with col3:
            st.markdown("##### 그래프")
            single_col_visualize(df, selected_column, selected_graph)

        if selected_filters:          
            st.subheader(f"[{selected_column}] & {selected_filters} EDA")

            st.markdown("#### 평균, 표준편차 표")
            grouped_stats = df.groupby(selected_column)[selected_filters].agg(['mean', 'std']).reset_index()
            grouped_stats.columns = [f"{col[0]}_{col[1]}" if col[1] else col[0] for col in grouped_stats.columns]
            st.write(grouped_stats)

            st.markdown("#### 그래프")
            col_filter_graph(df, selected_column, selected_filters)


if __name__ == '__main__':
    main()