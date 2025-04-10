import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
import requests
import tempfile
import os

# Streamlit 페이지 설정
st.title("🔍 LangChain SQL Query Demo")
st.write("자연어로 질문하여 데이터베이스를 조회하세요.")

# OpenAI API 키 설정
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# 질문 입력
query = st.text_input("데이터베이스에 대해 질문해 보세요.", placeholder="예: 금융회사별 수익률이 가장 높은 상품은 무엇인가요?")

# 캐시된 임시 DB 생성 함수
@st.cache_resource
def get_local_db_path():
    DB_URL = "https://raw.githubusercontent.com/pjm9889/buhome/main/db/fin_db.db"
    response = requests.get(DB_URL)
    response.raise_for_status()

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    tmp_file.write(response.content)
    tmp_file.close()
    return tmp_file.name

# 실행
if openai_api_key and query:
    with st.spinner('DB 다운로드 중...'):
        local_db_path = get_local_db_path()
        db_uri = f"sqlite:///{local_db_path}"

    # LangChain용 SQL DB 객체 생성
    db = SQLDatabase.from_uri(db_uri)

    # OpenAI LLM 설정
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-3.5-turbo", temperature=0)

    # LangChain SQL 체인 생성
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=False)

    # 질의 실행
    with st.spinner('질의 처리 중...'):
        result = db_chain.run(query)

    # 결과 출력
    st.subheader("📌 결과")
    st.write(result)
