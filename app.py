import streamlit as st
import os
from PIL import Image
import time

import json
import pandas as pd
# --- 1. 앱에 필요한 기본 데이터 및 설정 ---
SUBMITTED_LOGS_FILE = "submitted_logs.json"
# 실험 결과에 따라 보여줄 이미지 파일들을 생성하는 함수
# @st.cache_resource: 함수 결과를 캐시에 저장하여 앱 실행 속도를 높여줍니다.
@st.cache_resource
def create_images():
    """실험 결과에 필요한 이미지 파일들을 생성합니다."""
    image_dir = "images"
    os.makedirs(image_dir, exist_ok=True)

    # 생성할 이미지 정보: 파일명, 배경색
    images_to_create = {
        "litmus_red.png": "#FF5733",
        "litmus_blue.png": "#335BFF",        
        "phenol_red.png": "#FF33A1",
        "phenol_colorless.png": "#E0E0E0",
    }

    for filename, color in images_to_create.items():
        filepath = os.path.join(image_dir, filename)
        if not os.path.exists(filepath):
            img = Image.new('RGB', (250, 250), color=color)
            img.save(filepath)

# 제출된 탐구일지를 파일에서 불러오는 함수
def load_submitted_logs():
    if not os.path.exists(SUBMITTED_LOGS_FILE):
        return []
    try:
        with open(SUBMITTED_LOGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

# 탐구일지를 파일에 저장하는 함수
def save_submitted_logs(logs):
    with open(SUBMITTED_LOGS_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4, ensure_ascii=False)


# --- 2. 페이지 기본 설정 및 초기화 ---

st.set_page_config(
    page_title="산-염기 탐구 실험실",
    page_icon="🧪",
    layout="centered" # 화면을 중앙 정렬하여 집중도를 높임
)

# 앱 실행 시 필요한 이미지 파일들을 미리 생성
create_images()

# 세션 상태(session_state) 초기화: 앱 사용 중 데이터를 기억하기 위함
if 'experiment_step' not in st.session_state:
    st.session_state.experiment_step = "ready"  # 현재 실험 단계 (ready, result, done)
    st.session_state.experiment_data = {}      # 현재 실험 정보 저장
    st.session_state.log = []                  # 탐구 일지 기록
    st.session_state.requests = []             # 학생 요청 목록
    # 기본 용액 데이터를 세션 상태에 저장하여 동적으로 관리
    st.session_state.solution_data = {
        "레몬즙": "산성",
        "식초": "산성",
        "사이다": "산성",
        "비눗물": "염기성",
        "치약 용액": "염기성",
        "유리세정제": "염기성",
    }


# --- 3. 화면 구성 ---

st.title("🧪 산-염기 탐구 실험실")
st.markdown("---")

# STEP 1: 실험 준비 단계
if st.session_state.experiment_step == "ready":
    st.header("🔬 실험 준비하기")

    solution = st.selectbox(
        "어떤 용액을 관찰해볼까요?",
        options=list(st.session_state.solution_data.keys()),
        index=None,
        placeholder="용액을 선택하세요"
    )

    # 공통 지시약 선택
    indicator = st.selectbox(
        "어떤 지시약을 사용해볼까요?",
        options=["리트머스 종이", "페놀프탈레인 용액"],
        index=None,
        placeholder="지시약을 선택하세요"
    )

    if st.button("🧪 실험 시작!", use_container_width=True):
        if not solution or not indicator:
            st.warning("용액과 지시약을 모두 선택해주세요!")
        else:
            property = st.session_state.solution_data.get(solution)
            # 선택한 실험 정보를 세션 상태에 저장
            if property: # property가 None이 아닌 경우에만 진행
                st.session_state.experiment_data = {
                    "solution": solution,
                    "indicator": indicator,
                    "property": property
                }
                st.session_state.experiment_step = "result"
                st.rerun()

    st.markdown("---")
    st.subheader("💡 새로운 용액 탐구 요청하기")
    new_solution_request = st.text_input("실험해보고 싶은 다른 용액이 있나요?", placeholder="예: 오렌지 주스, 샴푸")
    if st.button("요청 보내기"):
        if new_solution_request:
            # 이미 목록에 있거나 요청된 용액인지 확인
            if new_solution_request in st.session_state.solution_data:
                st.info(f"'{new_solution_request}'은(는) 이미 실험 목록에 있어요!")
            elif new_solution_request in st.session_state.requests:
                st.info(f"'{new_solution_request}'은(는) 이미 선생님께 요청했어요!")
            else:
                st.session_state.requests.append(new_solution_request)
                st.success(f"'{new_solution_request}' 용액을 선생님께 요청했습니다! 선생님이 추가해주시면 목록에 나타날 거예요.")
        else:
            st.warning("요청할 용액의 이름을 입력해주세요.")

# STEP 2: 실험 결과 확인 및 판단 단계
elif st.session_state.experiment_step == "result":
    exp_data = st.session_state.experiment_data
    st.header(f"📊 '{exp_data['solution']}' 실험 결과")

    # 지시약과 용액 성질에 따라 결과 이미지 표시
    prop = exp_data["property"]

    # 1. 리트머스 종이 실험 결과
    if exp_data["indicator"] == "리트머스 종이":
        if prop == "산성":
            st.image("images/litmus_red.png", caption="푸른색 리트머스 종이가 붉게 변했습니다.")
        elif prop == "염기성":
            st.image("images/litmus_blue.png", caption="붉은색 리트머스 종이가 푸르게 변했습니다.")
    
    # 2. 페놀프탈레인 용액 실험 결과
    elif exp_data["indicator"] == "페놀프탈레인 용액":
        if prop == "염기성":
            st.image("images/phenol_red.png", caption="페놀프탈레인 용액이 붉은색으로 변했습니다.")
        elif prop == "산성":
            st.image("images/phenol_colorless.png", caption="페놀프탈레인 용액의 색이 변하지 않았습니다.")

    st.markdown("---")
    st.subheader("🤔 결과 분석하기")
    
    # 학생의 판단 입력받기
    student_choice = st.radio(
        "실험 결과를 보고 이 용액이 무엇이라고 생각하나요?",
        ["산성", "염기성"],
        index=None,
        horizontal=True
    )

    if st.button("결과 확인하기", use_container_width=True):
        if student_choice is None:
            st.warning("자신의 생각을 선택해주세요!")
        else:
            is_correct = student_choice == prop
            # 정답과 학생의 선택 비교
            if is_correct:
                st.success(f"🎉 정답입니다! '{exp_data['solution']}'은(는) '{prop}'이 맞습니다.")
                st.balloons()
            else:
                st.error(f"아쉬워요. 정답은 '{prop}'입니다. 왜 그런지 다시 생각해볼까요?")
            
            # 탐구 일지에 결과 기록
            log_entry = {
                "용액": exp_data['solution'],
                "사용한 지시약": exp_data['indicator'],
                "나의 예상": student_choice,
                "실제 결과": prop,
                "정답 여부": "✅ 정답" if is_correct else "❌ 오답"
            }
            st.session_state.log.append(log_entry)

            # 3초 후 초기 화면으로 돌아가기
            st.info("3초 후에 새로운 실험을 준비합니다.")
            st.session_state.experiment_step = "done" # 완료 상태로 변경
            time.sleep(3)
            st.session_state.experiment_step = "ready" # 준비 상태로 리셋
            st.rerun()

# STEP 3: 실험 완료 후 리셋 단계 (사용자에게는 보이지 않음)
elif st.session_state.experiment_step == "done":
    st.info("실험을 초기화하는 중입니다...")

# --- 4. 탐구 일지 표시 ---
st.markdown("---")
with st.expander("📖 나의 탐구 일지 보기"):
    if not st.session_state.log:
        st.info("아직 기록된 실험이 없습니다. 첫 실험을 시작해보세요!")
    else:
        # 로그를 DataFrame으로 변환하여 표로 표시
        log_df = pd.DataFrame(st.session_state.log)
        # 최신 기록이 위로 오도록 인덱스를 역순으로 재설정
        st.dataframe(log_df.iloc[::-1].reset_index(drop=True), use_container_width=True)

        # 탐구 일지 초기화 버튼
        if st.button("⚠️ 탐구 일지 모두 지우기"):
            st.session_state.log = []
            st.success("탐구 일지를 모두 지웠습니다!")
            time.sleep(1)
            st.rerun()

    # --- 4-1. 탐구 일지 전송 기능 ---
    st.markdown("---")
    st.subheader("👩‍🏫 선생님께 탐구일지 전송하기")

    with st.form("submission_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            grade = st.text_input("학년")
        with col2:
            class_num = st.text_input("반")
        with col3:
            student_num = st.text_input("번호")
        with col4:
            name = st.text_input("이름")
        
        submitted = st.form_submit_button("전송하기")

        if submitted:
            if not all([grade, class_num, student_num, name]):
                st.warning("학년, 반, 번호, 이름을 모두 입력해주세요.")
            elif not st.session_state.log:
                st.warning("전송할 탐구일지 내용이 없습니다. 먼저 실험을 진행해주세요.")
            else:
                all_logs = load_submitted_logs()
                submission_data = {
                    "info": f"{grade}학년 {class_num}반 {student_num}번 {name}",
                    "log": st.session_state.log,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                all_logs.append(submission_data)
                save_submitted_logs(all_logs)
                st.success("탐구일지를 선생님께 성공적으로 전송했습니다!")


# --- 5. 교사 관리 페이지 ---
st.markdown("---")
with st.expander("👩‍🏫 교사 관리 페이지"):
    # 비밀번호 입력 필드
    password = st.text_input("선생님 비밀번호를 입력하세요.", type="password")

    # 비밀번호가 맞을 경우에만 관리자 기능 표시
    # st.secrets를 사용하여 안전하게 비밀번호를 불러옵니다.
    # 이 비밀번호는 Streamlit Cloud의 설정에서 지정하게 됩니다.
    if "TEACHER_PASSWORD" in st.secrets and password == st.secrets["TEACHER_PASSWORD"]:
        tab1, tab2 = st.tabs(["용액 요청 관리", "제출된 탐구일지"])

        with tab1:
            st.subheader("학생들이 요청한 용액 목록")

            if not st.session_state.requests:
                st.info("아직 학생들이 요청한 새로운 용액이 없습니다.")
            else:
                # 요청된 각 용액에 대해 처리 UI 생성
                for req_solution in st.session_state.requests[:]: # 복사본으로 순회하여 안전하게 제거
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.markdown(f"**요청 용액:** `{req_solution}`")
                        with col2:
                            # 각 용액에 대한 고유한 키를 생성
                            property_choice = st.radio(
                                "성질 선택", ["산성", "염기성"],
                                key=f"prop_{req_solution}",
                                horizontal=True,
                                label_visibility="collapsed"
                            )
                        with col3:
                            if st.button("추가하기", key=f"add_{req_solution}"):
                                st.session_state.solution_data[req_solution] = property_choice
                                st.session_state.requests.remove(req_solution)
                                st.success(f"'{req_solution}'({property_choice})을(를) 실험 목록에 추가했습니다.")
                                time.sleep(1)
                                st.rerun()
        
        with tab2:
            st.subheader("학생들이 제출한 탐구일지")
            submitted_logs = load_submitted_logs()

            if not submitted_logs:
                st.info("아직 제출된 탐구일지가 없습니다.")
            else:
                if st.button("⚠️ 모든 제출 기록 지우기"):
                    save_submitted_logs([])
                    st.success("제출된 모든 탐구일지를 삭제했습니다.")
                    time.sleep(1)
                    st.rerun()

                # 최신 제출이 위로 오도록 역순으로 표시
                for i, submission in enumerate(reversed(submitted_logs)):
                    with st.container(border=True):
                        st.markdown(f"**제출자:** {submission['info']} ({submission['timestamp']})")
                        log_df = pd.DataFrame(submission['log'])
                        st.dataframe(log_df, use_container_width=True)

    elif password: # 비밀번호가 입력되었지만 일치하지 않을 경우
        st.error("비밀번호가 올바르지 않습니다. 다시 시도해주세요.")
