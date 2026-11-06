import streamlit as st
import requests
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re

@st.cache_resource
def load_kiwi():
    return Kiwi()

kiwi = load_kiwi()

def fetch_github_comments(repo_owner, repo_name, token=None):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/comments"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
        
    response = requests.get(url, headers=headers, params={"per_page": 100, "page": 1})
    if response.status_code == 200:
        return [item.get("body", "") for item in response.json()]
    else:
        st.error(f"데이터 요청 실패 (상태 코드: {response.status_code})")
        return []

def extract_nouns(comments):
    full_text = " ".join(comments)
    clean_text = re.sub(r'[^가-힣a-zA-Z\s]', '', full_text)
    tokens = kiwi.tokenize(clean_text)
    nouns = [token.form for token in tokens if token.tag.startswith('NN') and len(token.form) > 1]
    return " ".join(nouns)

st.title("🐙 GitHub 댓글 키워드 분석기")

col1, col2 = st.columns(2)
with col1:
    repo_owner = st.text_input("GitHub Owner", value="")
with col2:
    repo_name = st.text_input("Repository Name", value="")

github_token = st.sidebar.text_input("Personal Access Token (선택)", type="password")

if st.button("분석 시작"):
    if repo_owner and repo_name:
        with st.spinner("댓글 수집 중..."):
            comments = fetch_github_comments(repo_owner, repo_name, github_token)
            
        if comments:
            st.success(f"총 {len(comments)}개 수집 완료!")
            processed_text = extract_nouns(comments)
            
            if processed_text.strip():
                # Streamlit Cloud 배포 환경에 맞는 기본 폰트 설정
                wc = WordCloud(
                    background_color="white",
                    width=800,
                    height=400
                ).generate(processed_text)
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wc, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
