import streamlit as st
import os

os.makedirs("data", exist_ok=True)
import sqlite3
import pandas as pd
import time

from sql_generator import generate_sql

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NL→SQL Engine",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=Syne:wght@400;600;700;800&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #0b0e14;
    --surface:   #111620;
    --border:    #1e2535;
    --accent:    #00e5a0;
    --accent2:   #4f8bff;
    --muted:     #3d4a63;
    --text:      #c8d6f0;
    --text-dim:  #5a6a85;
    --danger:    #ff5f6d;
    --font-mono: 'IBM Plex Mono', monospace;
    --font-ui:   'Syne', sans-serif;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-ui) !important;
}

/* Ensure content sits above bg effects */
[data-testid="stSidebar"],
.block-container { position: relative; z-index: 1; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Main content padding ── */
.block-container {
    padding: 1.2rem 1.8rem 2rem !important;
    max-width: 100% !important;
}
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
.element-container { margin-bottom: 0.4rem !important; }

/* ── Page header ── */
.nl-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.2rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 1rem;
}
.nl-logo {
    width: 44px; height: 44px;
    background: var(--accent);
    clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
    flex-shrink: 0;
}
.nl-title {
    font-family: var(--font-ui);
    font-size: 1.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    color: #fff;
    margin: 0;
    line-height: 1;
}
.nl-subtitle {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-dim);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 3px;
}

/* ── Section label ── */
.section-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-top: 1rem;
    margin-bottom: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    background: var(--accent);
    clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    border: 1.5px dashed var(--border) !important;
    border-radius: 10px !important;
    background: var(--surface) !important;
    padding: 0.5rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploaderDropzone"] > div {
    color: var(--text-dim) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
}

/* ── Text input ── */
[data-testid="stTextInput"] input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.9rem !important;
    padding: 0.7rem 1rem !important;
    caret-color: var(--accent) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0, 229, 160, 0.12) !important;
    outline: none !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--muted) !important; }

/* ── Primary button ── */
[data-testid="stButton"] > button {
    background: var(--accent) !important;
    color: #000 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.5rem !important;
    cursor: pointer !important;
    transition: opacity 0.15s, transform 0.1s !important;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active { transform: translateY(0) !important; }

/* ── SQL result box ── */
.sql-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-top: 1.2rem;
    position: relative;
}
.sql-card-label {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.6rem;
}
.sql-card pre {
    margin: 0;
    font-family: var(--font-mono) !important;
    font-size: 0.88rem !important;
    color: #e2f0ff !important;
    white-space: pre-wrap;
    line-height: 1.7;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
    background: var(--surface) !important;
}
[data-testid="stDataFrame"] th {
    background: #161d2e !important;
    color: var(--accent) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text) !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: rgba(0,229,160,0.04) !important;
}

/* ── Alert / success ── */
[data-testid="stAlert"] {
    background: rgba(0, 229, 160, 0.07) !important;
    border: 1px solid rgba(0, 229, 160, 0.2) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
    color: var(--accent) !important;
}

/* ── Error box ── */
.stException, [data-testid="stException"] {
    background: rgba(255, 95, 109, 0.08) !important;
    border: 1px solid rgba(255, 95, 109, 0.25) !important;
    border-radius: 8px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
    color: var(--danger) !important;
}

/* ── Sidebar history ── */
.hist-item {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 0.8rem;
    margin-bottom: 0.5rem;
    font-family: var(--font-mono);
    font-size: 0.73rem;
    color: var(--text-dim);
    cursor: default;
    transition: border-color 0.15s;
}
.hist-item:hover { border-color: var(--accent); color: var(--text); }
.hist-num {
    color: var(--accent);
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 2px;
}

/* ── Metrics strip ── */
.metrics-row {
    display: flex;
    gap: 1rem;
    margin: 1.2rem 0;
}
.metric-pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.55rem 1rem;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--text-dim);
    display: flex;
    gap: 0.5rem;
    align-items: center;
}
.metric-val { color: var(--accent); font-weight: 600; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Force sidebar visible ── */
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
section[data-testid="stSidebar"] { transform: none !important; min-width: 260px !important; width: 260px !important; }
section[data-testid="stSidebar"][aria-expanded="false"] { margin-left: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--muted); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--accent); }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "table_loaded" not in st.session_state:
    st.session_state.table_loaded = False
if "df_preview" not in st.session_state:
    st.session_state.df_preview = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:0.8rem 0 1.2rem'>
        <div style='font-family:var(--font-mono);font-size:0.6rem;
                    letter-spacing:0.14em;text-transform:uppercase;
                    color:var(--text-dim);margin-bottom:0.8rem'>
            ◆ &nbsp;Query history
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✕  Clear history"):
        st.session_state.history = []
        st.rerun()

    if not st.session_state.history:
        st.markdown("""
        <div style='font-family:var(--font-mono);font-size:0.72rem;
                    color:var(--text-dim);margin-top:1rem'>
            No queries yet.
        </div>
        """, unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(st.session_state.history), 1):
            st.markdown(f"""
            <div class='hist-item'>
                <div class='hist-num'>#{len(st.session_state.history) - i + 1}</div>
                {item['question']}
            </div>
            """, unsafe_allow_html=True)

# ── Main ──────────────────────────────────────────────────────────────────────

# Canvas background via components (scripts work here)
import streamlit.components.v1 as components
components.html("""
<style>
#bgCanvas { position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:0; pointer-events:none; }
</style>
<canvas id='bgCanvas'></canvas>
<script>
(function() {
  var canvas = document.getElementById('bgCanvas');
  // Escape into parent frame
  var topCanvas = window.parent.document.getElementById('bgCanvas');
  if (!topCanvas) {
    topCanvas = window.parent.document.createElement('canvas');
    topCanvas.id = 'bgCanvas';
    topCanvas.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none;';
    window.parent.document.body.appendChild(topCanvas);
  }
  var ctx = topCanvas.getContext('2d');
  var W, H;
  function resize() { W = topCanvas.width = window.parent.innerWidth; H = topCanvas.height = window.parent.innerHeight; }
  resize();
  window.parent.addEventListener('resize', resize);

  var NUM = 80;
  var particles = [];
  for (var i = 0; i < NUM; i++) {
    particles.push({
      x: Math.random() * 1600, y: Math.random() * 900,
      vx: (Math.random()-0.5)*0.5, vy: (Math.random()-0.5)*0.5,
      r: Math.random()*1.8+0.6,
      color: Math.random()>0.5 ? '0,229,160' : '79,139,255',
      alpha: Math.random()*0.5+0.5,
      pulse: Math.random()*Math.PI*2,
      pulseSpeed: Math.random()*0.025+0.008
    });
  }

  var orbs = [
    {x:0.12,y:0.18,r:420,color:'0,229,160',alpha:0.22,phase:0,speed:0.008},
    {x:0.88,y:0.80,r:380,color:'79,139,255',alpha:0.20,phase:2.1,speed:0.006},
    {x:0.62,y:0.05,r:260,color:'0,229,160',alpha:0.13,phase:1.0,speed:0.012},
    {x:0.25,y:0.90,r:220,color:'79,139,255',alpha:0.12,phase:3.5,speed:0.009},
  ];

  var GRID=54, gridOffset=0;
  var t=0;

  function loop() {
    ctx.clearRect(0,0,W,H);
    t++; gridOffset+=0.35;

    // Orbs
    orbs.forEach(function(o) {
      var pulse = Math.sin(t*o.speed+o.phase)*0.3+0.7;
      var g = ctx.createRadialGradient(o.x*W,o.y*H,0,o.x*W,o.y*H,o.r*pulse);
      g.addColorStop(0,'rgba('+o.color+','+(o.alpha*pulse)+')');
      g.addColorStop(0.5,'rgba('+o.color+','+(o.alpha*0.35*pulse)+')');
      g.addColorStop(1,'rgba('+o.color+',0)');
      ctx.fillStyle=g;
      ctx.beginPath(); ctx.arc(o.x*W,o.y*H,o.r*pulse,0,Math.PI*2); ctx.fill();
    });

    // Grid
    var off = gridOffset % GRID;
    ctx.lineWidth=0.5;
    for(var x=off;x<W+GRID;x+=GRID){
      var gx=ctx.createLinearGradient(x,0,x,H);
      gx.addColorStop(0,'rgba(0,229,160,0)'); gx.addColorStop(0.5,'rgba(0,229,160,0.07)'); gx.addColorStop(1,'rgba(0,229,160,0)');
      ctx.strokeStyle=gx; ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
    }
    for(var y=off;y<H+GRID;y+=GRID){
      var gy=ctx.createLinearGradient(0,y,W,y);
      gy.addColorStop(0,'rgba(0,229,160,0)'); gy.addColorStop(0.5,'rgba(0,229,160,0.07)'); gy.addColorStop(1,'rgba(0,229,160,0)');
      ctx.strokeStyle=gy; ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
    }

    // Connections
    for(var i=0;i<particles.length;i++){
      for(var j=i+1;j<particles.length;j++){
        var dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y;
        var dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<130){
          ctx.strokeStyle='rgba(0,229,160,'+(1-dist/130)*0.2+')';
          ctx.lineWidth=0.7;
          ctx.beginPath(); ctx.moveTo(particles[i].x,particles[i].y); ctx.lineTo(particles[j].x,particles[j].y); ctx.stroke();
        }
      }
    }

    // Particles
    particles.forEach(function(p){
      p.x+=p.vx; p.y+=p.vy;
      if(p.x<0)p.x=W; if(p.x>W)p.x=0;
      if(p.y<0)p.y=H; if(p.y>H)p.y=0;
      p.pulse+=p.pulseSpeed;
      var a=p.alpha*(0.7+Math.sin(p.pulse)*0.3);
      var g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r*6);
      g.addColorStop(0,'rgba('+p.color+','+a+')');
      g.addColorStop(0.4,'rgba('+p.color+','+(a*0.35)+')');
      g.addColorStop(1,'rgba('+p.color+',0)');
      ctx.fillStyle=g; ctx.beginPath(); ctx.arc(p.x,p.y,p.r*6,0,Math.PI*2); ctx.fill();
      ctx.fillStyle='rgba('+p.color+','+Math.min(a*2,1)+')';
      ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill();
    });

    requestAnimationFrame(loop);
  }
  loop();
})();
</script>
""", height=0, scrolling=False)

# Header
st.markdown("""
<div class='nl-header'>
    <div class='nl-logo'></div>
    <div>
        <div class='nl-title'>NL → SQL Engine</div>
        <div class='nl-subtitle'>Ask questions in plain English · Get instant SQL results</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Upload section ────────────────────────────────────────────────────────────
st.markdown("<div class='section-label'>Data source</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    import os
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/sample.db")
    df.to_sql("uploaded_data", conn, if_exists="replace", index=False)
    conn.close()

    st.session_state.table_loaded = True
    st.session_state.df_preview = df

    st.success(f"✓  Loaded **{uploaded_file.name}** — {len(df):,} rows · {len(df.columns)} columns")

    # Metrics strip
    cols_str = " · ".join(df.columns.tolist())
    st.markdown(f"""
    <div class='metrics-row'>
        <div class='metric-pill'>Rows <span class='metric-val'>{len(df):,}</span></div>
        <div class='metric-pill'>Columns <span class='metric-val'>{len(df.columns)}</span></div>
        <div class='metric-pill' style='flex:1;min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis'>
            Fields <span class='metric-val' style='margin-left:4px'>{cols_str}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Preview data", expanded=False):
        st.dataframe(df.head(10), use_container_width=True)

# ── Query section ─────────────────────────────────────────────────────────────
st.markdown("<div class='section-label'>Natural language query</div>", unsafe_allow_html=True)

# Ghost-text suggestion injected directly into parent page via st.markdown
# Works because it targets Streamlit's own input in the same DOM
import json
SUGGESTIONS = [
    "Show me all records",
    "Show me the top 5 employees by salary",
    "Show me the average salary by department",
    "Show me the total count of employees",
    "Show me employees in the Engineering department",
    "Show me the highest paid employee",
    "Show me employees with salary greater than 50000",
    "Show me the lowest salary in each department",
    "Show me all departments and their employee count",
    "Show me employees sorted by name alphabetically",
]

col_input, col_btn = st.columns([5, 1], gap="small")
with col_input:
    question = st.text_input("q", key="main_q", label_visibility="collapsed",
                             placeholder="e.g.  Show me the top 5 employees by salary")
with col_btn:
    run = st.button("Run \u2192", use_container_width=True)

# Rotating animated placeholder via CSS keyframes
st.markdown("""
<style>
@keyframes ph1  { 0%,16%{opacity:1} 17%,100%{opacity:0} }
@keyframes ph2  { 0%,16%{opacity:0} 17%,33%{opacity:1} 34%,100%{opacity:0} }
@keyframes ph3  { 0%,33%{opacity:0} 34%,50%{opacity:1} 51%,100%{opacity:0} }
@keyframes ph4  { 0%,50%{opacity:0} 51%,67%{opacity:1} 68%,100%{opacity:0} }
@keyframes ph5  { 0%,67%{opacity:0} 68%,84%{opacity:1} 85%,100%{opacity:0} }
@keyframes ph6  { 0%,84%{opacity:0} 85%,100%{opacity:1} }

.ph-wrap {
    position: relative;
    pointer-events: none;
    height: 0;
    overflow: visible;
}
.ph-line {
    position: absolute;
    bottom: 12px;
    left: 0;
    right: 0;
    padding: 0 1rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.88rem;
    color: rgba(90,106,133,0.55);
    white-space: nowrap;
    overflow: hidden;
    opacity: 0;
    animation-duration: 18s;
    animation-iteration-count: infinite;
    animation-timing-function: ease-in-out;
    pointer-events: none;
    z-index: 100;
}
.ph1 { animation-name: ph1; }
.ph2 { animation-name: ph2; }
.ph3 { animation-name: ph3; }
.ph4 { animation-name: ph4; }
.ph5 { animation-name: ph5; }
.ph6 { animation-name: ph6; }
</style>
<div class="ph-wrap">
  <div class="ph-line ph1">e.g.&nbsp;&nbsp;Show me the top 5 employees by salary</div>
  <div class="ph-line ph2">e.g.&nbsp;&nbsp;Average salary by department</div>
  <div class="ph-line ph3">e.g.&nbsp;&nbsp;Who is the highest paid employee?</div>
  <div class="ph-line ph4">e.g.&nbsp;&nbsp;Count of employees per department</div>
  <div class="ph-line ph5">e.g.&nbsp;&nbsp;Show all Engineering employees</div>
  <div class="ph-line ph6">e.g.&nbsp;&nbsp;Employees earning more than 50000</div>
</div>
""", unsafe_allow_html=True)

# Dropdown suggestion list via selectbox hidden as a hint
if question:
    matches = [s for s in SUGGESTIONS if s.lower().startswith(question.lower())]
    if matches and question.lower() != matches[0].lower():
        rows_html = ""
        for i, m in enumerate(matches[:4]):
            color = "#00e5a0" if i == 0 else "#5a6a85"
            bold_part = "<b style='color:#00e5a0'>" + m[:len(question)] + "</b>"
            rest_part = m[len(question):]
            rows_html += "<div style='padding:0.5rem 1rem;font-size:0.82rem;color:" + color + ";border-bottom:1px solid #1e2535;'>" + bold_part + rest_part + "</div>"
        dropdown_html = "<div style='margin-top:-8px;margin-bottom:4px;background:#111620;border:1px solid #1e2535;border-radius:0 0 8px 8px;font-family:IBM Plex Mono,monospace;overflow:hidden;'>" + rows_html + "</div>"
        st.markdown(dropdown_html, unsafe_allow_html=True)
        st.caption("Suggestion: " + matches[0])



# ── Execution ─────────────────────────────────────────────────────────────────
if run:
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Generating SQL…"):
            t0 = time.time()
            sql_query = generate_sql(question)
            elapsed = time.time() - t0

        st.session_state.history.append({"question": question, "sql": sql_query})

        # SQL card
        st.markdown(f"""
        <div class='sql-card'>
            <div class='sql-card-label'>⬡ &nbsp;Generated SQL &nbsp;·&nbsp; {elapsed:.2f}s</div>
            <pre>{sql_query}</pre>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-label'>Query results</div>", unsafe_allow_html=True)

        conn = sqlite3.connect("data/sample.db")
        try:
            result = pd.read_sql_query(sql_query, conn)
            st.markdown(f"""
            <div style='font-family:var(--font-mono);font-size:0.7rem;
                        color:var(--text-dim);margin-bottom:0.5rem'>
                {len(result):,} row{"s" if len(result) != 1 else ""} returned
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Query error: {e}")
        finally:
            conn.close()