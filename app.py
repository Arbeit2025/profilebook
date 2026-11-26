# profilebook - プロフィール帳ジェネレーター
# 昔ながらのプロフィール帳の項目をフォームに入力すると、
# 罫線ノート風のプレビューがその場で出来上がる単一ファイルFlaskアプリ。
# 入力内容はブラウザの localStorage に自動保存され、サーバーには送信されない。
import json

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# フォームの項目（キー, ラベル, 種類）
FIELDS = [
("name", "なまえ", "text"),
("nickname", "ニックネーム", "text"),
("birthday", "誕生日", "text"),
("blood", "血液型", "select"),
("food", "好きな食べ物", "text"),
("color", "好きな色", "text"),
("music", "好きな音楽・歌手", "text"),
("hobby", "趣味", "text"),
("skill", "特技", "text"),
("dream", "将来の夢", "text"),
("want", "今ほしいもの", "text"),
("message", "一言メッセージ", "textarea"),
]

BLOOD_TYPES = ["A型", "B型", "O型", "AB型", "わからない"]

# ランダムお題のプール（ここから3つ抽選される）
QUESTIONS = [
"無人島に1つ持っていくなら？",
"明日世界が終わるなら何食べる？",
"自分を動物に例えると？",
"宝くじで100万円当たったら何に使う？",
"タイムマシンで行ってみたい時代は？",
"魔法が1つ使えるなら何の魔法？",
"生まれ変わるなら何になりたい？",
"一番の宝物は？",
"最近笑ったことは？",
"子どもの頃の夢は？",
"好きな季節とその理由は？",
"自分へのごほうびといえば？",
"カラオケの十八番は？",
"ペットを飼うなら何を飼いたい？",
"宇宙旅行に行けるなら行く？ 行かない？",
"一番行きたい場所は？",
"昨日の晩ごはんは？",
"自分のチャームポイントは？",
"ストレス解消法は？",
"1日だけ誰かと入れ替わるなら誰？",
"好きな映画やドラマは？",
"休みの日は何してる？",
"最近ハマっていることは？",
"10年後の自分にひとこと",
]

CSS = """
* { box-sizing: border-box;}
html, body { margin: 0; padding: 0;}
body {
background: #fdf3f5; color: #4a3a42;
font-family: "Hiragino Maru Gothic ProN", "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
line-height: 1.7;
}
header { text-align: center; padding: 2rem 1rem 0.2rem;}
header h1 { font-size: 1.6rem; letter-spacing: 0.14em; margin: 0; color: #c2506e;}
header p { color: #a58391; font-size: 0.88rem; margin: 0.35rem 0 0;}
main {
max-width: 1060px; margin: 0 auto; padding: 1.2rem 1rem 3rem;
display: flex; flex-wrap: wrap; gap: 1.4rem; align-items: flex-start;
}
section.form-area { flex: 1 1 340px; min-width: 0;}
section.preview-area { flex: 1 1 340px; min-width: 0;}
@media (min-width: 900px) {
section.preview-area { position: sticky; top: 1rem;}
}
h2 { font-size: 1.05rem; color: #c2506e; letter-spacing: 0.1em; margin: 0.6rem 0 0.8rem;}
.field { margin-bottom: 0.95rem;}
.field label { display: block; font-size: 0.86rem; color: #9c5a72; margin-bottom: 0.25rem;}
.field input[type="text"],.field select,.field textarea {
width: 100%; font-family: inherit; font-size: 1rem; color: #4a3a42;
background: #fffefe; border: 1px solid #eccdd5; border-radius: 8px;
padding: 0.5rem 0.7rem;
}
.field textarea { min-height: 4.2rem; resize: vertical;}
.field input:focus,.field select:focus,.field textarea:focus {
outline: 2px solid #f3a8bc; border-color: #f3a8bc;
}
.qa {
background: #fffefe; border: 1px dashed #e5a9bb; border-radius: 10px;
padding: 0.7rem 0.85rem; margin-bottom: 0.8rem;
}
.qa.q { font-size: 0.92rem; color: #b03a5c; margin-bottom: 0.35rem;}
.qa input[type="text"] {
width: 100%; font-family: inherit; font-size: 1rem; color: #4a3a42;
background: #fffefe; border: 1px solid #eccdd5; border-radius: 8px; padding: 0.45rem 0.7rem;
}
.actions { margin: 1.1rem 0 0.4rem; display: flex; flex-wrap: wrap; gap: 0.5rem;}
button {
font-family: inherit; border: none; cursor: pointer; border-radius: 999px;
padding: 0.55rem 1.25rem; font-size: 0.92rem; letter-spacing: 0.06em;
background: #d95f83; color: #fff;
}
button:hover { background: #c2506e;}
button.sub { background: #fff; color: #b03a5c; border: 1px solid #d95f83;}
button.danger { background: #fff; color: #8a8a8a; border: 1px solid #cfcfcf;}
.saved-note { font-size: 0.78rem; color: #b79aa5; margin-top: 0.5rem;}
.paper {
background-color: #fffdf4;
background-image:
linear-gradient(90deg, transparent 34px, #f2a7b8 35px, transparent 36px),
repeating-linear-gradient(transparent, transparent 33px, #cfe0f2 34px);
border: 1px solid #e8d9a8; border-radius: 6px;
box-shadow: 0 8px 24px rgba(160, 110, 60, 0.14);
padding: 1.1rem 1.1rem 1.3rem 3rem;
}
.paper h3 {
margin: 0 0 0.4rem; font-size: 1.15rem; color: #c2506e; line-height: 34px;
letter-spacing: 0.12em;
}
.paper.row { line-height: 34px; font-size: 0.98rem; overflow-wrap: break-word;}
.paper.row.lbl { color: #b03a5c; font-size: 0.82rem; margin-right: 0.5rem;}
.paper.row.val { color: #4a3a42;}
.paper.row.val.empty { color: #c9b8a6;}
.paper.qa-q { line-height: 34px; color: #b03a5c; font-size: 0.9rem; overflow-wrap: break-word;}
.paper.qa-a { line-height: 34px; font-size: 0.98rem; padding-left: 0.8rem; overflow-wrap: break-word;}
.paper.qa-a.empty { color: #c9b8a6;}
footer { text-align: center; color: #bfa3ae; font-size: 0.8rem; padding: 0 1rem 2rem;}
"""

SCRIPT_TEMPLATE = """
var STORAGE_KEY = 'profilebook-v1';
var QUESTION_POOL = __QUESTION_POOL_JSON__;
var QUESTION_COUNT = 3;

function fieldEls() { return document.querySelectorAll('.field-input');}
function qaSlots() { return document.querySelectorAll('.qa');}

function currentQuestions() {
var qs = [];
qaSlots().forEach(function (slot) { qs.push(slot.getAttribute('data-question') || '');});
return qs;
}

function drawQuestions() {
var pool = QUESTION_POOL.slice();
var picked = [];
while (picked.length < QUESTION_COUNT && pool.length > 0) {
var i = Math.floor(Math.random() * pool.length);
picked.push(pool.splice(i, 1)[0]);
}
qaSlots().forEach(function (slot, idx) {
slot.setAttribute('data-question', picked[idx]);
slot.querySelector('.q').textContent = 'Q. ' + picked[idx];
slot.querySelector('.qa-answer').value = '';
});
}

function collectState() {
var state = { fields: {}, questions: currentQuestions(), answers: {}};
fieldEls().forEach(function (el) { state.fields[el.getAttribute('data-field')] = el.value;});
qaSlots().forEach(function (slot) {
var q = slot.getAttribute('data-question');
var a = slot.querySelector('.qa-answer').value;
if (q) { state.answers[q] = a;}
});
return state;
}

function save() {
try { localStorage.setItem(STORAGE_KEY, JSON.stringify(collectState()));} catch (e) {}
}

function restore() {
var raw = null;
try { raw = localStorage.getItem(STORAGE_KEY);} catch (e) {}
if (!raw) { drawQuestions(); return;}
var state = null;
try { state = JSON.parse(raw);} catch (e) { drawQuestions(); return;}
if (state.fields) {
fieldEls().forEach(function (el) {
var v = state.fields[el.getAttribute('data-field')];
if (typeof v === 'string') { el.value = v;}
});
}
if (state.questions && state.questions.length === QUESTION_COUNT) {
qaSlots().forEach(function (slot, idx) {
var q = state.questions[idx];
slot.setAttribute('data-question', q);
slot.querySelector('.q').textContent = 'Q. ' + q;
var a = (state.answers && state.answers[q]) || '';
slot.querySelector('.qa-answer').value = a;
});
} else {
drawQuestions();
}
}

function esc(s) {
return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function updatePreview() {
fieldEls().forEach(function (el) {
var key = el.getAttribute('data-field');
var pv = document.getElementById('pv-' + key);
if (!pv) { return;}
var v = el.value.trim();
pv.textContent = v === ''? '…………': v;
pv.className = 'val' + (v === ''? ' empty': '');
});
qaSlots().forEach(function (slot, idx) {
var q = slot.getAttribute('data-question') || '';
var a = slot.querySelector('.qa-answer').value.trim();
document.getElementById('pv-q-' + idx).textContent = 'Q. ' + q;
var pa = document.getElementById('pv-a-' + idx);
pa.textContent = a === ''? '…………': a;
pa.className = 'qa-a' + (a === ''? ' empty': '');
});
}

function buildText() {
var lines = [''];
fieldEls().forEach(function (el) {
var v = el.value.trim();
if (v!== '') { lines.push(el.getAttribute('data-label') + '：' + v);}
});
lines.push('');
lines.push('');
qaSlots().forEach(function (slot) {
var q = slot.getAttribute('data-question') || '';
var a = slot.querySelector('.qa-answer').value.trim();
lines.push('Q. ' + q);
lines.push('A. ' + a);
});
return lines.join('\\n');
}

function copyText() {
var text = buildText();
function done() {
var btn = document.getElementById('copy-btn');
var old = btn.textContent;
btn.textContent = 'コピーしました';
setTimeout(function () { btn.textContent = old;}, 1600);
}
if (navigator.clipboard && navigator.clipboard.writeText) {
navigator.clipboard.writeText(text).then(done, done);
} else {
var ta = document.createElement('textarea');
ta.value = text;
document.body.appendChild(ta);
ta.select();
try { document.execCommand('copy');} catch (e) {}
document.body.removeChild(ta);
done();
}
}

function clearAll() {
if (!window.confirm('入力した内容を全部消して、最初からにしますか？')) { return;}
fieldEls().forEach(function (el) { el.value = '';});
try { localStorage.removeItem(STORAGE_KEY);} catch (e) {}
drawQuestions();
updatePreview();
save();
}

document.addEventListener('DOMContentLoaded', function () {
restore();
updatePreview();
document.querySelectorAll('input, select, textarea').forEach(function (el) {
el.addEventListener('input', function () { save(); updatePreview();});
el.addEventListener('change', function () { save(); updatePreview();});
});
document.getElementById('shuffle-btn').addEventListener('click', function () {
drawQuestions(); save(); updatePreview();
});
document.getElementById('copy-btn').addEventListener('click', copyText);
document.getElementById('clear-btn').addEventListener('click', clearAll);
});
"""

SCRIPT = SCRIPT_TEMPLATE.replace(
    "__QUESTION_POOL_JSON__", json.dumps(QUESTIONS, ensure_ascii=False)
)


def form_html():
    parts = []
    for key, label, kind in FIELDS:
        if kind == "select":
            options = ['<option value="">（えらんでね）</option>']
            for b in BLOOD_TYPES:
                options.append(f'<option value="{b}">{b}</option>')
            control = (
                f'<select class="field-input" data-field="{key}" data-label="{label}">'
                + "".join(options)
                + "</select>"
            )
        elif kind == "textarea":
            control = (
                f'<textarea class="field-input" data-field="{key}" data-label="{label}" '
                f'placeholder="みんなへのひとことをどうぞ"></textarea>'
            )
        else:
            control = (
                f'<input type="text" class="field-input" data-field="{key}" '
                f'data-label="{label}">'
            )
        parts.append(f'<div class="field"><label>{label}</label>{control}</div>')
    return "\n".join(parts)


def qa_form_html():
    parts = []
    for _ in range(3):
        parts.append(
            '<div class="qa" data-question="">'
            '<div class="q">Q.</div>'
            '<input type="text" class="qa-answer" placeholder="答えを書いてね">'
            "</div>"
        )
    return "\n".join(parts)


def preview_html():
    rows = []
    for key, label, _kind in FIELDS:
        rows.append(
            f'<div class="row"><span class="lbl">{label}</span>'
            f'<span class="val empty" id="pv-{key}">…………</span></div>'
        )
    for i in range(3):
        rows.append(f'<div class="qa-q" id="pv-q-{i}">Q.</div>')
        rows.append(f'<div class="qa-a empty" id="pv-a-{i}">…………</div>')
    return "\n".join(rows)


BODY = f"""
<section class="form-area">
  <h2>プロフィールを書く</h2>
  {form_html()}
  <h2>ランダムお題</h2>
  {qa_form_html()}
  <div class="actions">
    <button type="button" id="shuffle-btn" class="sub">お題をシャッフル</button>
    <button type="button" id="copy-btn">文章でコピー</button>
    <button type="button" id="clear-btn" class="danger">全部消す</button>
  </div>
  <p class="saved-note">入力した内容は、このブラウザに自動で保存されます（サーバーには送られません）。</p>
</section>
<section class="preview-area">
  <h2>プレビュー</h2>
  <div class="paper">
    <h3>プロフィール</h3>
    {preview_html()}
  </div>
</section>
"""

BASE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }} | profilebook</title>
<style>{{ css|safe }}</style>
</head>
<body>
<header>
<h1>プロフィール帳</h1>
<p>profilebook ― 懐かしのプロフィール帳を、ブラウザで書けるようにしました</p>
</header>
<main>
{{ body|safe }}
</main>
<footer>書いた内容はお使いのブラウザの中だけに保存されます。</footer>
<script>{{ script|safe }}</script>
</body>
</html>
"""


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok", "questions": len(QUESTIONS)})


@app.route("/")
def index():
    return render_template_string(BASE, title="プロフィール帳", body=BODY, css=CSS, script=SCRIPT)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
