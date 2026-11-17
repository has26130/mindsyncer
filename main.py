import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ==========================================
# 0. 페이지 기본 설정 & 프리미엄 에디토리얼 CSS
# ==========================================
st.set_page_config(
    page_title="mindsyncer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');

    html, body, [class*="css"] {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    }

    /* 미니멀 & 하이엔드 브랜드 헤더 */
    .brand-hero {
        position: relative;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2.2rem 2.6rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 4px 24px -4px rgba(15, 23, 42, 0.04);
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
        overflow: hidden;
    }
    .brand-hero::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #0f172a 0%, #3b82f6 50%, #6366f1 100%);
    }
    .brand-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: #64748b;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        background-color: #3b82f6;
        border-radius: 50%;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.15);
    }
    .brand-title-row {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .brand-logo {
        font-size: 2.55rem;
        font-weight: 300;
        letter-spacing: -0.04em;
        color: #0f172a;
        margin: 0;
        line-height: 1.05;
    }
    .brand-logo strong {
        font-weight: 800;
        background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .brand-logo .dot {
        color: #3b82f6;
        font-weight: 800;
    }
    .brand-tag {
        font-size: 0.78rem;
        font-weight: 500;
        color: #475569;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 6px 14px;
        border-radius: 999px;
        letter-spacing: -0.01em;
    }
    .brand-subtitle {
        margin: 0.15rem 0 0 0;
        font-size: 0.98rem;
        font-weight: 400;
        color: #475569;
        letter-spacing: -0.01em;
        line-height: 1.5;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 1. 세션 상태(Session State) 초기화
# ==========================================
if "caffeine_logs" not in st.session_state:
    st.session_state.caffeine_logs = [
        {"item": "아메리카노 (150mg)", "mg": 150, "hour": 8.5},
        {"item": "에너씨슬 (60mg)", "mg": 60, "hour": 15.5}
    ]

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "title": "수학 미적분 고난도 문항 5제 풀이", "level": "🔥 고집중 (Deep Work)", "hours": 2.0, "done": False},
        {"id": 2, "title": "파이썬 알고리즘 문제 풀이 및 디버깅", "level": "🔥 고집중 (Deep Work)", "hours": 1.5, "done": True},
        {"id": 3, "title": "국어 문학 작품 핵심 노트 정리", "level": "⚡ 중집중 (Flow Work)", "hours": 1.5, "done": False},
        {"id": 4, "title": "영어 단어 Day 15~16 암기", "level": "🌱 저집중 (Light Work)", "hours": 1.0, "done": True},
        {"id": 5, "title": "오답노트 프린트 스크랩 및 파일 정리", "level": "🌱 저집중 (Light Work)", "hours": 1.0, "done": False},
    ]

if "weekly_logs" not in st.session_state:
    st.session_state.weekly_logs = [
        {"day": "월", "sleep": 6.5, "caffeine": 150, "stress": 45, "focus_rate": 82, "mood": "🙂 평온"},
        {"day": "화", "sleep": 5.5, "caffeine": 210, "stress": 65, "focus_rate": 75, "mood": "😐 보통"},
        {"day": "수", "sleep": 4.5, "caffeine": 300, "stress": 82, "focus_rate": 60, "mood": "😫 피곤"},
        {"day": "목", "sleep": 5.0, "caffeine": 250, "stress": 78, "focus_rate": 64, "mood": "😰 불안"},
        {"day": "금", "sleep": 7.0, "caffeine": 100, "stress": 40, "focus_rate": 88, "mood": "🤩 최고"},
        {"day": "토", "sleep": 8.0, "caffeine": 50,  "stress": 30, "focus_rate": 90, "mood": "🙂 평온"},
        {"day": "일", "sleep": 6.0, "caffeine": 210, "stress": 58, "focus_rate": 78, "mood": "😐 보통"},
    ]

if "detox_active" not in st.session_state:
    st.session_state.detox_active = False

# ==========================================
# 2. 핵심 과학 알고리즘 함수 (카페인 반감기 & 뇌 각성도)
# ==========================================
INTAKE_DB = {
    "아메리카노 (150mg)": 150,
    "에너씨슬 (60mg)": 60,
    "고카페인 에너지드링크 (200mg)": 200,
    "몬스터 에너지 (100mg)": 100,
    "핫식스 (60mg)": 60,
    "에너지 젤리 / 부스터 정제 (50mg)": 50,
    "콜라 / 녹차 / 초콜릿 (35mg)": 35,
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
        circadian_wave = 18 * np.sin((h - wake_hour - 1.5) * np.pi / 10.0)
        post_lunch_dip = -14 * np.exp(-((h - 14.0) ** 2) / 1.5)
        homeostatic_fatigue = awake_duration * 2.3

        # 카페인 각성 부스트 (과다 섭취 시 신경과민 역효과 반영)
        if total_caf <= 250:
            caf_boost = min(22.0, total_caf * 0.11)
        else:
            caf_boost = 22.0 - (total_caf - 250) * 0.05

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
            sleep_ready_time = "⚠️ 새벽 04:00 이후 (수면 방해)"
        else:
            sleep_ready_time = f"{int(ready_h % 24):02d}:{int((ready_h % 1) * 60):02d}" + (" (익일 새벽)" if ready_h >= 24 else "")

    return df, round(cumulative_debt, 1), sleep_ready_time

# ==========================================
# 3. 사이드바: 내 생체 데이터 입력 및 상황별 프리셋
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ 바이오 프로필 설정")
    st.caption("수면·카페인 상태에 따라 전체 스케줄과 타이머가 실시간 동기화됩니다.")

    sleep_today = st.slider("🌙 어젯밤 수면 시간 (시간)", 2.0, 10.0, 5.5, 0.5)
    sleep_recent = st.slider("🛌 최근 3일 평균 수면 (시간)", 3.0, 10.0, 6.0, 0.5)
    wake_hour = st.slider("⏰ 오늘 기상 시각 (시)", 5.0, 10.0, 7.0, 0.5)
    sensitivity = st.selectbox(
        "🧬 카페인 대사 민감도",
        list(SENSITIVITY_HALF_LIFE.keys()),
        index=1,
        help="사람마다 다른 카페인 분해 속도를 반영해 오차를 줄입니다."
    )
    current_fatigue = st.slider("🔋 현재 주관적 피로도 (%)", 0, 100, 55, 5)

    st.divider()
    st.markdown("### ⚡ 예시 상황별 프리셋")
    col_preset1, col_preset2 = st.columns(2)
    with col_preset1:
        if st.button("🚨 시험기간 과부하", use_container_width=True):
            st.session_state.caffeine_logs = [
                {"item": "아메리카노 (150mg)", "mg": 150, "hour": 8.0},
                {"item": "에너씨슬 (60mg)", "mg": 60, "hour": 14.0},
                {"item": "고카페인 에너지드링크 (200mg)", "mg": 200, "hour": 20.5},
            ]
            st.toast("시험기간 카페인 과부하 예시가 적용되었습니다!", icon="🚨")
            st.rerun()
    with col_preset2:
        if st.button("🌿 건강한 밸런스", use_container_width=True):
            st.session_state.caffeine_logs = [
                {"item": "에너씨슬 (60mg)", "mg": 60, "hour": 10.0},
                {"item": "디카페인 커피 (10mg)", "mg": 10, "hour": 15.0}
            ]
            st.session_state.detox_active = False
            st.toast("건강한 수면·학습 밸런스 예시가 적용되었습니다!", icon="🌿")
            st.rerun()

# 생체리듬 시뮬레이션 실행
bio_df, sleep_debt, sleep_ready_str = simulate_biorhythm(
    sleep_today, sleep_recent, wake_hour, sensitivity, st.session_state.caffeine_logs
)

total_caffeine_today = sum(x["mg"] for x in st.session_state.caffeine_logs)
peak_row = bio_df.loc[bio_df["뇌 각성도(%)"].idxmax()]
golden_time_str = peak_row["시각"]
max_alertness = peak_row["뇌 각성도(%)"]

# ==========================================
# 4. 상단 헤더 (하이엔드 에디토리얼 스타일 - mindsyncer)
# ==========================================
st.markdown(f"""
<div class="brand-hero">
    <div class="brand-eyebrow">
        <span class="status-dot"></span>
        <span>BIORHYTHM & COGNITIVE PACING ENGINE</span>
    </div>
    <div class="brand-title-row">
        <h1 class="brand-logo">mind<strong>syncer</strong><span class="dot">.</span></h1>
        <span class="brand-tag">Peak Alertness · {golden_time_str} ({max_alertness}%)</span>
    </div>
    <p class="brand-subtitle">
        수면 부채와 카페인 대사 곡선을 정밀하게 추적하여, 당신의 뇌가 가장 깨어 있는 시간에 최적의 몰입을 설계합니다.
    </p>
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
    "⚡ 오늘 총 카페인 섭취량",
    f"{total_caffeine_today} mg",
    delta="일일권장량(150mg) 초과" if total_caffeine_today > 150 else "권장량 이내 안전",
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
# 5. 메인 4대 탭 구성
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🧪 바이오리듬",
    "📅 스마트 플래너",
    "🎧 집중 스튜디오",
    "📊 주간 리포트"
])

# ------------------------------------------
# TAB 1: 바이오리듬
# ------------------------------------------
with tab1:
    st.subheader("🧪 시간대별 카페인 반감기 & 뇌 각성도 분석")
    st.write("섭취한 카페인·에너지 부스터 항목과 시각을 추가하면 반감기 공식($C(t) = C_0 \\times 0.5^{t/h}$)에 따라 체내 분해 곡선과 뇌 집중력 변화가 실시간 계산됩니다.")

    col_left, col_right = st.columns([1.1, 2.2])

    with col_left:
        st.markdown("#### ➕ 카페인·에너지 섭취 추가")
        selected_item = st.selectbox("섭취 항목 선택 (음료·영양제·간식)", list(INTAKE_DB.keys()))
        intake_hour = st.slider("섭취 시각 (24시간 기준)", 6.0, 23.5, 15.0, 0.5, format="%.1f시")

        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("⚡ 항목 추가하기", use_container_width=True, type="primary"):
                st.session_state.caffeine_logs.append({
                    "item": selected_item,
                    "mg": INTAKE_DB[selected_item],
                    "hour": intake_hour
                })
                st.rerun()
        with c_btn2:
            if st.button("🗑️ 기록 전체 초기화", use_container_width=True):
                st.session_state.caffeine_logs = []
                st.rerun()

        st.markdown("#### 📋 오늘 섭취한 항목")
        if st.session_state.caffeine_logs:
            for item_log in st.session_state.caffeine_logs:
                h_int = int(item_log["hour"])
                m_int = int((item_log["hour"] % 1) * 60)
                st.info(f"**{h_int:02d}:{m_int:02d}** — {item_log['item']}")
        else:
            st.success("오늘 섭취한 카페인이 없습니다! 깊고 깨끗한 수면이 기대됩니다.")

        if total_caffeine_today > 200:
            st.error(
                "🚨 **카페인 과다 경보**: 현재 총 섭취량이 200mg을 넘었습니다! "
                "심장 두근거림, 손 떨림 및 야간 수면 구조 파괴(깊은 잠 감소)가 발생할 수 있습니다. "
                "지금부터는 물이나 논카페인 차로 대체하세요."
            )

    with col_right:
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
            name="⚡ 체내 잔여 카페인 (mg)",
            mode="lines",
            line=dict(color="#dc2626", width=3, dash="dot"),
            yaxis="y2"
        ))

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
# TAB 2: 스마트 플래너
# ------------------------------------------
with tab2:
    st.subheader("📅 뇌 에너지 동기화 스마트 플래너")
    st.write("할 일의 **인지 부하(고집중/중집중/저집중)**를 선택하면, 오늘 나의 시간대별 뇌 각성도 곡선에 맞춰 가장 효율적인 시간대에 과목을 자동 배치합니다.")

    available_energy = max(20.0, round(100.0 - sleep_debt * 4.5 - current_fatigue * 0.35, 1))
    if st.session_state.detox_active:
        st.warning("🌿 **디톡스 데이(Detox Day) 모드가 활성화되어 있습니다**: 번아웃 예방을 위해 고집중 학습 권장량이 30% 축소되었습니다.")

    total_planned_hours = sum(t["hours"] for t in st.session_state.tasks if not t["done"])
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
        st.markdown("#### 🤖 바이오리듬 자동 시간대 매칭 결과")
        st.caption("오늘 나의 뇌 각성도가 가장 높은 시간대부터 🔥고집중 → ⚡중집중 → 🌱저집중 순서로 타임블록을 자동 배정합니다.")

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
# TAB 3: 집중 스튜디오
# ------------------------------------------
with tab3:
    st.subheader("🎧 적응형 집중 스튜디오")
    st.write("현재 내 피로도와 수면 부채를 분석하여 **최적의 뽀모도로 집중/휴식 비율**을 자동 세팅하고, 브라우저 내장 **백색소음 사운드 믹서**와 **복식호흡 가이드**를 제공합니다.")

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
        mode_desc = "학습 리듬과 가장 잘 맞는 안정적인 집중·휴식 밸런스 모드입니다."

    st.info(f"**🤖 맞춤 타이머 추천: {rec_mode}**\n\n{mode_desc}")

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
            21%  {{ transform: scale(1.28); background: #38bdf8; }}
            58%  {{ transform: scale(1.28); background: #818cf8; }}
            100% {{ transform: scale(0.85); background: #2563eb; }}
        }}
    </style>
    </head>
    <body>
    <div class="studio-grid">
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

        <div class="panel">
            <h3 style="margin-top:0;">🎚️ 뇌파 & 백색소음 사운드 믹서</h3>
            <p style="color:#94a3b8; font-size:0.8rem; margin-bottom:10px;">브라우저 오디오 엔진으로 즉시 합성되는 집중 사운드입니다.</p>
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

        <div class="panel">
            <h3 style="margin-top:0;">🧘 4-7-8 뇌 피로 회복 호흡</h3>
            <p style="color:#94a3b8; font-size:0.8rem;">쉬는 시간 스마트폰 대신 원의 크기에 맞춰 호흡해 보세요.</p>
            <div class="breath-circle" id="breathText">들이쉬기 (4초)</div>
            <div style="color:#cbd5e1; font-size:0.82rem;">4초 들숨 → 7초 멈춤 → 8초 날숨 (부교감신경 활성화)</div>
        </div>
    </div>

    <script>
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

        setInterval(() => {{
            const t = (Date.now() / 1000) % 19;
            const el = document.getElementById('breathText');
            if (t < 4) el.innerText = '들이쉬기 (4초)';
            else if (t < 11) el.innerText = '숨 참기 (7초)';
            else el.innerText = '내쉬기 (8초)';
        }}, 500);

        let audioCtx = null;
        let isPlaying = false;
        let rainGain, fireGain, alphaGain;

        function initAudio() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const bufferSize = 2 * audioCtx.sampleRate;

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
# TAB 4: 주간 리포트
# ------------------------------------------
with tab4:
    st.subheader("📊 번아웃 레이더 & 주간 학습 밸런스 리포트")
    st.write("하루 공부가 끝난 뒤 3초 컨디션 체크인을 남기면, **5각 밸런스 레이더 차트**와 **번아웃 조기 경보 시스템**이 작동합니다.")

    burnout_score = min(100, int(sleep_debt * 5.5 + (total_caffeine_today / 4.0) + current_fatigue * 0.4))

    if burnout_score >= 70:
        st.error(
            f"🚨 **번아웃 위험 경보 발령 (현재 번아웃 위험도: {burnout_score}점 / 100점)**\n\n"
            "수면 부족과 카페인 의존도, 주관적 피로도가 위험 수위에 도달했습니다! "
            "오늘 밤은 과감히 추가 공부를 멈추고 최소 7시간 이상 숙면을 취하는 것이 내일 집중력을 높이는 가장 확실한 방법입니다."
        )
        if st.button("🌿 내일 일정 30% 감축 '디톡스 데이(Detox Day)' 모드 발동", type="primary"):
            st.session_state.detox_active = True
            st.toast("디톡스 데이 모드가 켜졌습니다! 플래너에서 무리한 고집중 일정을 조절합니다.", icon="🌿")
    elif burnout_score >= 45:
        st.warning(f"⚠️ **번아웃 주의 단계 (현재 번아웃 위험도: {burnout_score}점 / 100점)**: 오후 늦은 카페인을 줄이고 쉬는 시간 스트레칭을 꼭 실천해 주세요.")
    else:
        st.success(f"✅ **건강한 학습 밸런스 상태 (현재 번아웃 위험도: {burnout_score}점 / 100점)**: 수면과 집중 효율이 이상적인 균형을 유지하고 있습니다!")

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
            yaxis2=dict(title="카페인 (mg)", overlaying="y", side="right", range=[0, 450]),
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
