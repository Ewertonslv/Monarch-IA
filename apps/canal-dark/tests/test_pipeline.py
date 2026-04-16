import pytest

from canal_dark.models import ChannelBrief
from canal_dark.pipeline import build_script_draft, build_topic_backlog, choose_priority_topic, render_script


def test_build_topic_backlog_creates_one_topic_per_theme():
    brief = ChannelBrief(
        niche="historias bizarras",
        audience="publico que consome shorts narrativos",
        promise="entregar historias surpreendentes com ritmo rapido",
        themes=["curiosidades", "ranking", "mistérios"],
        references=["reddit", "documentarios"],
    )

    backlog = build_topic_backlog(brief)

    assert len(backlog) == 3
    assert backlog[0].title == "Curiosidades de historias bizarras"


def test_choose_priority_topic_returns_first_item():
    brief = ChannelBrief(
        niche="fatos ocultos",
        audience="curiosos",
        promise="surpreender com fatos pouco conhecidos",
    )

    backlog = build_topic_backlog(brief)

    assert choose_priority_topic(backlog) == backlog[0]


def test_choose_priority_topic_raises_for_empty_backlog():
    with pytest.raises(ValueError):
        choose_priority_topic([])


def test_render_script_contains_sections():
    brief = ChannelBrief(
        niche="lendas urbanas",
        audience="publico de videos curtos",
        promise="reter com suspense e curiosidade",
    )

    script = build_script_draft(choose_priority_topic(build_topic_backlog(brief)), brief)
    markdown = render_script(script)

    assert "## Abertura" in markdown
    assert "## Desenvolvimento" in markdown
    assert "## Fechamento" in markdown
