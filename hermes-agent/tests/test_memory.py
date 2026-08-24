from pathlib import Path

from hermes.memory import Memory


def test_remember_persists_across_instances(tmp_path: Path):
    path = tmp_path / "memory.json"
    mem = Memory(path=path)
    mem.remember("사용자는 Kotlin으로 Android 앱을 개발한다", tags=["profile"])
    assert path.exists()

    reloaded = Memory(path=path)
    assert len(reloaded.entries) == 1
    assert reloaded.entries[0]["fact"] == "사용자는 Kotlin으로 Android 앱을 개발한다"


def test_search_matches_fact_or_tag(tmp_path: Path):
    mem = Memory(path=tmp_path / "memory.json")
    mem.remember("좋아하는 언어는 Kotlin", tags=["language"])
    mem.remember("싫어하는 언어는 없음")

    results = mem.search("kotlin")
    assert len(results) == 1
    assert results[0]["fact"].startswith("좋아하는")


def test_as_context_empty_when_no_entries(tmp_path: Path):
    mem = Memory(path=tmp_path / "memory.json")
    assert mem.as_context() == "(기억된 내용 없음)"
