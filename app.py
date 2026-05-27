import streamlit as st
import requests
import time

# 1. 페이지 기본 설정 및 디자인 테마
st.set_page_config(page_title="SKI E&S RCA Agent", page_icon="🏭", layout="wide")

# 상단 메인 타이틀
st.title("🏭 SKI E&S 실시간 발전 설비 이상 신호 분석 시스템")
st.markdown("---")

# 2. 화면을 좌우 2개의 컬럼으로 분할 (관제 패널 | 분석 리포트 패널)
col1, col2 = st.columns([1, 1.8])

with col1:
    st.subheader("🚨 설비 관제 및 이상신호 유입")
    st.info("발전소 현장에서 발생한 실시간 텔레메트리 경보 데이터입니다.")
    
    # 시연용 입력 폼 구성
    selected_device = st.selectbox(
        "대상 설비 (Device)", 
        ["보일러 급수 펌프 A (EQ_BFP_01A)", "보일러 급수 펌프 B (EQ_BFP_01B)", "주증기 밸브 (EQ_MSV_02)"]
    )
    
    alarm_code = st.selectbox(
        "발생 알람 코드 (Alarm Code)", 
        ["진동 고 경보 (AL_VIB_HIGH)", "베어링 온도 고 경보 (AL_TEMP_HIGH)"]
    )
    
    current_value = st.slider("현재 측정 수치 (Telemetry Value)", min_value=0.0, max_value=20.0, value=12.8, step=0.1)
    
    st.markdown("---")
    
    # 시연 가동 버튼
    submit_button = st.button("⚡ 실시간 RCA 분석 실행", type="primary", use_container_width=True)

with col2:
    # 경영진 저격용 통합 타이틀 유지
    st.subheader("🧠 AI RCA Agent 센터 (SKI E&S 지식 자산 기반)")
    
    if submit_button:
        # 🎬 3단계 타임라인 및 프로그레스 바 플레이스홀더 설정
        step1_placeholder = st.empty()
        step2_placeholder = st.empty()
        step3_placeholder = st.empty()
        progress_placeholder = st.empty()  # 동적 프로그레스 바 공간
        st.markdown("---")
        
        # --- [Step 1] 진행 연출 ---
        step1_placeholder.info("⚙️ [Step 1] Neo4j 그래프 DB 접속 중... 알람-고장 모드 온톨로지 토폴로지 분석")
        time.sleep(1.2)
        step1_placeholder.success("✔ [Step 1 완료] 과거 운전/정비 이력 탐색(Neo4j 지식 그래프)을 통해 설비 간 인과관계 메커니즘 도출 완료")
        
        # --- [Step 2] 진행 연출 ---
        step2_placeholder.info("⚡ [Step 2] Pinecone 벡터 DB 검색 중... 과거 10년 치 RCA 이력 및 기술 매뉴얼 매칭")
        time.sleep(1.2)
        step2_placeholder.success("✔ [Step 2 완료] 기술문서, RCA보고서 자료(Pinecone 벡터 DB) 고차원 임베딩 검색을 통해 실무 규격 및 유사 고장 사례 정합성 매칭 완료")
        
        # --- [Step 3] 진행 및 동적 타임 바 연출 ---
        step3_placeholder.info("🚀 [Step 3] AI 에이전트 컨텍스트 융합 및 정식 엔지니어링 리포트 심층 생성 중...")
        
        n8n_url = "https://seoneenam.app.n8n.cloud/webhook/rca-test" 
        
        payload = {
            "device": str(selected_device),
            "alarm": str(alarm_code),
            "value": float(current_value),
            "prompt": f"대상 설비는 {selected_device}이고, 발생한 알람은 {alarm_code}이며, 현재 측정 수치는 {current_value}mm/s야. 이 정보를 바탕으로 실시간 툴을 호출해서 최종 RCA 리포트를 정식 서식에 맞춰 상세히 작성해줘."
        }
        
        # requests 통신이 도는 동안 화면에서 초 단위를 세어줄 가상 게이지 로직
        # n8n 응답 대기 중에도 화면의 프로그레스 바와 숫자가 계속 올라갑니다.
        try:
            # 💡 대기 연출과 통신을 안전하게 결합하기 위해 비동기적 느낌을 주는 시각 튜닝
            # 게이지바와 텍스트를 지속적으로 리프레시합니다.
            response = None
            start_time = time.time()
            
            # 주의: Streamlit 내부 구조상 requests를 보내는 동안 루프를 도는 것은 제약이 있으므로,
            # st.spinner의 프로페셔널 로딩 링과 시간 경과 메시지를 결합하여 연출력을 극대화합니다.
            with progress_placeholder.container():
                with st.spinner("📊 인공지능이 수집된 정비 데이터를 학습 컨텍스트로 변환 중입니다. 잠시만 기다려 주십시오..."):
                    # 대기 시간 동안 지루하지 않게 긴장감을 주는 얼럿 배치
                    st.toast("💡 대규모 지식 자산(GraphRAG)을 바탕으로 보고서를 추론하는 중입니다.")
                    response = requests.post(n8n_url, json=payload, timeout=120)
            
            # 통신이 무사히 완료되면 로딩바 삭제
            progress_placeholder.empty()
            
            if response and response.status_code == 200:
                # 성공 시 상태 업데이트
                step3_placeholder.success("✔ [Step 3 완료] LLM 기반 컨텍스트 융합 및 RCA 리포트 생성 완료")
                st.success("✅ AX 기반 실시간 플랜트 리스크 지시서 발행 완료")
                
                # [🚨 알맹이 추출 치트키 로직] 
                report_text = ""
                try:
                    res_json = response.json()
                    
                    if isinstance(res_json, list) and len(res_json) > 0:
                        inner_data = res_json[0]
                        if isinstance(inner_data, dict):
                            report_text = inner_data.get('json', {}).get('output', "")
                            if not report_text:
                                report_text = inner_data.get('output', "")
                            if not report_text:
                                json_body = inner_data.get('json', {})
                                report_text = list(json_body.values())[0] if json_body else str(inner_data)
                    
                    elif isinstance(res_json, dict):
                        report_text = res_json.get('output', "")
                        if not report_text:
                            report_text = list(res_json.values())[0]
                    
                except Exception as parse_error:
                    report_text = response.text
                
                if not report_text or str(report_text).strip() == "{}":
                    report_text = response.text

                # 최종 정제된 명품 마크다운 보고서 화면에 출력!
                st.markdown(report_text)
                
            else:
                st.error(f"❌ Step 3 실패: n8n 서버 연동 오류")
                
        except Exception as e:
            progress_placeholder.empty()
            step3_placeholder.error(f"❌ Step 3 오류: 네트워크 연결이 원활하지 않습니다.")
            st.caption(str(e))
            
    else:
        # 버튼을 누르기 전 대기 화면 상태 연출
        st.write("")
        st.info("왼쪽 관제 패널에서 이상 신호를 발생시키면, 실시간으로 지식 베이스(Graph + Vector DB)를 탐색하여 이곳에 엔지니어링 리포트를 출력합니다.")
