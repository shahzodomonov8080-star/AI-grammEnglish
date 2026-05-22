"""mobil_dasturlash_testlari.txt dan quiz HTML yaratadi."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TXT = ROOT / "mobil_dasturlash_testlari.txt"
OUT_HTML = Path(__file__).resolve().parent / "index.html"
OUT_JSON = Path(__file__).resolve().parent / "quiz_data.json"

OPTION_RE = re.compile(r"^#?\s*([A-D])\)\s*(.+)$")


def parse_questions(text: str) -> list[dict]:
    questions = []
    blocks = re.split(r"--- Savol \d+ ---\s*", text)
    for block in blocks[1:]:
        lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
        if not lines:
            continue
        q_text = []
        options = []
        correct = None
        for ln in lines:
            if ln.startswith("=") or ln.startswith("JAMI:"):
                continue
            m = OPTION_RE.match(ln)
            if m:
                letter, opt_text = m.group(1), m.group(2)
                if ln.startswith("#"):
                    correct = letter
                options.append({"id": letter, "text": opt_text})
            else:
                q_text.append(ln)
        if len(options) >= 2 and correct:
            questions.append(
                {
                    "question": " ".join(q_text),
                    "options": options,
                    "correct": correct,
                }
            )
    return questions


def main():
    text = TXT.read_text(encoding="utf-8")
    questions = parse_questions(text)
    OUT_JSON.write_text(
        json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    data_js = json.dumps(questions, ensure_ascii=False)
    html = HTML_TEMPLATE.replace("/*__QUIZ_DATA__*/", data_js)
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"{len(questions)} savol -> {OUT_HTML}")


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Mobil dasturlash — Quiz</title>
  <style>
    :root {
      --bg: #0f1419;
      --card: #1a2332;
      --accent: #3d9cf5;
      --accent-dim: #2563eb;
      --ok: #22c55e;
      --bad: #ef4444;
      --text: #e8edf4;
      --muted: #8b9cb3;
      --border: #2a3a52;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: "Segoe UI", system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
    }
    .wrap { max-width: 720px; margin: 0 auto; padding: 24px 16px 48px; }
    header { text-align: center; margin-bottom: 28px; }
    header h1 { font-size: 1.5rem; font-weight: 700; margin-bottom: 6px; }
    header p { color: var(--muted); font-size: 0.9rem; }
    .panel {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 28px 24px;
      box-shadow: 0 8px 32px rgba(0,0,0,.35);
    }
    .hidden { display: none !important; }
    .progress-bar {
      height: 6px;
      background: var(--border);
      border-radius: 3px;
      overflow: hidden;
      margin-bottom: 20px;
    }
    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--accent-dim), var(--accent));
      border-radius: 3px;
      transition: width .3s ease;
    }
    .meta {
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 16px;
    }
    .q-text {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 22px;
      line-height: 1.45;
    }
    .options { display: flex; flex-direction: column; gap: 10px; }
    .opt {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 14px 16px;
      border: 2px solid var(--border);
      border-radius: 12px;
      cursor: pointer;
      transition: border-color .15s, background .15s;
      text-align: left;
      width: 100%;
      background: transparent;
      color: var(--text);
      font-size: 0.95rem;
    }
    .opt:hover:not(:disabled) { border-color: var(--accent); background: rgba(61,156,245,.08); }
    .opt .letter {
      flex-shrink: 0;
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: var(--border);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.8rem;
    }
    .opt.correct { border-color: var(--ok); background: rgba(34,197,94,.12); }
    .opt.correct .letter { background: var(--ok); color: #fff; }
    .opt.wrong { border-color: var(--bad); background: rgba(239,68,68,.1); }
    .opt.wrong .letter { background: var(--bad); color: #fff; }
    .opt:disabled { cursor: default; opacity: .95; }
    .actions { margin-top: 24px; display: flex; gap: 10px; flex-wrap: wrap; }
    .btn {
      padding: 12px 22px;
      border: none;
      border-radius: 10px;
      font-size: 0.95rem;
      font-weight: 600;
      cursor: pointer;
      transition: transform .1s, opacity .15s;
    }
    .btn:active { transform: scale(0.98); }
    .btn-primary { background: var(--accent); color: #fff; }
    .btn-primary:hover { background: var(--accent-dim); }
    .btn-primary:disabled { opacity: .45; cursor: not-allowed; }
    .btn-ghost {
      background: transparent;
      color: var(--muted);
      border: 1px solid var(--border);
    }
    .btn-ghost:hover { color: var(--text); border-color: var(--accent); }
    .start-grid {
      display: grid;
      gap: 14px;
      margin: 20px 0;
    }
    .start-grid label {
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 0.85rem;
      color: var(--muted);
    }
    select {
      padding: 10px 12px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--text);
      font-size: 1rem;
    }
    .score-ring {
      width: 140px;
      height: 140px;
      margin: 0 auto 20px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 2rem;
      font-weight: 800;
      background: conic-gradient(var(--accent) calc(var(--pct) * 1%), var(--border) 0);
      position: relative;
    }
    .score-ring::after {
      content: "";
      position: absolute;
      inset: 10px;
      background: var(--card);
      border-radius: 50%;
    }
    .score-ring span { position: relative; z-index: 1; }
    .result-title { text-align: center; font-size: 1.35rem; margin-bottom: 8px; }
    .result-sub { text-align: center; color: var(--muted); margin-bottom: 24px; }
    .stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-bottom: 24px;
    }
    .stat {
      text-align: center;
      padding: 14px;
      background: var(--bg);
      border-radius: 10px;
      border: 1px solid var(--border);
    }
    .stat b { display: block; font-size: 1.4rem; margin-bottom: 4px; }
    .stat.ok b { color: var(--ok); }
    .stat.bad b { color: var(--bad); }
    .stat span { font-size: 0.75rem; color: var(--muted); }
    .review { margin-top: 20px; max-height: 280px; overflow-y: auto; }
    .review h3 { font-size: 0.9rem; color: var(--muted); margin-bottom: 10px; }
    .review-item {
      padding: 10px 12px;
      border-radius: 8px;
      margin-bottom: 8px;
      font-size: 0.85rem;
      border-left: 3px solid var(--bad);
      background: rgba(239,68,68,.06);
    }
    .review-item.ok { border-left-color: var(--ok); background: rgba(34,197,94,.06); }
    .feedback {
      margin-top: 14px;
      padding: 12px;
      border-radius: 10px;
      font-size: 0.9rem;
    }
    .feedback.ok { background: rgba(34,197,94,.15); color: #86efac; }
    .feedback.bad { background: rgba(239,68,68,.15); color: #fca5a5; }
  </style>
</head>
<body>
  <div class="wrap">
    <header>
      <h1>Mobil dasturlash</h1>
      <p>131 ta savol — interaktiv quiz</p>
    </header>

    <div id="screen-start" class="panel">
      <h2 style="margin-bottom:8px;font-size:1.2rem;">Quizni boshlash</h2>
      <p style="color:var(--muted);font-size:0.9rem;margin-bottom:4px;">
        Savollar aralashtiriladi. Javob tanlangach keyingi savolga avtomatik o'tiladi.
      </p>
      <div class="start-grid">
        <label>
          Savollar soni
          <select id="count-select">
            <option value="10">10 ta</option>
            <option value="20">20 ta</option>
            <option value="30">30 ta</option>
            <option value="50">50 ta</option>
            <option value="0" selected>Barchasi (131)</option>
          </select>
        </label>
      </div>
      <button type="button" class="btn btn-primary" id="btn-start">Boshlash</button>
    </div>

    <div id="screen-quiz" class="panel hidden">
      <div class="progress-bar"><div class="progress-fill" id="progress"></div></div>
      <div class="meta">
        <span id="counter">1 / 10</span>
        <span id="score-live">Ball: 0</span>
      </div>
      <p class="q-text" id="question"></p>
      <div class="options" id="options"></div>
      <div id="feedback" class="feedback hidden"></div>
      <div class="actions">
        <button type="button" class="btn btn-ghost" id="btn-quit">Chiqish</button>
      </div>
    </div>

    <div id="screen-result" class="panel hidden">
      <div class="score-ring" id="score-ring"><span id="pct-text">0%</span></div>
      <h2 class="result-title" id="result-title">Natija</h2>
      <p class="result-sub" id="result-sub"></p>
      <div class="stats">
        <div class="stat ok"><b id="stat-ok">0</b><span>To'g'ri</span></div>
        <div class="stat bad"><b id="stat-bad">0</b><span>Noto'g'ri</span></div>
        <div class="stat"><b id="stat-total">0</b><span>Jami</span></div>
      </div>
      <div class="review hidden" id="review">
        <h3>Noto'g'ri javoblar</h3>
        <div id="review-list"></div>
      </div>
      <div class="actions" style="justify-content:center;">
        <button type="button" class="btn btn-primary" id="btn-restart">Qayta boshlash</button>
      </div>
    </div>
  </div>

  <script>
    const ALL_QUESTIONS = /*__QUIZ_DATA__*/;

    let deck = [];
    let index = 0;
    let score = 0;
    let answered = false;
    let wrongList = [];
    let advanceTimer = null;
    const AUTO_ADVANCE_MS = 1200;

    const $ = (id) => document.getElementById(id);

    function clearAdvanceTimer() {
      if (advanceTimer) {
        clearTimeout(advanceTimer);
        advanceTimer = null;
      }
    }

    function goNext() {
      clearAdvanceTimer();
      if (index < deck.length - 1) {
        index++;
        renderQuestion();
      } else {
        showResult();
      }
    }

    function shuffle(arr) {
      const a = [...arr];
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    }

    function show(id) {
      ["screen-start", "screen-quiz", "screen-result"].forEach((s) => {
        $(s).classList.toggle("hidden", s !== id);
      });
    }

    function startQuiz() {
      clearAdvanceTimer();
      const n = parseInt($("count-select").value, 10);
      deck = shuffle(ALL_QUESTIONS);
      if (n > 0) deck = deck.slice(0, Math.min(n, deck.length));
      index = 0;
      score = 0;
      wrongList = [];
      show("screen-quiz");
      renderQuestion();
    }

    function renderQuestion() {
      clearAdvanceTimer();
      answered = false;
      const q = deck[index];
      $("counter").textContent = `${index + 1} / ${deck.length}`;
      $("score-live").textContent = `Ball: ${score}`;
      $("progress").style.width = `${((index) / deck.length) * 100}%`;
      $("question").textContent = q.question;
      $("feedback").classList.add("hidden");

      const opts = shuffle(q.options);
      const box = $("options");
      box.innerHTML = "";
      opts.forEach((o) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "opt";
        btn.dataset.id = o.id;
        btn.innerHTML = `<span class="letter">${o.id}</span><span>${escapeHtml(o.text)}</span>`;
        btn.addEventListener("click", () => pick(btn, o.id));
        box.appendChild(btn);
      });
    }

    function escapeHtml(s) {
      const d = document.createElement("div");
      d.textContent = s;
      return d.innerHTML;
    }

    function pick(btn, id) {
      if (answered) return;
      answered = true;
      const q = deck[index];
      const correct = q.correct;
      const all = $("options").querySelectorAll(".opt");
      all.forEach((b) => {
        b.disabled = true;
        if (b.dataset.id === correct) b.classList.add("correct");
        else if (b === btn && id !== correct) b.classList.add("wrong");
      });

      const fb = $("feedback");
      fb.classList.remove("hidden", "ok", "bad");
      if (id === correct) {
        score++;
        fb.classList.add("ok");
        fb.textContent = "To'g'ri!";
      } else {
        fb.classList.add("bad");
        const right = q.options.find((o) => o.id === correct);
        fb.textContent = `Noto'g'ri. To'g'ri javob: ${correct}) ${right.text}`;
        wrongList.push({ q, picked: id });
      }
      $("score-live").textContent = `Ball: ${score}`;
      advanceTimer = setTimeout(goNext, AUTO_ADVANCE_MS);
    }

    function showResult() {
      show("screen-result");
      const total = deck.length;
      const pct = total ? Math.round((score / total) * 100) : 0;
      $("pct-text").textContent = pct + "%";
      $("score-ring").style.setProperty("--pct", pct);
      $("stat-ok").textContent = score;
      $("stat-bad").textContent = total - score;
      $("stat-total").textContent = total;

      let title = "Ajoyib!";
      if (pct < 50) title = "Yana mashq qiling";
      else if (pct < 80) title = "Yaxshi natija!";
      $("result-title").textContent = title;
      $("result-sub").textContent = `${score} ta to'g'ri, ${total - score} ta noto'g'ri (${total} savoldan)`;

      const rev = $("review");
      const list = $("review-list");
      list.innerHTML = "";
      if (wrongList.length) {
        rev.classList.remove("hidden");
        wrongList.forEach(({ q, picked }) => {
          const right = q.options.find((o) => o.id === q.correct);
          const div = document.createElement("div");
          div.className = "review-item";
          div.innerHTML = `<strong>${escapeHtml(q.question)}</strong><br>Siz: ${picked}) · To'g'ri: ${q.correct}) ${escapeHtml(right.text)}`;
          list.appendChild(div);
        });
      } else {
        rev.classList.add("hidden");
      }
    }

    $("btn-start").addEventListener("click", startQuiz);
    $("btn-quit").addEventListener("click", () => {
      clearAdvanceTimer();
      if (confirm("Quizni tugatmoqchimisiz?")) show("screen-start");
    });
    $("btn-restart").addEventListener("click", () => show("screen-start"));
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
