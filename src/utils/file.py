import pandas as pd
import streamlit as st

def load_data(uploaded_file):
    """업로드된 파일을 pandas DataFrame으로 변환"""
    if uploaded_file is not None:
        try:
            extension = uploaded_file.name.split('/')[-1].split('.')[1]
            if extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif extension == "xlsx":
                df = pd.read_excel(uploaded_file)

            return df
        except Exception as e:
            st.error(f"파일 로드 중 오류 발생: {e}")
    return None