import streamlit as st
import anthropic

# 페이지 설정
st.set_page_config(
    page_title="회의록 정리 AI Agent",
    page_icon="📋",
    layout="wide"
)

# 스타일
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a1a2e;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f8f9fa;
        border-left: 4px solid #4A90E2;
        padding: 1.5rem;
        border-radius: 8px;
        margin-top: 1rem;
    }
    .stTextArea textarea {
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<div class="main-title">📋 회의록 정리 AI Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">회의 내용을 붙여넣으면 자동으로 요약 · 액션아이템 · 핵심 결정사항을 정리해드립니다</div>', unsafe_allow_html=True)

# 사이드바 - API 키 입력
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    
    st.markdown("---")
    st.markdown("**회의 유형 선택**")
    meeting_type = st.selectbox(
        "회의 유형",
        ["일반 회의", "주간 팀 회의", "프로젝트 킥오프", "의사결정 회의", "브레인스토밍"]
    )
    
    st.markdown("---")
    st.markdown("**출력 언어**")
    language = st.radio("언어", ["한국어", "English"])
    
    st.markdown("---")
    st.markdown("**추가 옵션**")
    include_email = st.checkbox("이메일 초안 생성", value=False)
    include_followup = st.checkbox("다음 회의 안건 포함", value=True)

# 메인 영역
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📝 회의 내용 입력")
    meeting_text = st.text_area(
        "회의 내용을 여기에 붙여넣으세요",
        height=400,
        placeholder="""예시)
참석자: 김철수(PM), 이영희(개발), 박민준(디자인)
일시: 2025년 6월 30일 오후 2시

김철수: 이번 스프린트 목표는 로그인 기능 완성입니다.
이영희: 개발은 7월 5일까지 완료 가능합니다.
박민준: 디자인은 내일까지 시안 공유하겠습니다.
김철수: 다음 주 월요일에 중간 점검 회의 잡겠습니다.
        """
    )
    
    summarize_btn = st.button("🚀 회의록 정리하기", type="primary", use_container_width=True)

with col2:
    st.subheader("✨ 정리 결과")
    
    if summarize_btn:
        if not api_key:
            st.error("❌ 사이드바에 Anthropic API Key를 입력해주세요!")
        elif not meeting_text.strip():
            st.error("❌ 회의 내용을 입력해주세요!")
        else:
            with st.spinner("AI가 회의록을 분석중입니다..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    
                    email_instruction = """
## 📧 후속 이메일 초안
회의 결과를 참석자들에게 공유할 이메일 초안을 작성해주세요.
""" if include_email else ""

                    followup_instruction = """
## 🔜 다음 회의 안건
다음 회의에서 논의할 안건을 정리해주세요.
""" if include_followup else ""

                    prompt = f"""
당신은 전문 회의록 정리 AI입니다.
회의 유형: {meeting_type}
출력 언어: {language}

아래 회의 내용을 다음 형식으로 정리해주세요:

## 📋 회의 요약
회의 목적과 주요 논의 내용을 3줄 이내로 간결하게 요약

## 👥 참석자
참석자 목록과 역할 (확인 가능한 경우)

## ✅ 액션 아이템
| 할 일 | 담당자 | 기한 |
|------|-------|------|
표 형식으로 정리. 담당자/기한 불명확하면 "미정"으로 표기

## 💡 핵심 결정 사항
- 회의에서 최종 결정된 중요 사항들을 bullet point로

{followup_instruction}
{email_instruction}

---
회의 내용:
{meeting_text}
"""
                    
                    response = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    result = response.content[0].text
                    
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="📥 결과 다운로드 (.txt)",
                        data=result,
                        file_name="회의록_정리결과.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {str(e)}")
    else:
        st.markdown("""
        <div style="color: #999; text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 3rem;">📋</div>
            <div style="margin-top: 1rem;">왼쪽에 회의 내용을 입력하고<br>정리하기 버튼을 눌러주세요</div>
        </div>
        """, unsafe_allow_html=True)

# 하단 안내
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.8rem;">
    회의록 정리 AI Agent · Powered by Claude AI · SK 신입구성원 과정 사전과제
</div>
""", unsafe_allow_html=True)
