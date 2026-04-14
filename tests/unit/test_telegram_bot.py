import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.task import Task, TaskStatus


@pytest.fixture
def bot_setup():
    from interfaces.telegram_bot import TelegramBot

    mock_db = AsyncMock()
    mock_orch = AsyncMock()

    with patch("interfaces.telegram_bot.Application") as MockApp:
        mock_app_instance = MagicMock()
        mock_app_instance.bot = AsyncMock()
        MockApp.builder.return_value.token.return_value.build.return_value = mock_app_instance

        bot = TelegramBot(db=mock_db, orchestrator=mock_orch)
        bot._app = mock_app_instance
        yield bot, mock_db, mock_orch, mock_app_instance


def _make_update(text: str = "hello", chat_id: int = 123456789) -> MagicMock:
    update = MagicMock()
    update.message.text = text
    update.message.reply_text = AsyncMock()
    update.effective_chat.id = chat_id
    return update


def _make_callback(data: str, chat_id: int = 123456789) -> MagicMock:
    query = MagicMock()
    query.data = data
    query.answer = AsyncMock()
    query.edit_message_text = AsyncMock()
    update = MagicMock()
    update.callback_query = query
    update.effective_chat.id = chat_id
    return update


@pytest.mark.asyncio
async def test_start_command_replies(bot_setup):
    bot, db, orch, _ = bot_setup
    update = _make_update()
    await bot._cmd_start(update, None)
    update.message.reply_text.assert_called_once()
    assert "Monarch AI" in update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_tasks_command_no_tasks(bot_setup):
    bot, mock_db, _, _ = bot_setup
    mock_db.list_active_tasks = AsyncMock(return_value=[])
    update = _make_update()
    await bot._cmd_tasks(update, None)
    update.message.reply_text.assert_called_once()
    assert "No active" in update.message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_tasks_command_with_tasks(bot_setup):
    bot, mock_db, _, _ = bot_setup
    task = Task(raw_input="build login")
    mock_db.list_active_tasks = AsyncMock(return_value=[task])
    update = _make_update()
    await bot._cmd_tasks(update, None)
    text = update.message.reply_text.call_args[0][0]
    assert task.task_id in text


@pytest.mark.asyncio
async def test_handle_task_input_creates_task(bot_setup):
    bot, db, mock_orch, _ = bot_setup
    mock_orch.run = AsyncMock(return_value=MagicMock(
        status=TaskStatus.DONE, pr_url=None, task_id="monarch-abc"
    ))
    update = _make_update(text="add pagination to /users")
    with patch("interfaces.telegram_bot.asyncio.create_task"):
        await bot._handle_task_input(update, None)
    update.message.reply_text.assert_called_once()
    text = update.message.reply_text.call_args[0][0]
    assert "monarch-" in text


@pytest.mark.asyncio
async def test_approve_callback(bot_setup):
    bot, db, mock_orch, _ = bot_setup
    mock_orch.approve_task = AsyncMock()
    update = _make_callback("approve:monarch-xyz")
    await bot._handle_callback(update, None)
    mock_orch.approve_task.assert_called_once_with("monarch-xyz")
    update.callback_query.edit_message_text.assert_called_once()


@pytest.mark.asyncio
async def test_reject_callback(bot_setup):
    bot, db, mock_orch, _ = bot_setup
    mock_orch.reject_task = AsyncMock()
    update = _make_callback("reject:monarch-xyz")
    await bot._handle_callback(update, None)
    mock_orch.reject_task.assert_called_once_with("monarch-xyz")


@pytest.mark.asyncio
async def test_send_approval_request(bot_setup):
    bot, _, _, mock_app_instance = bot_setup
    mock_app_instance.bot.send_message = AsyncMock()
    await bot.send_approval_request("monarch-1", "post_planning", "Build search feature")
    mock_app_instance.bot.send_message.assert_called_once()
    call_kwargs = mock_app_instance.bot.send_message.call_args[1]
    assert "monarch-1" in call_kwargs["text"]
    assert "reply_markup" in call_kwargs
