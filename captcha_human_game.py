import random
import streamlit as st

st.set_page_config(
    page_title="I'm Not A Robot — CAPTCHA Game",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp {
    background:
      radial-gradient(circle at 15% 10%, rgba(43,103,255,.18), transparent 32%),
      radial-gradient(circle at 90% 90%, rgba(0,224,190,.12), transparent 30%),
      #080d18;
    color: #eef3ff;
}
.block-container { max-width: 760px; padding-top: 1.4rem; padding-bottom: 3rem; }
#MainMenu, footer, header { visibility: hidden; }
.hero {
    border: 1px solid rgba(125,153,205,.25);
    border-radius: 22px;
    padding: 22px;
    background: linear-gradient(135deg, rgba(21,32,55,.96), rgba(12,20,37,.92));
    box-shadow: 0 18px 60px rgba(0,0,0,.25);
    margin-bottom: 18px;
}
.eyebrow { color:#6ee7d8; font-size:.76rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
h1 { color:#f5f7ff; font-size:clamp(1.8rem, 6vw, 2.8rem)!important; line-height:1.08!important; margin:.45rem 0!important; }
.sub { color:#aebbd2; line-height:1.6; }
.panel {
    border:1px solid rgba(125,153,205,.24);
    background:rgba(15,23,41,.94);
    border-radius:18px;
    padding:18px;
    margin:12px 0;
}
.progressline { height:7px; border-radius:20px; background:#202b41; overflow:hidden; margin:10px 0 16px; }
.progressfill { height:100%; border-radius:20px; background:linear-gradient(90deg,#3b82f6,#5eead4); }
.small { color:#8fa0bb; font-size:.86rem; }
div.stButton > button {
    width:100%; min-height:54px; border-radius:12px;
    border:1px solid #33435f; background:#17233a; color:#edf4ff;
    font-weight:700; transition:all .15s ease;
}
div.stButton > button:hover { border-color:#60a5fa; color:#fff; background:#223451; }
div.stButton > button[kind="primary"] { background:linear-gradient(135deg,#2563eb,#0d9488); border:0; }
div[data-testid="stMetric"] {
    background:#111b2d; padding:12px 14px; border:1px solid #283650; border-radius:14px;
}
div[data-testid="stMetricLabel"] { color:#91a4c3; }
div[data-testid="stMetricValue"] { color:#f2f7ff; }
div[data-testid="stAlert"] { border-radius:12px; }
hr { border-color:#25324a; }
@media(max-width:600px) {
  .block-container { padding-left: .8rem; padding-right: .8rem; }
  .hero { padding:18px; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Game data ----------
PUZZLES = [
    {
        "title": "Chọn tất cả ô có đèn giao thông",
        "hint": "Hãy chọn những ô có đèn giao thông. Chọn xong nhấn XÁC MINH.",
        "tiles": ["🚦", "🚗", "🚦", "🛵", "🏙️", "🚦", "🚲", "🚕", "🚦"],
        "correct": [0, 2, 5, 8],
        "type": "tiles",
    },
    {
        "title": "Chọn tất cả ô có xe buýt",
        "hint": "Cẩn thận nhé, có vài hình khá giống nhau!",
        "tiles": ["🚐", "🚌", "🚕", "🚍", "🚎", "🚗", "🚌", "🚚", "🚙"],
        "correct": [1, 3, 6],
        "type": "tiles",
    },
    {
        "title": "Thử thách phép tính",
        "hint": "Trả lời đúng để chứng minh bạn không phải robot.",
        "question": "Nếu có 3 robot, mỗi robot có 4 pin, tổng cộng có bao nhiêu viên pin?",
        "options": ["7", "12", "9", "16"],
        "answer": "12",
        "type": "quiz",
    },
    {
        "title": "Kiểm tra phản xạ của con người",
        "hint": "Chọn biểu tượng KHÁC với các biểu tượng còn lại.",
        "tiles": ["🔒", "🔒", "🔒", "🔓", "🔒", "🔒", "🔒", "🔒", "🔒"],
        "correct": [3],
        "type": "tiles",
    },
    {
        "title": "Câu hỏi cuối cùng",
        "hint": "Một robot đang đứng trước 2 cánh cửa. Một cửa dẫn đến tự do, cửa còn lại dẫn về màn đầu. Bạn có thể chọn cửa nào?",
        "options": ["Cửa trái 🚪", "Cửa phải 🚪", "Cả hai đều có thể", "Không chọn cửa nào"],
        "answer": "Cả hai đều có thể",
        "type": "quiz",
    },
]

def reset_game():
    st.session_state.level = 0
    st.session_state.score = 0
    st.session_state.selected = set()
    st.session_state.feedback = None
    st.session_state.started = False
    st.session_state.finished = False

if "level" not in st.session_state:
    reset_game()

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="eyebrow">CAPTCHA CHALLENGE · HUMAN TEST</div>
  <h1>I'm Not A Robot<span style="color:#5eead4">.</span></h1>
  <div class="sub">Bạn có đủ tỉnh táo để vượt qua hệ thống xác minh không?<br>Hoàn thành mọi thử thách để mở khóa danh hiệu <b>HUMAN VERIFIED</b>.</div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.started and not st.session_state.finished:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### 🤖 Hệ thống đang chờ bạn")
    st.write("5 thử thách • CAPTCHA hình ảnh • Câu đố logic • Màn xác minh cuối")
    st.write("**Luật chơi:** chọn đúng, tránh chọn nhầm. Mỗi màn vượt qua được cộng 100 điểm.")
    if st.button("▶ BẮT ĐẦU XÁC MINH", type="primary", use_container_width=True):
        st.session_state.started = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("Fan-made mini game • Không phải hệ thống CAPTCHA thật")
    st.stop()

if st.session_state.finished:
    st.markdown('<div class="panel" style="text-align:center">', unsafe_allow_html=True)
    st.markdown("## ✅ HUMAN VERIFIED")
    st.markdown("# 🎉 Bạn đã vượt qua!")
    st.write(f"Điểm cuối cùng: **{st.session_state.score} / {len(PUZZLES)*100}**")
    st.write("Hệ thống đã xác nhận: có vẻ bạn là con người… hoặc một robot cực kỳ thông minh 🤨")
    if st.button("↻ CHƠI LẠI", type="primary", use_container_width=True):
        reset_game()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

level = st.session_state.level
puzzle = PUZZLES[level]
progress = int(level / len(PUZZLES) * 100)

m1, m2, m3 = st.columns(3)
m1.metric("MÀN", f"{level + 1}/{len(PUZZLES)}")
m2.metric("ĐIỂM", st.session_state.score)
m3.metric("TRẠNG THÁI", "ĐANG TEST")
st.markdown(f'<div class="progressline"><div class="progressfill" style="width:{progress}%"></div></div>', unsafe_allow_html=True)

st.markdown('<div class="panel">', unsafe_allow_html=True)
st.markdown(f"### 🔐 Thử thách {level + 1}: {puzzle['title']}")
st.write(puzzle["hint"])

if puzzle["type"] == "tiles":
    st.info("Nhấn vào các ô để chọn hoặc bỏ chọn.")
    for row in range(3):
        cols = st.columns(3, gap="small")
        for col in range(3):
            idx = row * 3 + col
            chosen = idx in st.session_state.selected
            label = ("☑ " if chosen else "") + puzzle["tiles"][idx]
            if cols[col].button(label, key=f"tile_{level}_{idx}", use_container_width=True):
                if idx in st.session_state.selected:
                    st.session_state.selected.remove(idx)
                else:
                    st.session_state.selected.add(idx)
                st.rerun()
    st.caption(f"Đã chọn {len(st.session_state.selected)} ô")
    if st.button("XÁC MINH LỰA CHỌN", type="primary", use_container_width=True):
        if st.session_state.selected == set(puzzle["correct"]):
            st.session_state.score += 100
            st.session_state.feedback = "success"
        else:
            st.session_state.feedback = "fail"
else:
    answer = st.radio("Chọn câu trả lời:", puzzle["options"], index=None, key=f"answer_{level}")
    if st.button("GỬI CÂU TRẢ LỜI", type="primary", use_container_width=True):
        if answer == puzzle["answer"]:
            st.session_state.score += 100
            st.session_state.feedback = "success"
        else:
            st.session_state.feedback = "fail"

if st.session_state.feedback == "success":
    st.success("XÁC MINH THÀNH CÔNG! Bạn đã vượt qua thử thách.")
    if st.button("TIẾP TỤC →", type="primary", use_container_width=True):
        st.session_state.level += 1
        st.session_state.selected = set()
        st.session_state.feedback = None
        if st.session_state.level >= len(PUZZLES):
            st.session_state.finished = True
        st.rerun()
elif st.session_state.feedback == "fail":
    st.error("Chưa chính xác! Hãy thử lại, bạn vẫn còn cơ hội.")
    if st.button("THỬ LẠI", use_container_width=True):
        st.session_state.selected = set()
        st.session_state.feedback = None
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    if st.button("⏸ BỎ CUỘC / CHƠI LẠI", use_container_width=True):
        reset_game()
        st.rerun()
with right:
    st.caption("TIP: Đọc kỹ yêu cầu trước khi chọn ô.")
