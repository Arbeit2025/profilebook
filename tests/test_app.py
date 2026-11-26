import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as m


client = m.app.test_client()

FIELD_LABELS = [
    "なまえ", "ニックネーム", "誕生日", "血液型", "好きな食べ物", "好きな色",
    "好きな音楽・歌手", "趣味", "特技", "将来の夢", "今ほしいもの", "一言メッセージ",
]


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"
    assert data["questions"] == len(m.QUESTIONS)


def test_question_pool_size():
    assert len(m.QUESTIONS) >= 20
    assert len(set(m.QUESTIONS)) == len(m.QUESTIONS)


def test_index_ok_and_has_form_fields():
    r = client.get("/")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    for label in FIELD_LABELS:
        assert label in html
    # 血液型の選択肢
    for blood in ["A型", "B型", "O型", "AB型"]:
        assert blood in html
    # ボタン類
    assert "お題をシャッフル" in html
    assert "文章でコピー" in html
    assert "全部消す" in html
    assert "ランダムお題" in html


def test_index_embeds_full_question_pool():
    html = client.get("/").get_data(as_text=True)
    for q in m.QUESTIONS:
        assert q in html


def test_index_has_preview_and_storage():
    html = client.get("/").get_data(as_text=True)
    assert "プレビュー" in html
    assert "localStorage" in html


def test_script_not_escaped():
    # render_template_string で JS が HTML エスケープされると全機能が死ぬ（過去の事故）。
    html = client.get("/").get_data(as_text=True)
    assert "&#39;" not in html
    assert "var STORAGE_KEY = 'profilebook-v1';" in html
    assert "navigator.clipboard.writeText(text).then(done, done)" in html
