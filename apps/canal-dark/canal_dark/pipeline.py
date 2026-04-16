from __future__ import annotations

from canal_dark.models import ChannelBrief, ScriptDraft, TopicIdea


def build_topic_backlog(brief: ChannelBrief) -> list[TopicIdea]:
    themes = brief.themes or ["curiosidades", "ranking", "historia", "comparacao"]
    references = brief.references or [brief.niche]
    backlog: list[TopicIdea] = []

    for index, theme in enumerate(themes):
        reference = references[index % len(references)]
        backlog.append(
            TopicIdea(
                title=f"{theme.title()} de {brief.niche}",
                hook=f"Pouca gente percebe isto sobre {brief.niche.lower()}.",
                theme=theme,
                angle=(
                    f"Usar a referencia {reference.lower()} para contar uma historia curta "
                    f"que reforce a promessa: {brief.promise.lower()}."
                ),
            )
        )

    return backlog


def choose_priority_topic(backlog: list[TopicIdea]) -> TopicIdea:
    if not backlog:
        raise ValueError("Backlog nao pode estar vazio.")
    return backlog[0]


def build_script_draft(topic: TopicIdea, brief: ChannelBrief) -> ScriptDraft:
    return ScriptDraft(
        title=topic.title,
        opening=topic.hook,
        beats=[
            f"Apresentar o contexto para {brief.audience.lower()} em uma frase direta.",
            f"Desenvolver o angulo central: {topic.angle}",
            "Encerrar com uma revelacao, comparacao ou virada que estimule retencao.",
        ],
        closing=f"Fechar reforcando a promessa principal: {brief.promise}.",
    )


def render_script(script: ScriptDraft) -> str:
    lines = [
        f"# {script.title}",
        "",
        "## Abertura",
        "",
        script.opening,
        "",
        "## Desenvolvimento",
        "",
    ]
    lines.extend(f"- {beat}" for beat in script.beats)
    lines.extend(
        [
            "",
            "## Fechamento",
            "",
            script.closing,
        ]
    )
    return "\n".join(lines).strip() + "\n"
