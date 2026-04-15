from flask import Flask, send_file, request
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import qis
import qis3
import threading
import time

q = Flask(__name__)


def run_infinite_logger():
    while True:
        print(f"[Background Log] System active at: {time.ctime()}")
        time.sleep(60)


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QEntangle — Quantum Entanglement Simulator</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #03050f;
            --surface: #080d1e;
            --surface2: #0d1530;
            --border: rgba(100, 180, 255, 0.12);
            --accent: #4af0c8;
            --accent2: #7b6ff7;
            --accent3: #f06aad;
            --text: #e8f0ff;
            --text-muted: #6a7fa8;
            --glow: rgba(74, 240, 200, 0.18);
            --glow2: rgba(123, 111, 247, 0.18);
        }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html { scroll-behavior: smooth; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Space Mono', monospace;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* PRELOADER */
        #preloader {
            position: fixed; inset: 0;
            background: var(--bg);
            z-index: 9999;
            display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 32px;
            transition: opacity 0.7s ease, visibility 0.7s ease;
        }
        #preloader.hidden { opacity: 0; visibility: hidden; pointer-events: none; }
        .preloader-logo {
            font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800;
            letter-spacing: 0.15em; color: var(--accent); text-transform: uppercase;
            animation: pulseText 1.5s ease-in-out infinite;
        }
        .preloader-logo span { color: var(--accent2); }
        @keyframes pulseText { 0%,100%{opacity:1} 50%{opacity:0.35} }
        .orb-wrap { position:relative; width:100px; height:100px; }
        .orb-ring {
            position:absolute; inset:0; border-radius:50%;
            border: 2px solid transparent; animation: spinR 1.2s linear infinite;
        }
        .orb-ring:nth-child(1){ border-top-color:var(--accent); border-right-color:var(--accent); }
        .orb-ring:nth-child(2){ inset:12px; border-bottom-color:var(--accent2); border-left-color:var(--accent2); animation-duration:1.8s; animation-direction:reverse; }
        .orb-ring:nth-child(3){ inset:24px; border-top-color:var(--accent3); animation-duration:2.4s; }
        .orb-core {
            position:absolute; inset:36px; border-radius:50%;
            background:radial-gradient(circle,var(--accent),var(--accent2));
            animation:corePulse 1.5s ease-in-out infinite;
            box-shadow: 0 0 20px var(--accent), 0 0 40px var(--glow);
        }
        @keyframes spinR { to{ transform:rotate(360deg) } }
        @keyframes corePulse { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(0.65);opacity:0.5} }
        .preloader-sub {
            font-size:0.68rem; letter-spacing:0.3em; color:var(--text-muted);
            text-transform:uppercase; animation:blinkT 1s step-end infinite;
        }
        @keyframes blinkT { 0%,100%{opacity:1} 50%{opacity:0} }

        /* PARTICLES */
        #pcanvas { position:fixed; inset:0; z-index:0; pointer-events:none; opacity:0.55; }

        /* GRID BG */
        .grid-bg {
            position:fixed; inset:0; z-index:0; pointer-events:none;
            background-image: linear-gradient(rgba(100,180,255,0.03) 1px,transparent 1px),
                              linear-gradient(90deg,rgba(100,180,255,0.03) 1px,transparent 1px);
            background-size:60px 60px;
        }

        /* NAVBAR */
        nav {
            position:fixed; top:0; left:0; right:0; z-index:100;
            padding:0 40px; height:72px;
            display:flex; align-items:center; justify-content:space-between;
            background:rgba(3,5,15,0.8); backdrop-filter:blur(20px);
            border-bottom:1px solid var(--border);
            animation:slideDown 0.8s cubic-bezier(0.16,1,0.3,1) 2.2s both;
        }
        @keyframes slideDown { from{transform:translateY(-100%);opacity:0} to{transform:translateY(0);opacity:1} }
        .nav-brand {
            font-family:'Syne',sans-serif; font-size:1.2rem; font-weight:800;
            letter-spacing:0.1em; color:var(--accent); text-transform:uppercase;
            text-decoration:none; display:flex; align-items:center; gap:10px;
        }
        .nav-brand-orb {
            width:30px; height:30px; border-radius:50%;
            background:conic-gradient(var(--accent),var(--accent2),var(--accent3),var(--accent));
            animation:spinR 4s linear infinite; flex-shrink:0;
        }
        .nav-brand span { color:var(--text); }
        .nav-tabs {
            display:flex; gap:6px;
            background:var(--surface2); padding:5px; border-radius:50px;
            border:1px solid var(--border);
        }
        .nav-tab {
            padding:8px 22px; border-radius:50px; border:none;
            background:transparent; color:var(--text-muted);
            font-family:'Syne',sans-serif; font-size:0.78rem; font-weight:600;
            letter-spacing:0.08em; text-transform:uppercase;
            cursor:pointer; transition:all 0.3s cubic-bezier(0.16,1,0.3,1);
            text-decoration:none; display:inline-flex; align-items:center; gap:8px;
        }
        .nav-tab:hover { color:var(--text); }
        .nav-tab.active {
            background:linear-gradient(135deg,var(--accent2),var(--accent));
            color:var(--bg); font-weight:700;
            box-shadow:0 0 20px var(--glow),0 0 40px var(--glow2);
        }
        .qbadge {
            background:rgba(255,255,255,0.2); border-radius:50%;
            width:20px; height:20px; font-size:0.65rem;
            display:flex; align-items:center; justify-content:center; font-weight:700;
        }
        .nav-info { font-size:0.68rem; color:var(--text-muted); letter-spacing:0.05em; }

        /* MAIN */
        main { position:relative; z-index:1; padding-top:72px; }

        /* HERO */
        .hero {
            padding:80px 40px 60px; text-align:center;
            animation:fadeUp 0.9s cubic-bezier(0.16,1,0.3,1) 2.4s both;
        }
        @keyframes fadeUp { from{transform:translateY(30px);opacity:0} to{transform:translateY(0);opacity:1} }
        .mode-tag {
            display:inline-flex; align-items:center; gap:8px;
            background:rgba(74,240,200,0.08); border:1px solid rgba(74,240,200,0.25);
            border-radius:50px; padding:6px 16px;
            font-size:0.68rem; letter-spacing:0.2em; text-transform:uppercase;
            color:var(--accent); margin-bottom:28px;
            font-family:'Syne',sans-serif; font-weight:600;
        }
        .live-dot {
            width:6px; height:6px; border-radius:50%; background:var(--accent);
            animation:livePulse 2s ease-in-out infinite;
        }
        @keyframes livePulse {
            0%,100%{box-shadow:0 0 0 0 rgba(74,240,200,0.6)}
            50%{box-shadow:0 0 0 6px rgba(74,240,200,0)}
        }
        .hero h1 {
            font-family:'Syne',sans-serif; font-size:clamp(2rem,5vw,3.8rem);
            font-weight:800; line-height:1.05; letter-spacing:-0.02em; margin-bottom:20px;
            background:linear-gradient(135deg,var(--text) 0%,var(--accent) 55%,var(--accent2) 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        }
        .hero-eq { font-size:1.05rem; color:var(--text-muted); margin-bottom:16px; }
        .hero-eq .ket { color:var(--accent); font-weight:700; }
        .hero-sub { font-size:0.82rem; color:var(--text-muted); max-width:500px; margin:0 auto; line-height:1.9; }

        /* CONTROL CARD */
        .ctrl-section { padding:0 40px 60px; display:flex; justify-content:center; animation:fadeUp 0.9s cubic-bezier(0.16,1,0.3,1) 2.6s both; }
        .ctrl-card {
            background:var(--surface); border:1px solid var(--border);
            border-radius:24px; padding:40px; width:100%; max-width:640px; position:relative; overflow:hidden;
        }
        .ctrl-card::before {
            content:''; position:absolute; top:-1px; left:20%; right:20%; height:1px;
            background:linear-gradient(90deg,transparent,var(--accent),var(--accent2),transparent);
        }
        .ctrl-card::after {
            content:''; position:absolute; top:0; left:0;
            width:200px; height:200px;
            background:radial-gradient(circle,var(--glow) 0%,transparent 70%);
            pointer-events:none;
        }
        .ctrl-label { font-family:'Syne',sans-serif; font-size:0.68rem; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; color:var(--text-muted); margin-bottom:12px; }
        .shots-wrap { position:relative; margin-bottom:20px; }
        .shots-wrap::before {
            content:'|ψ⟩'; position:absolute; left:16px; top:50%; transform:translateY(-50%);
            font-size:0.78rem; color:var(--accent); pointer-events:none; z-index:1;
        }
        input[type="number"] {
            width:100%; padding:16px 16px 16px 56px;
            background:var(--surface2); border:1px solid var(--border); border-radius:12px;
            color:var(--text); font-family:'Space Mono',monospace; font-size:1rem; outline:none;
            transition:all 0.3s ease; -moz-appearance:textfield;
        }
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button { -webkit-appearance:none; }
        input[type="number"]:focus { border-color:var(--accent); box-shadow:0 0 0 3px var(--glow); }
        .quick-shots { display:flex; gap:8px; margin-bottom:28px; flex-wrap:wrap; }
        .qbtn {
            padding:6px 14px; background:var(--surface2); border:1px solid var(--border);
            border-radius:8px; color:var(--text-muted); font-family:'Space Mono',monospace;
            font-size:0.7rem; cursor:pointer; transition:all 0.2s ease;
        }
        .qbtn:hover { border-color:var(--accent); color:var(--accent); background:rgba(74,240,200,0.06); }
        .sim-btn {
            width:100%; padding:18px;
            background:linear-gradient(135deg,var(--accent2) 0%,var(--accent) 100%);
            border:none; border-radius:14px; color:var(--bg);
            font-family:'Syne',sans-serif; font-size:0.92rem; font-weight:700;
            letter-spacing:0.1em; text-transform:uppercase; cursor:pointer;
            transition:all 0.3s cubic-bezier(0.16,1,0.3,1); position:relative; overflow:hidden;
        }
        .sim-btn::before { content:''; position:absolute; inset:0; background:linear-gradient(135deg,rgba(255,255,255,0.18),transparent); opacity:0; transition:opacity 0.3s ease; }
        .sim-btn:hover::before { opacity:1; }
        .sim-btn:hover { transform:translateY(-2px); box-shadow:0 12px 40px var(--glow),0 12px 40px var(--glow2); }
        .sim-btn:active { transform:translateY(0); }
        .sim-btn:disabled { opacity:0.45; cursor:not-allowed; transform:none; }

        /* LOADING OVERLAY */
        #load-overlay {
            display:none; position:fixed; inset:0;
            background:rgba(3,5,15,0.88); z-index:200;
            align-items:center; justify-content:center; flex-direction:column; gap:24px;
            backdrop-filter:blur(10px);
        }
        #load-overlay.on { display:flex; animation:fadeIn 0.3s ease; }
        @keyframes fadeIn { from{opacity:0} to{opacity:1} }
        .spin2 {
            position:relative; width:72px; height:72px;
        }
        .spin2::before, .spin2::after {
            content:''; position:absolute; border-radius:50%;
        }
        .spin2::before { inset:0; border:2px solid transparent; border-top-color:var(--accent); border-right-color:var(--accent); animation:spinR 1s linear infinite; }
        .spin2::after { inset:12px; border:2px solid transparent; border-bottom-color:var(--accent2); border-left-color:var(--accent2); animation:spinR 1.5s linear infinite reverse; }
        .load-text { font-family:'Syne',sans-serif; font-size:0.75rem; letter-spacing:0.2em; color:var(--accent); text-transform:uppercase; animation:pulseText 1.5s ease-in-out infinite; }

        /* RESULTS */
        .res-section { padding:0 40px 60px; display:flex; justify-content:center; animation:fadeUp 0.9s cubic-bezier(0.16,1,0.3,1) 2.8s both; }
        .res-card {
            background:var(--surface); border:1px solid var(--border);
            border-radius:24px; padding:40px; width:100%; max-width:820px; position:relative;
        }
        .res-card::after {
            content:''; position:absolute; bottom:-1px; left:20%; right:20%; height:1px;
            background:linear-gradient(90deg,transparent,var(--accent2),var(--accent3),transparent);
        }
        .res-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:28px; flex-wrap:wrap; gap:12px; }
        .res-title { font-family:'Syne',sans-serif; font-size:0.68rem; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; color:var(--text-muted); }
        .res-badge {
            display:flex; align-items:center; gap:8px;
            background:rgba(74,240,200,0.08); border:1px solid rgba(74,240,200,0.2);
            border-radius:50px; padding:5px 14px;
            font-size:0.67rem; color:var(--accent); font-family:'Syne',sans-serif; font-weight:600; letter-spacing:0.1em;
        }
        .plot-wrap { background:#fff; border-radius:16px; overflow:hidden; }
        .plot-wrap img { width:100%; height:auto; display:block; transition:opacity 0.4s ease; }

        /* INFO CARDS */
        .info-grid {
            display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
            gap:16px; padding:0 40px 80px; max-width:900px; margin:0 auto;
            animation:fadeUp 0.9s cubic-bezier(0.16,1,0.3,1) 3s both;
        }
        .info-card {
            background:var(--surface); border:1px solid var(--border);
            border-radius:16px; padding:24px;
            transition:all 0.3s ease;
        }
        .info-card:hover { border-color:rgba(74,240,200,0.3); transform:translateY(-4px); box-shadow:0 16px 48px rgba(74,240,200,0.07); }
        .ic-label { font-size:0.63rem; letter-spacing:0.2em; text-transform:uppercase; color:var(--text-muted); font-family:'Syne',sans-serif; font-weight:600; margin-bottom:10px; }
        .ic-val { font-family:'Space Mono',monospace; font-size:1.05rem; color:var(--accent); font-weight:700; }
        .ic-sub { font-size:0.68rem; color:var(--text-muted); margin-top:6px; line-height:1.55; }

        /* SCROLLBAR */
        ::-webkit-scrollbar { width:5px; }
        ::-webkit-scrollbar-track { background:var(--bg); }
        ::-webkit-scrollbar-thumb { background:var(--surface2); border-radius:3px; }
        ::-webkit-scrollbar-thumb:hover { background:var(--accent2); }

        @media(max-width:640px) {
            nav { padding:0 16px; }
            .nav-brand span { display:none; }
            .nav-tab { padding:8px 12px; font-size:0.72rem; }
            .nav-info { display:none; }
            .hero { padding:60px 20px 40px; }
            .ctrl-section,.res-section { padding-left:16px; padding-right:16px; }
            .info-grid { padding-left:16px; padding-right:16px; }
        }
    </style>
</head>
<body>

<div id="preloader">
    <div class="preloader-logo">Q<span>Entangle</span></div>
    <div class="orb-wrap">
        <div class="orb-ring"></div>
        <div class="orb-ring"></div>
        <div class="orb-ring"></div>
        <div class="orb-core"></div>
    </div>
    <div class="preloader-sub">Initializing Quantum Simulator_</div>
</div>

<div id="load-overlay">
    <div class="spin2"></div>
    <div class="load-text">Collapsing Wavefunctions...</div>
</div>

<canvas id="pcanvas"></canvas>
<div class="grid-bg"></div>

<nav>
    <a href="/?mode=2&s=%(s)s" class="nav-brand">
        <div class="nav-brand-orb"></div>
        Q<span>Entangle</span>
    </a>
    <div class="nav-tabs">
        <a href="/?mode=2&s=%(s)s" class="nav-tab %(a2)s">
            <span class="qbadge">2</span> Qubit
        </a>
        <a href="/?mode=3&s=%(s)s" class="nav-tab %(a3)s">
            <span class="qbadge">3</span> Qubit
        </a>
    </div>
    <div class="nav-info">%(nav_info)s</div>
</nav>

<main>
    <section class="hero">
        <div class="mode-tag"><div class="live-dot"></div>%(state_name)s &bull; Active Simulation</div>
        <h1>%(hero_title)s</h1>
        <div class="hero-eq">%(equation)s</div>
        <p class="hero-sub">%(hero_sub)s</p>
    </section>

    <section class="ctrl-section">
        <div class="ctrl-card">
            <div class="ctrl-label">Simulation Shots</div>
            <div class="shots-wrap">
                <input type="number" id="s_input" value="%(s)s" min="1" max="100000">
            </div>
            <div class="ctrl-label">Quick Select</div>
            <div class="quick-shots">
                <button class="qbtn" onclick="setShots(50)">50</button>
                <button class="qbtn" onclick="setShots(100)">100</button>
                <button class="qbtn" onclick="setShots(500)">500</button>
                <button class="qbtn" onclick="setShots(1000)">1000</button>
                <button class="qbtn" onclick="setShots(5000)">5K</button>
                <button class="qbtn" onclick="setShots(10000)">10K</button>
            </div>
            <button class="sim-btn" id="sim-btn" onclick="simulate()">&#x27F6; Run Simulation</button>
        </div>
    </section>

    <section class="res-section">
        <div class="res-card">
            <div class="res-header">
                <div class="res-title">Measurement Histogram</div>
                <div class="res-badge">
                    <div class="live-dot"></div>
                    %(s)s Shots &bull; %(qubits)sQ System
                </div>
            </div>
            <div class="plot-wrap">
                <img id="plot-img" src="/plot?mode=%(mode)s&s=%(s)s" alt="Quantum measurement histogram">
            </div>
        </div>
    </section>

    <div class="info-grid">
        <div class="info-card">
            <div class="ic-label">Entanglement Type</div>
            <div class="ic-val">%(ent_type)s</div>
            <div class="ic-sub">%(ent_desc)s</div>
        </div>
        <div class="info-card">
            <div class="ic-label">Expected States</div>
            <div class="ic-val">%(exp_states)s</div>
            <div class="ic-sub">%(states_desc)s</div>
        </div>
        <div class="info-card">
            <div class="ic-label">State Vector</div>
            <div class="ic-val" style="font-size:0.85rem;">%(state_vec)s</div>
            <div class="ic-sub">Normalized superposition amplitude</div>
        </div>
        <div class="info-card">
            <div class="ic-label">Circuit Gates</div>
            <div class="ic-val">%(gates)s</div>
            <div class="ic-sub">%(gates_desc)s</div>
        </div>
    </div>
</main>

<script>
// PRELOADER
window.addEventListener('load', () => {
    setTimeout(() => document.getElementById('preloader').classList.add('hidden'), 2200);
});

// PARTICLES
const cvs = document.getElementById('pcanvas');
const ctx = cvs.getContext('2d');
function resizeCvs() { cvs.width = window.innerWidth; cvs.height = window.innerHeight; }
resizeCvs();
window.addEventListener('resize', resizeCvs);

const pts = Array.from({length:65}, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vx: (Math.random()-0.5)*0.38,
    vy: (Math.random()-0.5)*0.38,
    r: Math.random()*1.4+0.3,
    a: Math.random()*0.5+0.1,
    col: Math.random()>0.5 ? '74,240,200' : '123,111,247',
    ph: Math.random()*Math.PI*2
}));

function drawPts() {
    ctx.clearRect(0,0,cvs.width,cvs.height);
    pts.forEach((p,i) => {
        p.x += p.vx; p.y += p.vy; p.ph += 0.018;
        if(p.x<0) p.x=cvs.width; if(p.x>cvs.width) p.x=0;
        if(p.y<0) p.y=cvs.height; if(p.y>cvs.height) p.y=0;
        const al = p.a*(0.55+0.45*Math.sin(p.ph));
        ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fillStyle=`rgba(${p.col},${al})`.toString(); ctx.fill();
        for(let j=i+1;j<pts.length;j++){
            const q=pts[j], dx=p.x-q.x, dy=p.y-q.y, d=Math.sqrt(dx*dx+dy*dy);
            if(d<115){ ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y);
                ctx.strokeStyle=`rgba(${p.col},${(1-d/115)*0.11})`; ctx.lineWidth=0.5; ctx.stroke(); }
        }
    });
    requestAnimationFrame(drawPts);
}
drawPts();

// SIMULATION
const MODE = '%(mode)s';
function setShots(v){ document.getElementById('s_input').value=v; }
function simulate(){
    const s = document.getElementById('s_input').value || 100;
    document.getElementById('load-overlay').classList.add('on');
    document.getElementById('sim-btn').disabled=true;
    const img=document.getElementById('plot-img');
    const tmp=new Image();
    tmp.onload=()=>{
        img.style.opacity='0';
        setTimeout(()=>{ img.src=tmp.src; img.style.opacity='1'; },100);
        document.getElementById('load-overlay').classList.remove('on');
        document.getElementById('sim-btn').disabled=false;
        history.replaceState(null,'',`/?mode=${MODE}&s=${s}`);
    };
    tmp.onerror=()=>{
        document.getElementById('load-overlay').classList.remove('on');
        document.getElementById('sim-btn').disabled=false;
    };
    tmp.src=`/plot?mode=${MODE}&s=${s}&t=${Date.now()}`;
}
</script>
</body>
</html>"""


def build_page(mode, s):
    if mode == 3:
        data = dict(
            s=s, mode=3, a2="", a3="active",
            nav_info="GHZ State &bull; 3-Qubit System",
            state_name="GHZ State",
            hero_title="3-Qubit GHZ Entanglement",
            equation='<span class="ket">|GHZ&rang;</span> = ( <span class="ket">|000&rang;</span> + <span class="ket">|111&rang;</span> ) / &radic;2',
            hero_sub="Three qubits entangled in the Greenberger&ndash;Horne&ndash;Zeilinger state &mdash; the maximally entangled 3-body quantum state, fundamental to quantum error correction and multi-party cryptography.",
            qubits=3,
            ent_type="GHZ State",
            ent_desc="Greenberger&ndash;Horne&ndash;Zeilinger maximally entangled 3-qubit state",
            exp_states="|000&rang;, |111&rang;",
            states_desc="Only 2 of 8 possible states measured &mdash; perfect tripartite entanglement",
            state_vec="1/&radic;2 (|000&rang;+|111&rang;)",
            gates="H + CX + CX",
            gates_desc="Hadamard gate followed by two cascaded CNOT gates",
        )
    else:
        data = dict(
            s=s, mode=2, a2="active", a3="",
            nav_info="Bell State &bull; 2-Qubit System",
            state_name="Bell State",
            hero_title="2-Qubit Bell State Entanglement",
            equation='<span class="ket">|&Phi;<sup>+</sup>&rang;</span> = ( <span class="ket">|00&rang;</span> + <span class="ket">|11&rang;</span> ) / &radic;2',
            hero_sub="Two qubits locked in the maximally entangled Bell state &mdash; a cornerstone of quantum computing, quantum cryptography, and quantum teleportation protocols.",
            qubits=2,
            ent_type="Bell State &Phi;&sup+;",
            ent_desc="Maximally entangled EPR pair &mdash; the prototypical Bell state",
            exp_states="|00&rang;, |11&rang;",
            states_desc="Only 2 of 4 possible states appear &mdash; confirming entanglement",
            state_vec="1/&radic;2 (|00&rang;+|11&rang;)",
            gates="H + CNOT",
            gates_desc="Hadamard creates superposition, CNOT entangles the two qubits",
        )
    result = HTML_TEMPLATE
    for key, val in data.items():
        result = result.replace(f'%({key})s', str(val))
    return result


@q.route("/")
def index():
    try:
        s = request.args.get('s', default=100, type=int)
        if s <= 0:
            s = 100
    except (ValueError, TypeError):
        s = 100
    mode_str = request.args.get('mode', default='2')
    mode = 3 if mode_str == '3' else 2
    return build_page(mode, s)


@q.route("/plot")
def generate_plot():
    try:
        s = request.args.get('s', default=100, type=int)
        if s <= 0:
            s = 100
    except (ValueError, TypeError):
        s = 100
    mode = request.args.get('mode', default='2')
    buf = io.BytesIO()
    if mode == '3':
        fig = qis3.q3(s)
    else:
        fig = qis.q(s)
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return send_file(buf, mimetype='image/png', as_attachment=False, download_name='plot.png')


if __name__ == "__main__":
    thread = threading.Thread(target=run_infinite_logger)
    thread.daemon = True
    thread.start()
    q.run(debug=True)
