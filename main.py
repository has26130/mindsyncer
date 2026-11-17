import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components
from datetime import datetime, date

# ==========================================
# 0. 페이지 기본 설정 & 반응형 커스텀 CSS
# ==========================================
st.set_page_config(
    page_title="Mind-Sync | 바이오리듬 & 번아웃 케어 학습 OS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 전체 폰트 및 반응형 카드 스타일 */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
        color: #f8fafc;
    }
    .main-header p {
        margin: 0.4rem 0 0 0;
        color: #cbd5e1;
        font-size: 1rem;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    .badge-high {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 10px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-mid {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .badge-low {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 10px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.8rem;
    }
    .battery-box {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 세션 상태(Session State) 초기화
# ==========================================
if "caffeine_logs" not in st.session_state:
    st.session_state.caffeine_logs = [
        {"drink": "아메리카노 (150mg)", "mg": 150, "hour": 8.5},
        {"drink": "몬스터 에너지 (100mg)", "mg": 100, "hour": 16.0}
    ]

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "title": "수학 미적분 킬러문항 5제 풀이", "level": "🔥 고집중 (Deep Work)", "hours": 2.0, "done": False},
        {"id": 2, "title": "소프트웨어와 생활 수행평가 코딩 및 디버깅", "level": "🔥 고집중 (Deep Work)", "hours": 1.5, "done": True},
        {"id": 3, "title": "국어 문학 작품 해설 노트 정리", "level": "⚡ 중집중 (Flow Work)", "hours": 1.5, "done": False},
        {"id": 4, "title": "영어 단어 Day 15~16 암기", "level": "🌱 저집중 (Light Work)", "hours": 1.0, "done": True},
        {"id": 5, "title": "오답노트 프린트 스크랩 및 파일 정리", "level": "🌱 저집중 (Light Work)", "hours": 1.0, "done": False},
    ]

if "weekly_logs" not in st.session_state:
    st.session_state.weekly_logs = [
        {"day": "월", "sleep": 6.5, "caffeine": 150, "stress": 45, "focus_rate": 82, "mood": "🙂 평온"},
        {"day": "화", "sleep": 5.5, "caffeine": 220, "stress": 65, "focus_rate": 75, "mood": "😐 보통"},
        {"day": "수", "sleep": 4.5, "caffeine": 300, "stress": 82, "focus_rate": 60, "mood": "😫 피곤"},
        {"day": "목", "sleep": 5.0, "caffeine": 250, "stress": 78, "focus_rate": 64, "mood": "😰 불안"},
        {"day": "금", "sleep": 7.0, "caffeine": 100, "stress": 40, "focus_rate": 88, "mood": "🤩 최고"},
        {"day": "토", "sleep": 8.0, "caffeine": 50,  "stress": 30, "focus_rate": 90, "mood": "🙂 평온"},
        {"day": "일", "sleep": 6.0, "caffeine": 200, "stress": 58, "focus_rate": 78, "mood": "😐 보통"},
    ]

if "detox_active" not in st.session_state:
    st.session_state.detox_active = False

# ==========================================
# 2. 핵심 과학 알고리즘 함수 (카페인 반감기 & 뇌 각성도)
# ==========================================
DRINK_DB = {
    "아메리카노 (150mg)": 150,
    "고카페인 에너지드링크 (200mg)": 200,
    "몬스터 에너지 (100mg)": 100,
    "핫식스 (60mg)": 60,
    "콜라 / 녹차 (35mg)": 35,
    "디카페인 커피 (10mg)": 10
}

SENSITIVITY_HALF_LIFE = {
    "둔감 (반감기 3.5시간 - 빠른 분해)": 3.5,
    "보통 (반감기 5.0시간 - 표준)": 5.0,
    "민감 (반감기 7.0시간 - 느린 분해)": 7.0
}

def simulate_biorhythm(sleep_hours, recent_sleep_avg, wake_hour, sensitivity_label, caffeine_logs):
    """
    24시간(06시 ~ 익일 04시) 동안의 체내 잔여 카페인 농도(mg)와
    뇌 각성도(Brain Alertness Score: 0~100)를 시뮬레이션합니다.
    """
    half_life = SENSITIVITY_HALF_LIFE[sensitivity_label]
    hours = np.arange(6.0, 28.5, 0.5)  # 06:00 ~ 익일 04:00 (0.5시간 단위)
    time_labels = [f"{int(h % 24):02d}:{int((h % 1) * 60):02d}" + (" (익일)" if h >= 24 else "") for h in hours]

    # 수면 부채(Sleep Debt) 계산 (권장 수면 7.5시간 기준)
    daily_debt = max(0.0, 7.5 - sleep_hours)
    cumulative_debt = max(0.0, (7.5 - recent_sleep_avg) * 3.0 + daily_debt)
    sleep_penalty = min(35.0, cumulative_debt * 2.8)

    caffeine_curve = []
    alertness_curve = []

    for h in hours:
        # 1) 잔여 카페인 계산: 섭취 후 45분간 흡수 상승, 이후 지수 감쇠 C(t) = C0 * (0.5)^(t / half_life)
        total_caf = 0.0
        for log in caffeine_logs:
            dt = h - log["hour"]
            if dt >= 0:
                if dt < 0.75:
                    absorption = dt / 0.75
                    total_caf += log["mg"] * absorption
                else:
                    total_caf += log["mg"] * (0.5 ** ((dt - 0.75) / half_life))
        caffeine_curve.append(round(total_caf, 1))

        # 2) 기본 생체리듬(Circadian Rhythm) 계산
        awake_duration = max(0.0, h - wake_hour)
        # 오전 피크(기상 후 3~5시간), 점심 식곤증(13~15시), 저녁 2차 집중(17~20시), 야간 멜라토닌 분비(22시 이후)
        circadian_wave = 18 * np.sin((h - wake_hour - 1.5) * np.pi / 10.0)
        post_lunch_dip = -14 * np.exp(-((h - 14.0) ** 2) / 1.5)
        homeostatic_fatigue = awake_duration * 2.3  # 깨어있는 시간이 길어질수록 피로 누적

        # 카페인 각성 부스트 (최대 +25점, 과다 섭취 시 불안/신경과민으로 효율 저하 반영)
        if total_caf <= 250:
            caf_boost = min(22.0, total_caf * 0.11)
        else:
            caf_boost = 22.0 - (total_caf - 250) * 0.05  # 과다 섭취 역효과(Jitteriness)

        base_score = 78.0 - sleep_penalty + circadian_wave + post_lunch_dip - homeostatic_fatigue + caf_boost
        alertness = float(np.clip(base_score, 15.0, 99.0))
        alertness_curve.append(round(alertness, 1))

    df = pd.DataFrame({
        "hour_num": hours,
        "시각": time_labels,
        "잔여 카페인(mg)": caffeine_curve,
        "뇌 각성도(%)": alertness_curve
    })

    # 숙면 가능 시각 판별 (잔여 카페인이 수면 방해 임계치 50mg 이하로 떨어지는 첫 밤 시각)
    sleep_ready_time = "22:00 이전 숙면 가능"
    night_df = df[df["hour_num"] >= 21.0]
    above_threshold = night_df[night_df["잔여 카페인(mg)"] > 50.0]
    if not above_threshold.empty:
        last_high_hour = above_threshold["hour_num"].max()
        ready_h = last_high_hour + 0.5
        if ready_h >= 28.0:
            sleep_ready_time = "⚠️ 새벽 04:00 이후 (수면 심각 방해)"
        else:
            sleep_ready_time = f"{int(ready_h % 24):02d}:{int((ready_h % 1) * 60):02d}" + (" (익일 새벽)" if ready_h >= 24 else "")

    return df, round(cumulative_debt, 1), sleep_ready_time

# ==========================================
# 3. 사이드바: 내 생체 데이터 입력 및 시연 컨트롤러
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ 내 바이오 프로필 설정")
    st.caption("수면·카페인 상태에 따라 전체 앱의 스케줄과 타이머가 실시간 동기화됩니다.")

    sleep_today = st.slider("🌙 어젯밤 수면 시간 (시간)", 2.0, 10.0, 5.5, 0.5)
    sleep_recent = st.slider("🛌 최근 3일 평균 수면 (시간)", 3.0, 10.0, 6.0, 0.5)
    wake_hour = st.slider("⏰ 오늘 기상 시각 (시)", 5.0, 10.0, 7.0, 0.5)
    sensitivity = st.selectbox(
        "🧬 카페인 대사 민감도 (개인차 보정)",
        list(SENSITIVITY_HALF_LIFE.keys()),
        index=1,
        help="사람마다 다른 간 효소(CYP1A2) 분해 속도를 반영해 오차를 줄입니다."
    )
    current_fatigue = st.slider("🔋 현재 주관적 피로도 (%)", 0, 100, 55, 5)

    st.divider()
    st.markdown("### 🎬 발표 시연용 원클릭 프리셋")
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button("🚨 시험기간 과부하", use_container_width=True):
            st.session_state.caffeine_logs = [
                {"drink": "아메리카노 (150mg)", "mg": 150, "hour": 8.0},
                {"drink": "고카페인 에너지드링크 (200mg)", "mg": 200, "hour": 14.5},
                {"drink": "몬스터 에너지 (100mg)", "mg": 100, "hour": 20.5},
            ]
            st.toast("시험기간 카페인 과부하 시나리오가 적용되었습니다!", icon="🚨")
            st.rerun()
    with col_demo2:
        if st.button("🌿 건강한 밸런스", use_container_width=True):
            st.session_state.caffeine_logs = [
                {"drink": "콜라 / 녹차 (35mg)", "mg": 35, "hour": 10.0},
                {"drink": "디카페인 커피 (10mg)", "mg": 10, "hour": 15.0}
            ]
            st.session_state.detox_active = False
            st.toast("건강한 수면·학습 밸런스 모드가 적용되었습니다!", icon="🌿")
            st.rerun()

# 생체리듬 시뮬레이션 실행
bio_df, sleep_debt, sleep_ready_str = simulate_biorhythm(
    sleep_today, sleep_recent, wake_hour, sensitivity, st.session_state.caffeine_logs
)

total_caffeine_today = sum(item["mg"] for item in st.session_state.caffeine_logs)
peak_row = bio_df.loc[bio_df["뇌 각성도(%)"].idxmax()]
golden_time_str = peak_row["시각"]
max_alertness = peak_row["뇌 각성도(%)"]

# ==========================================
# 4. 상단 헤더 & 핵심 상태 요약 배너
# ==========================================
st.markdown("""
<div class="main-header">
    <h1>🧠 Mind-Sync (마인드싱크)</h1>
    <p>무작정 밤새우지 마세요. 수면·카페인 반감기·뇌 과학 데이터에 맞춘 올인원 바이오리듬 학습 OS</p>
</div>
""", unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
m1.metric(
    "📉 누적 수면 부채",
    f"{sleep_debt} 시간",
    delta="-주의 (회복 필요)" if sleep_debt > 5 else "정상 범위",
    delta_color="inverse" if sleep_debt > 5 else "normal"
)
m2.metric(
    "☕ 오늘 총 카페인 섭취량",
    f"{total_caffeine_today} mg",
    delta="청소년 일일권장량(150mg) 초과!" if total_caffeine_today > 150 else "권장량 이내 안전",
    delta_color="inverse" if total_caffeine_today > 150 else "normal"
)
m3.metric(
    "🔥 오늘의 뇌 각성 골든타임",
    golden_time_str,
    delta=f"최고 각성도 {max_alertness}%"
)
m4.metric(
    "🛌 카페인 분해 후 숙면 가능 시각",
    sleep_ready_str,
    delta="50mg 이하 도달 기준"
)

# ==========================================
# 5. 메인 5대 모듈 탭 구성
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧪 1. 바이오 & 카페인 시뮬레이터",
    "📅 2. 에너지 맞춤 스마트 플래너",
    "🎧 3. 적응형 몰입 스튜디오 (타이머·사운드)",
    "📊 4. 번아웃 가드 & 주간 리포트",
    "🎤 5. 가치 분석 & Pitch Deck 요약"
])

# ------------------------------------------
# TAB 1: 바이오리듬 & 카페인 반감기 시뮬레이터
# ------------------------------------------
with tab1:
    st.subheader("🧪 시간대별 카페인 반감기 & 뇌 각성도 시뮬레이션")
    st.write("마신 음료와 섭취 시각을 추가하면 반감기 공식($C(t) = C_0 \\times 0.5^{t/h}$)에 따라 체내 카페인 분해 곡선과 뇌 집중력 변화가 실시간 계산됩니다.")

    col_left, col_right = st.columns([1.1, 2.2])

    with col_left:
        st.markdown("#### ➕ 카페인 섭취 기록 추가")
        selected_drink = st.selectbox("마신 음료 선택", list(DRINK_DB.keys()))
        intake_hour = st.slider("섭취 시각 (24시간 기준)", 6.0, 23.5, 15.0, 0.5, format="%.1f시")

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("☕ 음료 추가하기", use_container_width=True, type="primary"):
                st.session_state.caffeine_logs.append({
                    "drink": selected_drink,
                    "mg": DRINK_DB[selected_drink],
                    "hour": intake_hour
                })
                st.rerun()
        with c_btn2:
            if st.button("🗑️ 기록 전체 초기화", use_container_width=True):
                st.session_state.caffeine_logs = []
                st.rerun()

        st.markdown("#### 📋 오늘 마신 음료 목록")
        if st.session_state.caffeine_logs:
            for idx, item in enumerate(st.session_state.caffeine_logs):
                h_int = int(item["hour"])
                m_int = int((item["hour"] % 1) * 60)
                st.info(f"**{h_int:02d}:{m_int:02d}** — {item['drink']}")
        else:
            st.success("오늘 섭취한 카페인이 없습니다! 깨끗한 수면이 기대됩니다.")

        if total_caffeine_today > 200:
            st.error(
                "🚨 **카페인 과다 경보**: 현재 섭취량이 200mg을 넘었습니다! "
                "심장 두근거림, 손 떨림 및 야간 수면 구조 파괴(깊은 잠 감소)가 발생할 수 있습니다. "
                "지금부터는 물이나 루이보스차로 대체하세요."
            )

    with col_right:
        # 이중 축 인터랙티브 차트 (뇌 각성도 % & 잔여 카페인 mg)
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=bio_df["시각"],
            y=bio_df["뇌 각성도(%)"],
            name="🧠 뇌 각성도 (%)",
            mode="lines+markers",
            line=dict(color="#2563eb", width=3.5),
            fill="tozeroy",
            fillcolor="rgba(37, 99, 235, 0.1)"
        ))

        fig.add_trace(go.Scatter(
            x=bio_df["시각"],
            y=bio_df["잔여 카페인(mg)"],
            name="☕ 체내 잔여 카페인 (mg)",
            mode="lines",
            line=dict(color="#dc2626", width=3, dash="dot"),
            yaxis="y2"
        ))

        # 숙면 방해 마지노선 (50mg) 표시
        fig.add_hline(
            y=50, line_dash="dash", line_color="#f59e0b",
            annotation_text="숙면 방해 임계선 (카페인 50mg)",
            annotation_position="bottom right",
            yref="y2"
        )

        fig.update_layout(
            title="시간대별 뇌 각성도(%) 및 체내 잔여 카페인 농도(mg) 변화",
            xaxis=dict(title="시각 (06:00 ~ 익일 04:00)"),
            yaxis=dict(title="뇌 각성도 (%)", range=[0, 105]),
            yaxis2=dict(title="잔여 카페인 (mg)", overlaying="y", side="right", range=[0, max(350, total_caffeine_today + 50)]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=450,
            margin=dict(l=20, r=20, t=60, b=20),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "💡 **과학적 원리**: 카페인은 뇌의 피로 물질인 '아데노신(Adenosine)' 수용체를 일시적으로 막아 피로를 못 느끼게 할 뿐, "
            "피로 자체를 없애지 않습니다. 늦은 오후 카페인 섭취는 밤잠을 설쳐 다음 날 더 큰 수면 부채를 부르는 악순환을 만듭니다."
        )

# ------------------------------------------
# TAB 2: 에너지 맞춤형 스마트 타임블록 플래너
# ------------------------------------------
with tab2:
    st.subheader("📅 뇌 에너지 동기화 스마트 타임블록 플래너")
    st.write("할 일의 **인지 부하(고집중/중집중/저집중)**를 선택하면, 오늘 나의 시간대별 뇌 각성도 곡선에 맞춰 가장 효율적인 시간대에 과목을 자동 배치합니다.")

    # 가용 에너지 배터리 계산
    available_energy = max(20.0, round(100.0 - sleep_debt * 4.5 - current_fatigue * 0.35, 1))
    if st.session_state.detox_active:
        st.warning("🌿 **디톡스 데이(Detox Day) 모드가 활성화되어 있습니다**: 번아웃 예방을 위해 고집중 학습 권장량이 30% 축소되었습니다.")

    total_planned_hours = sum(t["hours"] for t in st.session_state.tasks if not t["done"])
    completed_hours = sum(t["hours"] for t in st.session_state.tasks if t["done"])
    energy_load = min(100.0, round((total_planned_hours / 7.0) * 100.0, 1))

    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.markdown("##### 🔋 오늘 나의 가용 뇌 에너지 배터리")
        st.progress(int(available_energy) / 100.0, text=f"현재 가용 뇌 에너지: {available_energy}% (수면부채 및 피로도 반영)")
    with b_col2:
        st.markdown("##### 📚 남은 학습 부하 게이지")
        overload_warn = " ⚠️ 에너지 초과 위험! 할 일을 줄이거나 휴식을 넣으세요." if energy_load > available_energy else " ✅ 내 체력 안에서 소화 가능한 최적 분량입니다."
        st.progress(int(min(100, energy_load)) / 100.0, text=f"남은 공부량: {total_planned_hours}시간 (부하도 {energy_load}%){overload_warn}")

    st.divider()

    p_left, p_right = st.columns([1.2, 1.8])

    with p_left:
        st.markdown("#### ✍️ 새로운 할 일(Task) 추가")
        with st.form("add_task_form", clear_on_submit=True):
            new_title = st.text_input("과목 및 학습 내용", placeholder="예: 물리학1 역학 고난도 기출 3문제")
            new_level = st.selectbox("뇌 부하 난이도 선택", [
                "🔥 고집중 (Deep Work)",
                "⚡ 중집중 (Flow Work)",
                "🌱 저집중 (Light Work)"
            ])
            new_hours = st.slider("예상 소요 시간 (시간)", 0.5, 4.0, 1.5, 0.5)
            submitted = st.form_submit_button("📌 플래너에 추가하기", use_container_width=True, type="primary")
            if submitted and new_title.strip():
                next_id = max([t["id"] for t in st.session_state.tasks], default=0) + 1
                st.session_state.tasks.append({
                    "id": next_id,
                    "title": new_title.strip(),
                    "level": new_level,
                    "hours": new_hours,
                    "done": False
                })
                st.rerun()

        st.markdown("#### ✅ 할 일 완료 체크 & 관리")
        for idx, task in enumerate(st.session_state.tasks):
            checked = st.checkbox(
                f"[{task['level'][:4]}] {task['title']} ({task['hours']}h)",
                value=task["done"],
                key=f"task_chk_{task['id']}"
            )
            if checked != task["done"]:
                st.session_state.tasks[idx]["done"] = checked
                st.rerun()

    with p_right:
        st.markdown("#### 🤖 AI 바이오리듬 자동 시간대 매칭 결과")
        st.caption("오늘 나의 뇌 각성도가 가장 높은 시간대부터 🔥고집중 → ⚡중집중 → 🌱저집중 순서로 타임블록을 자동 배정합니다.")

        # 학습 가능 시간대 슬롯 (09시 ~ 23시 중 2시간 단위 블록 추출)
        study_slots = [
            {"slot": "09:00 ~ 11:00 (오전 골든타임)", "hour_ref": 10.0},
            {"slot": "11:00 ~ 13:00 (오전 집중타임)", "hour_ref": 12.0},
            {"slot": "14:00 ~ 16:00 (오후 페이스 조절)", "hour_ref": 15.0},
            {"slot": "16:30 ~ 18:30 (오후 2차 피크)", "hour_ref": 17.5},
            {"slot": "19:30 ~ 21:30 (저녁 마무리 학습)", "hour_ref": 20.5},
            {"slot": "21:30 ~ 23:00 (수면 전 가벼운 복습)", "hour_ref": 22.0},
        ]

        for s in study_slots:
            match_rows = bio_df[bio_df["hour_num"] == s["hour_ref"]]
            s["alertness"] = float(match_rows["뇌 각성도(%)"].iloc[0]) if not match_rows.empty else 65.0

        # 각성도 높은 순으로 슬롯 정렬 후 미완료 과제 우선순위와 매칭
        sorted_slots = sorted(study_slots, key=lambda x: x["alertness"], reverse=True)
        priority_map = {"🔥 고집중 (Deep Work)": 1, "⚡ 중집중 (Flow Work)": 2, "🌱 저집중 (Light Work)": 3}
        active_tasks = sorted(
            [t for t in st.session_state.tasks if not t["done"]],
            key=lambda x: priority_map.get(x["level"], 2)
        )

        schedule_rows = []
        for i, task in enumerate(active_tasks):
            slot_info = sorted_slots[i % len(sorted_slots)]
            schedule_rows.append({
                "추천 시간대": slot_info["slot"],
                "해당 시각 뇌 각성도": f"{slot_info['alertness']}%",
                "배정 난이도": task["level"],
                "추천 학습 과제": task["title"],
                "소요 시간": f"{task['hours']}시간"
            })

        if schedule_rows:
            sched_df = pd.DataFrame(schedule_rows).sort_values(by="추천 시간대")
            st.dataframe(sched_df, use_container_width=True, hide_index=True)
        else:
            st.balloons()
            st.success("🎉 오늘 계획된 모든 학습 과제를 완료했습니다! 충분한 수면으로 뇌를 회복시켜 주세요.")

# ------------------------------------------
# TAB 3: 적응형 몰입 스튜디오 (타이머 + 사운드 믹서 + 호흡 가이드)
# ------------------------------------------
with tab3:
    st.subheader("🎧 적응형 몰입 스튜디오 (Adaptive Focus Studio)")
    st.write("현재 내 피로도와 수면 부채를 분석하여 **최적의 뽀모도로 집중/휴식 비율**을 자동 세팅하고, 브라우저 내장 **Web Audio 신디사이저 백색소음**과 **복식호흡 가이드**를 제공합니다.")

    # 피로도에 따른 적응형 뽀모도로 추천
    if current_fatigue >= 70 or sleep_debt >= 6.0:
        rec_mode = "🌱 회복 모드 (25분 집중 + 5분 휴식)"
        default_focus, default_break = 25, 5
        mode_desc = "현재 수면 부채나 피로도가 높습니다. 짧은 호흡으로 자주 쉬어주어야 번아웃 없이 끝까지 완주할 수 있습니다."
    elif current_fatigue <= 35 and sleep_debt <= 3.0:
        rec_mode = "🔥 하드코어 몰입 모드 (50분 집중 + 10분 휴식)"
        default_focus, default_break = 50, 10
        mode_desc = "최상의 뇌 컨디션입니다! 긴 호흡의 딥워크(Deep Work)로 수학·코딩 등 고난도 문제를 돌파하세요."
    else:
        rec_mode = "⚡ 밸런스 표준 모드 (40분 집중 + 10분 휴식)"
        default_focus, default_break = 40, 10
        mode_desc = "학교 수업 리듬과 가장 잘 맞는 안정적인 집중·휴식 밸런스 모드입니다."

    st.info(f"**🤖 AI 추천 타이머 처방: {rec_mode}**\n\n{mode_desc}")

    # 인터랙티브 타이머 + Web Audio API 사운드 믹서 + 4-7-8 호흡 애니메이션 (단일 HTML/JS 위젯으로 에러 0% 작동)
    studio_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 12px;
            background: #0f172a;
            color: #f8fafc;
            border-radius: 16px;
        }}
        .studio-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 16px;
        }}
        .panel {{
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 18px;
            text-align: center;
        }}
        .timer-display {{
            font-size: 3.4rem;
            font-weight: 800;
            color: #38bdf8;
            margin: 12px 0;
            letter-spacing: 2px;
        }}
        .btn {{
            background: #2563eb;
            color: white;
            border: none;
            padding: 10px 16px;
            margin: 4px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            font-size: 0.9rem;
        }}
        .btn:hover {{ background: #1d4ed8; }}
        .btn-secondary {{ background: #475569; }}
        .btn-secondary:hover {{ background: #334155; }}
        .slider-row {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 12px 0;
            font-size: 0.9rem;
        }}
        input[type=range] {{
            width: 55%;
            accent-color: #38bdf8;
        }}
        .breath-circle {{
            width: 110px;
            height: 110px;
            margin: 14px auto;
            border-radius: 50%;
            background: radial-gradient(circle, #38bdf8 0%, #2563eb 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 0.95rem;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.4);
            animation: breathe 19s infinite ease-in-out;
        }}
        @keyframes breathe {{
            0%   {{ transform: scale(0.85); background: #2563eb; }}
            21%  {{ transform: scale(1.28); background: #38bdf8; }} /* 4초 들숨 */
            58%  {{ transform: scale(1.28); background: #818cf8; }} /* 7초 멈춤 */
            100% {{ transform: scale(0.85); background: #2563eb; }} /* 8초 날숨 */
        }}
    </style>
    </head>
    <body>
    <div class="studio-grid">
        <!-- 1. 적응형 뽀모도로 타이머 -->
        <div class="panel">
            <h3 style="margin-top:0;">⏱️ 스마트 뽀모도로 타이머</h3>
            <div id="modeLabel" style="color:#94a3b8; font-size:0.85rem;">현재 설정: 집중 {default_focus}분 / 휴식 {default_break}분</div>
            <div class="timer-display" id="timerDisplay">{default_focus:02d}:00</div>
            <div>
                <button class="btn" onclick="startTimer()">▶ 시작</button>
                <button class="btn btn-secondary" onclick="pauseTimer()">⏸ 일시정지</button>
                <button class="btn btn-secondary" onclick="resetTimer({default_focus})">↺ 리셋</button>
            </div>
            <div style="margin-top: 10px;">
                <button class="btn btn-secondary" style="font-size:0.78rem;" onclick="resetTimer(25)">25분 회복</button>
                <button class="btn btn-secondary" style="font-size:0.78rem;" onclick="resetTimer(50)">50분 딥워크</button>
                <button class="btn btn-secondary" style="font-size:0.78rem;" onclick="resetTimer(5)">5분 휴식</button>
            </div>
        </div>

        <!-- 2. Web Audio API 뇌파 & 백색소음 합성 믹서 -->
        <div class="panel">
            <h3 style="margin-top:0;">🎚️ 뇌파 & 백색소음 사운드 믹서</h3>
            <p style="color:#94a3b8; font-size:0.8rem; margin-bottom:10px;">외부 음원 없이 브라우저 오디오 엔진으로 즉시 생성됩니다.</p>
            <button class="btn" id="audioToggleBtn" onclick="toggleAudio()">🔊 사운드 믹서 켜기</button>
            <div class="slider-row">
                <span>🌧️ 빗소리 (Pink Noise)</span>
                <input type="range" id="rainVol" min="0" max="100" value="40" oninput="updateVolumes()">
            </div>
            <div class="slider-row">
                <span>🔥 장작불/도서관 (Brown)</span>
                <input type="range" id="fireVol" min="0" max="100" value="30" oninput="updateVolumes()">
            </div>
            <div class="slider-row">
                <span>🧠 알파파 집중음 (Binaural)</span>
                <input type="range" id="alphaVol" min="0" max="100" value="20" oninput="updateVolumes()">
            </div>
        </div>

        <!-- 3. 4-7-8 브레인 리프레시 복식호흡 가이드 -->
        <div class="panel">
            <h3 style="margin-top:0;">🧘 4-7-8 뇌 피로 회복 호흡</h3>
            <p style="color:#94a3b8; font-size:0.8rem;">쉬는 시간 쇼츠 대신 원의 크기에 맞춰 호흡해 보세요.</p>
            <div class="breath-circle" id="breathText">들이쉬기 (4초)</div>
            <div style="color:#cbd5e1; font-size:0.82rem;">4초 들숨 → 7초 멈춤 → 8초 날숨 (부교감신경 활성화)</div>
        </div>
    </div>

    <script>
        // 타이머 로직
        let totalSeconds = {default_focus} * 60;
        let timerInterval = null;

        function updateDisplay() {{
            const m = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
            const s = String(totalSeconds % 60).padStart(2, '0');
            document.getElementById('timerDisplay').innerText = m + ':' + s;
        }}

        function startTimer() {{
            if (timerInterval) return;
            timerInterval = setInterval(() => {{
                if (totalSeconds > 0) {{
                    totalSeconds--;
                    updateDisplay();
                }} else {{
                    clearInterval(timerInterval);
                    timerInterval = null;
                    alert('🎉 목표 집중 시간이 끝났습니다! 5분간 눈을 감고 호흡 가이드를 따라 휴식하세요.');
                }}
            }}, 1000);
        }}

        function pauseTimer() {{
            clearInterval(timerInterval);
            timerInterval = null;
        }}

        function resetTimer(minutes) {{
            pauseTimer();
            totalSeconds = minutes * 60;
            document.getElementById('modeLabel').innerText = '현재 설정: ' + minutes + '분 타이머';
            updateDisplay();
        }}

        // 4-7-8 호흡 텍스트 동기화
        setInterval(() => {{
            const t = (Date.now() / 1000) % 19;
            const el = document.getElementById('breathText');
            if (t < 4) el.innerText = '들이쉬기 (4초)';
            else if (t < 11) el.innerText = '숨 참기 (7초)';
            else el.innerText = '내쉬기 (8초)';
        }}, 500);

        // Web Audio API 백색소음 합성기
        let audioCtx = null;
        let isPlaying = false;
        let rainGain, fireGain, alphaGain;

        function initAudio() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const bufferSize = 2 * audioCtx.sampleRate;

            // Pink Noise (빗소리 느낌)
            const pinkBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
            const pinkOut = pinkBuffer.getChannelData(0);
            let b0=0, b1=0, b2=0, b3=0, b4=0, b5=0, b6=0;
            for (let i = 0; i < bufferSize; i++) {{
                let white = Math.random() * 2 - 1;
                b0 = 0.99886 * b0 + white * 0.0555179;
                b1 = 0.99332 * b1 + white * 0.0750759;
                b2 = 0.96900 * b2 + white * 0.1538520;
                b3 = 0.86650 * b3 + white * 0.3104856;
                b4 = 0.55000 * b4 + white * 0.5329522;
                b5 = -0.7616 * b5 - white * 0.0168980;
                pinkOut[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.04;
                b6 = white * 0.115926;
            }}
            const pinkNode = audioCtx.createBufferSource();
            pinkNode.buffer = pinkBuffer;
            pinkNode.loop = true;
            rainGain = audioCtx.createGain();
            pinkNode.connect(rainGain).connect(audioCtx.destination);
            pinkNode.start();

            // Brown Noise (따뜻한 장작불/도서관 저음)
            const brownBuffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
            const brownOut = brownBuffer.getChannelData(0);
            let lastOut = 0.0;
            for (let i = 0; i < bufferSize; i++) {{
                let white = Math.random() * 2 - 1;
                brownOut[i] = (lastOut + (0.02 * white)) / 1.02;
                lastOut = brownOut[i];
                brownOut[i] *= 0.15;
            }}
            const brownNode = audioCtx.createBufferSource();
            brownNode.buffer = brownBuffer;
            brownNode.loop = true;
            fireGain = audioCtx.createGain();
            brownNode.connect(fireGain).connect(audioCtx.destination);
            brownNode.start();

            // 알파파 유도 사인파 (200Hz 부드러운 앰비언트 톤)
            const osc = audioCtx.createOscillator();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(210, audioCtx.currentTime);
            alphaGain = audioCtx.createGain();
            osc.connect(alphaGain).connect(audioCtx.destination);
            osc.start();

            updateVolumes();
        }}

        function toggleAudio() {{
            const btn = document.getElementById('audioToggleBtn');
            if (!audioCtx) {{
                initAudio();
                isPlaying = true;
                btn.innerText = '🔇 사운드 믹서 끄기';
                btn.style.background = '#dc2626';
            }} else if (isPlaying) {{
                audioCtx.suspend();
                isPlaying = false;
                btn.innerText = '🔊 사운드 믹서 켜기';
                btn.style.background = '#2563eb';
            }} else {{
                audioCtx.resume();
                isPlaying = true;
                btn.innerText = '🔇 사운드 믹서 끄기';
                btn.style.background = '#dc2626';
            }}
        }}

        function updateVolumes() {{
            if (!audioCtx) return;
            rainGain.gain.value = (document.getElementById('rainVol').value / 100) * 0.5;
            fireGain.gain.value = (document.getElementById('fireVol').value / 100) * 0.6;
            alphaGain.gain.value = (document.getElementById('alphaVol').value / 100) * 0.08;
        }}
    </script>
    </body>
    </html>
    """
    components.html(studio_html, height=340)

# ------------------------------------------
# TAB 4: 번아웃 레이더 & 주간 리포트 (Burnout Guard)
# ------------------------------------------
with tab4:
    st.subheader("📊 번아웃 레이더 & 주간 학습 밸런스 리포트")
    st.write("하루 공부가 끝난 뒤 3초 컨디션 체크인을 남기면, **5각 밸런스 레이더 차트**와 **번아웃 조기 경보 시스템**이 작동합니다.")

    # 번아웃 지수 계산
    burnout_score = min(100, int(sleep_debt * 5.5 + (total_caffeine_today / 4.0) + current_fatigue * 0.4))

    if burnout_score >= 70:
        st.error(
            f"🚨 **번아웃 위험 경보 발령 (현재 번아웃 위험도: {burnout_score}점 / 100점)**\n\n"
            "수면 부족과 카페인 의존도, 주관적 피로도가 위험 수위에 도달했습니다! "
            "오늘 밤은 과감히 추가 공부를 멈추고 최소 7시간 이상 숙면을 취하는 것이 내일 시험 성적을 올리는 가장 확실한 방법입니다."
        )
        if st.button("🌿 내일 일정 30% 감축 '디톡스 데이(Detox Day)' 모드 발동", type="primary"):
            st.session_state.detox_active = True
            st.toast("디톡스 데이 모드가 켜졌습니다! 플래너에서 무리한 고집중 일정을 조절합니다.", icon="🌿")
    elif burnout_score >= 45:
        st.warning(f"⚠️ **번아웃 주의 단계 (현재 번아웃 위험도: {burnout_score}점 / 100점)**: 오후 늦은 카페인을 줄이고 쉬는 시간 스트레칭을 꼭 실천해 주세요.")
    else:
        st.success(f"✅ **건강한 학습 러닝메이트 상태 (현재 번아웃 위험도: {burnout_score}점 / 100점)**: 수면과 집중 효율이 이상적인 균형을 유지하고 있습니다!")

    r_col1, r_col2 = st.columns([1.1, 1.9])

    with r_col1:
        st.markdown("#### 📝 오늘의 3초 컨디션 체크인")
        with st.form("daily_checkin_form"):
            day_label = st.selectbox("기록할 요일", ["월", "화", "수", "목", "금", "토", "일"], index=6)
            mood_sel = st.selectbox("오늘 공부를 마친 기분", ["🤩 최고", "🙂 평온", "😐 보통", "😫 피곤", "😰 불안"])
            focus_input = st.slider("오늘 체감 순공 몰입도 (%)", 20, 100, 80, 5)
            save_checkin = st.form_submit_button("💾 주간 리포트에 업데이트", use_container_width=True)
            if save_checkin:
                for row in st.session_state.weekly_logs:
                    if row["day"] == day_label:
                        row["sleep"] = sleep_today
                        row["caffeine"] = total_caffeine_today
                        row["stress"] = current_fatigue
                        row["focus_rate"] = focus_input
                        row["mood"] = mood_sel
                st.toast(f"{day_label}요일 컨디션 기록이 리포트에 반영되었습니다!", icon="📊")
                st.rerun()

        # 5대 학습 헬스케어 지표 레이더 차트
        done_cnt = sum(1 for t in st.session_state.tasks if t["done"])
        total_cnt = max(1, len(st.session_state.tasks))
        goal_rate = int((done_cnt / total_cnt) * 100)
        sleep_score = int(max(20, min(100, 100 - sleep_debt * 8)))
        caf_control_score = int(max(15, min(100, 100 - max(0, total_caffeine_today - 100) * 0.35)))
        mental_recovery = int(max(20, 100 - current_fatigue))
        focus_efficiency = int(np.mean([x["focus_rate"] for x in st.session_state.weekly_logs]))

        radar_categories = ["수면 규칙성", "카페인 절제력", "계획 달성률", "멘탈 회복력", "순공 몰입 효율"]
        radar_values = [sleep_score, caf_control_score, goal_rate, mental_recovery, focus_efficiency]

        fig_radar = go.Figure(data=go.Scatterpolar(
            r=radar_values + [radar_values[0]],
            theta=radar_categories + [radar_categories[0]],
            fill="toself",
            fillcolor="rgba(37, 99, 235, 0.25)",
            line=dict(color="#2563eb", width=2.5)
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            title="나의 5각 학습-건강 밸런스 지수",
            height=340,
            margin=dict(l=35, r=35, t=50, b=25)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with r_col2:
        st.markdown("#### 📈 주간 수면·스트레스 vs 순공 몰입도 상관관계 분석")
        w_df = pd.DataFrame(st.session_state.weekly_logs)

        fig_week = go.Figure()
        fig_week.add_trace(go.Bar(
            x=w_df["day"],
            y=w_df["caffeine"],
            name="일일 카페인 섭취량 (mg)",
            marker_color="rgba(239, 68, 68, 0.55)",
            yaxis="y2"
        ))
        fig_week.add_trace(go.Scatter(
            x=w_df["day"],
            y=w_df["focus_rate"],
            name="순공 몰입 효율 (%)",
            mode="lines+markers",
            line=dict(color="#10b981", width=3.5)
        ))
        fig_week.add_trace(go.Scatter(
            x=w_df["day"],
            y=w_df["stress"],
            name="스트레스·피로 지수 (%)",
            mode="lines+markers",
            line=dict(color="#f59e0b", width=2.5, dash="dash")
        ))
        fig_week.update_layout(
            title="요일별 카페인·피로도와 실제 학습 몰입 효율(%) 추이",
            yaxis=dict(title="점수 / 비율 (%)", range=[0, 105]),
            yaxis2=dict(title="카페인 (mg)", overlaying="y", side="right", range=[0, 400]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=380,
            margin=dict(l=20, r=20, t=60, b=20),
            hovermode="x unified"
        )
        st.plotly_chart(fig_week, use_container_width=True)

        st.dataframe(
            w_df.rename(columns={
                "day": "요일", "sleep": "수면(h)", "caffeine": "카페인(mg)",
                "stress": "피로도(%)", "focus_rate": "순공효율(%)", "mood": "감정상태"
            }),
            use_container_width=True,
            hide_index=True
        )

# ------------------------------------------
# TAB 5: 수행평가 채점 기준 완벽 대응 (가치 분석 & Pitch Deck)
# ------------------------------------------
with tab5:
    st.subheader("🎤 소프트웨어 가치 분석 및 Pitch Deck 핵심 요약")
    st.write("발표(10분) 및 교사·동료 평가 시 바로 띄워놓고 설명할 수 있는 **비즈니스 피치덱 & 긍정/부정적 가치 분석** 요약 보드입니다.")

    v_col1, v_col2 = st.columns(2)
    with v_col1:
        st.markdown("""
        <div class="metric-card">
            <h4>✅ 긍정적 기능적 가치 (Positive Impact)</h4>
            <ul>
                <li><b>청소년 수면 건강권 및 카페인 오남용 예방</b>: 막연한 경고 대신 '체내 반감기 수식과 숙면 가능 시각'을 눈으로 확인시켜 자기조절 능력을 길러줍니다.</li>
                <li><b>메타인지 기반 학습 효율 극대화</b>: '무작정 오래 앉아 있기' 경쟁에서 벗어나, 내 뇌 각성도가 가장 높은 골든타임에 고난도 과목을 배치하여 공부의 질(Quality)을 높입니다.</li>
                <li><b>지속 가능한 학습 (번아웃 예방)</b>: 피로도와 감정 데이터를 누적 관리하여 시험 기간 정서적 탈진을 조기에 방어합니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with v_col2:
        st.markdown("""
        <div class="metric-card">
            <h4>⚖️ 부정적 기능적 가치 및 한계점 (Negative Impact & 객관적 성찰)</h4>
            <ul>
                <li><b>데이터 강박증 (Quantified-Self 피로감) 우려</b>: 자신의 모든 컨디션을 수치와 그래프로만 판단하려다, 각성도 점수가 낮게 나오면 아예 공부를 포기해 버리는 <b>'노시보 효과(Nocebo Effect)'</b>가 발생할 수 있습니다.</li>
                <li><b>생물학적 개인차의 한계</b>: 카페인 분해 효소(CYP1A2 유전자)나 적정 수면 시간은 개인마다 다른데 표준 공식만 적용하면 체감과 오차가 생길 수 있습니다.<br>
                👉 <i><b>기술적 보완책</b>: 좌측 사이드바에 <b>'카페인 대사 민감도(둔감/보통/민감 3단계)'</b> 보정 옵션을 구현하여 개인차 오차를 최소화했습니다.</i></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 🚀 Pitch Deck 핵심 구조 (Airbnb 피치덱 벤치마킹)")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.info("**1. 문제 정의 (Problem)**\n\n기존 스터디 앱은 '순공 시간 경쟁'만 부추겨 학생들의 고카페인 의존과 만성 수면 부족, 가짜 공부(번아웃)를 유발함.")
    with p2:
        st.success("**2. 해결책 & 차별성 (Solution)**\n\n`생체리듬 진단 → 에너지 맞춤 타임블록 → 적응형 타이머 → 번아웃 가드`가 하나로 연결된 국내 최초 바이오리듬 학습 OS.")
    with p3:
        st.warning("**3. 시장 검증 & 규모 (Market)**\n\n전국 중고생·수험생·대학생 약 450만 명 타깃. 에듀테크(스터디 플래너) 시장과 디지털 헬스케어(수면·멘탈케어) 시장의 교집합 선점.")
    with p4:
        st.error("**4. 수익 모델 & 투자 (BM & Ask)**\n\n• 기본 기능 무료 (Freemium)\n• 고교/교육청 단체 웰니스 라이선스(B2B2G)\n• 디카페인·수면케어 브랜드 제휴 커머스 수수료")
