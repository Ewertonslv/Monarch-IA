"""Testes para modelos do Canal Dark."""
from canal_dark.models import ChannelBrief, ScriptDraft, TopicIdea
from canal_dark.pipeline import build_topic_backlog, choose_priority_topic, build_script_draft


def test_channel_brief_defaults():
    b = ChannelBrief(niche="teste", audience="pub", promise="promessa")
    assert b.themes == []
    assert b.references == []


def test_topic_idea_fields():
    t = TopicIdea(title="Teste", hook="Hook", theme="curiosidade", angle="Angulo")
    assert t.title == "Teste"
    assert t.hook == "Hook"


def test_script_draft_defaults():
    s = ScriptDraft(title="Teste", opening="Abertura", beats=["B1", "B2"])
    assert s.closing == ""


def test_build_topic_backlog_respects_themes():
    b = ChannelBrief(niche="dark", audience="p", promise="pr", themes=["a", "b"])
    backlog = build_topic_backlog(b)
    assert len(backlog) == 2


def test_choose_priority_topic_returns_first():
    b = ChannelBrief(niche="t", audience="p", promise="pr")
    backlog = build_topic_backlog(b)
    chosen = choose_priority_topic(backlog)
    assert chosen == backlog[0]


def test_build_script_draft_includes_beats():
    b = ChannelBrief(niche="t", audience="p", promise="pr")
    backlog = build_topic_backlog(b)
    script = build_script_draft(backlog[0], b)
    assert script.opening
    assert len(script.beats) == 3
    assert script.closing
