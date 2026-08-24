from pathlib import Path

from hermes.skills import SkillLibrary


def test_save_and_match_by_trigger(tmp_path: Path):
    lib = SkillLibrary(path=tmp_path / "skills.json")
    lib.save_skill(
        name="release_build",
        description="Android 릴리즈 빌드를 생성한다",
        steps=["gradlew assembleRelease 실행", "apk 서명 확인"],
        triggers=["release build", "릴리즈 빌드"],
    )

    match = lib.match("릴리즈 빌드 해줘")
    assert match is not None
    assert match["name"] == "release_build"


def test_no_match_when_no_trigger_hits(tmp_path: Path):
    lib = SkillLibrary(path=tmp_path / "skills.json")
    lib.save_skill(name="foo", description="d", steps=[], triggers=["foo"])

    assert lib.match("전혀 관련 없는 요청") is None


def test_mark_used_increments_usage_count(tmp_path: Path):
    lib = SkillLibrary(path=tmp_path / "skills.json")
    lib.save_skill(name="foo", description="d", steps=[], triggers=["foo"])

    lib.mark_used("foo")
    lib.mark_used("foo")

    assert lib.find_by_name("foo")["usage_count"] == 2


def test_save_skill_updates_existing_by_name(tmp_path: Path):
    lib = SkillLibrary(path=tmp_path / "skills.json")
    lib.save_skill(name="foo", description="v1", steps=["a"], triggers=["foo"])
    lib.save_skill(name="foo", description="v2", steps=["a", "b"], triggers=["foo", "bar"])

    assert len(lib.skills) == 1
    assert lib.find_by_name("foo")["description"] == "v2"
    assert lib.find_by_name("foo")["steps"] == ["a", "b"]
