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
    
    # 시연용 입력 폼 구성 (고객 앞에서 직접 조작하는 맛을 줍니다)
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
    st.subheader("🧠 AI RCA Agent 센터 (SKI E&S 지식 자산 기반 분석) ")
    
    if submit_button:
        # 데이터가 전송되는 동안 시각적 효과 연출 (Running Tool 느낌 재현)
        status_box = st.empty()
        
        status_box.status("🔗 [Step 1] Neo4j 그래프 데이터베이스 접속 중... 알람-고장 모드 토폴로지 분석")
        time.sleep(1.2)
        
        status_box.status("🌲 [Step 2] Pinecone 벡터 데이터베이스 검색 중... 과거 RCA 이력 및 기술 매뉴얼 매칭")
        time.sleep(1.5)
        
        status_box.status("🤖 [Step 3] AI 에이전트 컨텍스트 융합 및 최종 엔지니어링 리포트 생성 중...")
        
        # 3. n8n Webhook 연동 통신 호출
        # ★ 주의: 사장님의 n8n Webhook Production 또는 Test URL 주소로 변경해 주세요!
        n8n_url = "https://seoneenam.app.n8n.cloud/webhook/rca-test" 
        
# [🚨 데이터 전송 포맷 완벽 정제]
        # AI가 헷갈리지 않도록 선택된 글자(문자열)와 숫자를 명확하게 텍스트로 조립해 전달합니다.
        payload = {
            "device": str(selected_device),
            "alarm": str(alarm_code),
            "value": float(current_value),
            "prompt": f"대상 설비는 {selected_device}이고, 발생한 알람은 {alarm_code}이며, 현재 측정 수치는 {current_value}mm/s야. 이 정보를 바탕으로 실시간 툴을 호출해서 최종 RCA 리포트를 정식 서식에 맞춰 상세히 작성해줘."
        }
        
        try:
            # n8n으로 포스트 요청 발송
            response = requests.post(n8n_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                status_box.empty() # 로딩 UI 제거
                st.success("✅ 실시간 종합 RCA 리포트 발행 완료")
                
                # [🚨 알맹이 추출 치트키 로직] 
                # n8n이 주는 데이터가 어떤 형태든(리스트, 딕셔너리, 텍스트) 무조건 답변만 쏙 빼냅니다.
                report_text = ""
                try:
                    res_json = response.json()
                    
                    # 케이스 1: n8n 응답이 리스트 형태인 경우 [ { "json": { "output": "내용" } } ]
                    if isinstance(res_json, list) and len(res_json) > 0:
                        inner_data = res_json[0]
                        if isinstance(inner_data, dict):
                            # json -> output 순서로 뒤지거나 안되면 최선을 다해 뒤짐
                            report_text = inner_data.get('json', {}).get('output', "")
                            if not report_text:
                                report_text = inner_data.get('output', "")
                            if not report_text:
                                # json 밑의 첫 번째 값을 그냥 다 가져옴
                                json_body = inner_data.get('json', {})
                                report_text = list(json_body.values())[0] if json_body else str(inner_data)
                    
                    # 케이스 2: n8n 응답이 딕셔너리 형태인 경우 { "output": "내용" }
                    elif isinstance(res_json, dict):
                        report_text = res_json.get('output', "")
                        if not report_text:
                            # 딕셔너리 안에 들어있는 첫 번째 긴 텍스트 값을 추출
                            report_text = list(res_json.values())[0]
                    
                except Exception as parse_error:
                    # 케이스 3: JSON 구조가 아니라 그냥 생 텍스트로 넘어온 경우
                    report_text = response.text
                
                # 만약 위 처리를 다 거쳤는데도 텍스트가 안 담겼다면 원본을 백업
                if not report_text or str(report_text).strip() == "{}":
                    report_text = response.text

                st.markdown("---")
                # 최종 정제된 명품 마크다운 보고서 화면에 낙하!
                st.markdown(report_text)
                
            else:
                status_box.empty()
                st.error(f"❌ n8n 연동 실패 (오류 코드: {response.status_code})")
                st.caption(response.text)
                
        except Exception as e:
            status_box.empty()
            st.error(f"❌ 네트워크 연결 오류: {str(e)}")
            
    else:
        # 버튼을 누르기 전 대기 화면 상태 연출
        st.write("")
        st.info("왼쪽 관제 패널에서 이상 신호를 발생시키면, 실시간으로 지식 베이스(Graph + Vector DB)를 탐색하여 이곳에 엔지니어링 리포트를 출력합니다.")
