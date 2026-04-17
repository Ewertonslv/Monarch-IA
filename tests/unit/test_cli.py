from interfaces.cli import (
    _build_project_brief,
    _detect_project_profile,
    _list_project_profiles_text,
    _prepare_pipeline_input,
)


def test_build_project_brief_for_instagram_ideation() -> None:
    brief = _build_project_brief(
        "instagram",
        "quero vender servicos e PDFs com conteudo de IA",
        "ideation",
    )
    assert "Projeto alvo: Instagram Automation" in brief
    assert "Modo desejado: ideation" in brief
    assert "Nao implemente codigo." in brief
    assert "PDF Factory" in brief
    assert "regras de aprovacao no Telegram" in brief
    assert "quero vender servicos e PDFs com conteudo de IA" in brief
    assert "Focos de backlog: pilares de conteudo; calendario editorial; CTAs por tipo de post; ofertas iniciais; aprovacao humana antes de publicar" in brief


def test_prepare_pipeline_input_uses_profile_when_present() -> None:
    prepared = _prepare_pipeline_input(
        "incube um canal dark com afiliados",
        "incubation",
        "canal-dark",
    )
    assert "Projeto alvo: Canal Dark" in prepared
    assert "Modo desejado: incubation" in prepared
    assert "incube um canal dark com afiliados" in prepared
    assert "Trilhas sugeridas: fonte; cortes; publicacao-automatica; descricao; monetizacao" in prepared
    assert "Estruture o backlog por trilhas nomeadas e bem separadas" in prepared
    assert "regras para alternar entre descricao de views e descricao de venda" in prepared


def test_prepare_pipeline_input_returns_normalized_prompt_without_profile() -> None:
    prepared = _prepare_pipeline_input(
        "orquestrador: gerar ideias para meu projeto",
        "ideation",
        None,
    )
    assert prepared == "gerar ideias para meu projeto"


def test_detect_project_profile_from_prompt_keywords() -> None:
    assert _detect_project_profile("quero crescer um instagram sobre IA") == "instagram"
    assert _detect_project_profile("canal dark com cortes diarios e afiliados") == "canal-dark"


def test_prepare_pipeline_input_auto_detects_project_profile() -> None:
    prepared = _prepare_pipeline_input(
        "quero um canal dark de cortes diarios com afiliados",
        "incubation",
        None,
    )
    assert "Projeto alvo: Canal Dark" in prepared
    assert "Modo desejado: incubation" in prepared


def test_list_project_profiles_text_mentions_examples() -> None:
    profiles_text = _list_project_profiles_text()
    assert "instagram: Instagram Automation" in profiles_text
    assert "trilhas: conteudo, oferta, automacao-aprovada, metricas" in profiles_text
    assert 'monarch incubate "perfil de instagram sobre IA com aprovacao via Telegram antes de publicar e foco em vender servicos, automacoes e PDFs" --project instagram' in profiles_text
