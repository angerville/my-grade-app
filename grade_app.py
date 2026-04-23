import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 페이지 설정
st.set_page_config(page_title="초등 성적 관리 매니저", layout="wide", page_icon="📝")

# 저장용 파일 이름
DB_FILE = "grade_db.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except Exception:
            return None
    return None

def save_data(df):
    df = df.sort_values(by=['학생명', '과목', '시험명'])
    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
    return df

if 'data' not in st.session_state:
    st.session_state.data = load_data()

# --- 1. 초기 설정 또는 데이터 부재 시 ---
if st.session_state.data is None:
    st.title("🌱 성적 관리 시스템 초기 설정")
    st.info("과목별로 평가 계획을 입력해 주세요. 나중에 사이드바에서 수정할 수 있습니다.")
    
    student_input = st.text_area("1. 학생 이름을 입력하세요 (쉼표 또는 줄바꿈으로 구분)", "학생1, 학생2, 학생3")
    
    st.markdown("---")
    st.subheader("2. 과목별 시험명 설정")
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        kor_tests = st.text_area("국어 시험명", "1단원, 2단원", key="kor")
    with col2:
        mat_tests = st.text_area("수학 시험명", "1단원, 단원평가", key="mat")
    with col3:
        soc_tests = st.text_area("사회 시험명", "1단원", key="soc")
    with col4:
        sci_tests = st.text_area("과학 시험명", "실험관찰", key="sci")

    if st.button("🚀 시스템 시작하기"):
        student_list = [s.strip() for s in student_input.replace('\n', ',').split(',') if s.strip()]
        test_config = {
            "국어": [t.strip() for t in kor_tests.replace('\n', ',').split(',') if t.strip()],
            "수학": [t.strip() for t in mat_tests.replace('\n', ',').split(',') if t.strip()],
            "사회": [t.strip() for t in soc_tests.replace('\n', ',').split(',') if t.strip()],
            "과학": [t.strip() for t in sci_tests.replace('\n', ',').split(',') if t.strip()]
        }
        
        rows = []
        for student in student_list:
            for sub, tests in test_config.items():
                for test in tests:
                    rows.append({
                        "학생명": student, "과목": sub, "시험명": test, 
                        "전체문항": 20, "맞은개수": 0, "정답률": 0.0, "백분위": 0.0
                    })
        
        new_df = pd.DataFrame(rows)
        st.session_state.data = save_data(new_df)
        st.rerun()
    st.stop()

# --- 2. 메인 화면 ---
st.title("📝 학생 성적 및 성취도 관리")

# 데이터 필터링 및 에디터
tabs = st.tabs(["국어", "수학", "사회", "과학"])
subjects = ["국어", "수학", "사회", "과학"]

for i, sub_name in enumerate(subjects):
    with tabs[i]:
        st.subheader(f"📍 {sub_name} 성적 기록")
        # 해당 과목 데이터만 추출
        sub_df = st.session_state.data[st.session_state.data['과목'] == sub_name].copy()
        
        if sub_df.empty:
            st.warning(f"{sub_name} 과목에 설정된 시험이 없습니다.")
            continue

        edited_sub_df = st.data_editor(
            sub_df, 
            key=f"editor_{sub_name}", 
            use_container_width=True,
            column_config={
                "학생명": st.column_config.TextColumn(disabled=True),
                "과목": st.column_config.TextColumn(disabled=True),
                "시험명": st.column_config.TextColumn(disabled=True),
                "전체문항": st.column_config.NumberColumn(min_value=1),
                "맞은개수": st.column_config.NumberColumn(min_value=0),
                "정답률": st.column_config.NumberColumn(format="%.1f%%", disabled=True),
                "백분위": st.column_config.NumberColumn(format="%.1f", disabled=True)
            }
        )
        
        if st.button(f"{sub_name} 데이터 저장 및 분석 반영", key=f"btn_{sub_name}"):
            # 원본 데이터 업데이트
            main_df = st.session_state.data.copy()
            for _, row in edited_sub_df.iterrows():
                idx = (main_df['학생명'] == row['학생명']) & (main_df['과목'] == sub_name) & (main_df['시험명'] == row['시험명'])
                main_df.loc[idx, '전체문항'] = row['전체문항']
                main_df.loc[idx, '맞은개수'] = row['맞은개수']
            
            # 정답률 계산
            main_df['정답률'] = (main_df['맞은개수'] / main_df['전체문항']).fillna(0) * 100
            
            # 백분위 계산 로직 개선
            def calculate_percentile(group):
                if len(group) <= 1:
                    group['백분위'] = 100.0
                else:
                    ranks = group['정답률'].rank(method='average', ascending=True)
                    group['백분위'] = (ranks - 0.5) / len(group) * 100
                return group

            analyzed_df = main_df.groupby(['과목', '시험명'], group_keys=False).apply(calculate_percentile)
            st.session_state.data = save_data(analyzed_df)
            st.success(f"{sub_name} 데이터가 성공적으로 분석되었습니다!")
            st.rerun()

# --- 3. 그래프 분석 ---
st.markdown("---")
st.header("📈 개별 학생 성취도 변화")

if st.session_state.data is not None and not st.session_state.data.empty:
    all_students = sorted(st.session_state.data['학생명'].unique())
    target_student = st.selectbox("학생을 선택하세요", all_students)

    student_plot_df = st.session_state.data[st.session_state.data['학생명'] == target_student].copy()
    
    if not student_plot_df.empty:
        fig = px.line(
            student_plot_df, 
            x='시험명', 
            y='백분위', 
            color='과목', 
            markers=True,
            title=f"{target_student} 학생의 과목별 성취도(백분위) 추이",
            range_y=[0, 105],
            template="plotly_white",
            labels={'백분위': '백분위 (높을수록 우수)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("선택한 학생의 데이터가 없습니다.")

with st.sidebar:
    st.header("⚙️ 관리 도구")
    if st.button("🚨 전체 데이터 초기화"):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        st.session_state.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption("v2.0 - Gemini CLI 자동 업데이트 적용됨")
