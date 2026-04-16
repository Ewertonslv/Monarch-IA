"""Canal Dark — produza pautas e roteiros para canais dark."""
from canal_dark.models import ChannelBrief, ScriptDraft, TopicIdea
from canal_dark.pipeline import build_script_draft, build_topic_backlog, choose_priority_topic, render_script

__all__ = ["ChannelBrief", "TopicIdea", "ScriptDraft", "build_topic_backlog", "choose_priority_topic", "build_script_draft", "render_script"]
