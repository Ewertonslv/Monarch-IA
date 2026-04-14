import asyncio
import logging
from typing import Any

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from config import config
from core.orchestrator import Orchestrator
from core.task import Task, TaskStatus
from storage.database import Database

logger = logging.getLogger(__name__)

_APPROVAL_PREFIX = "approve:"
_REJECTION_PREFIX = "reject:"


class TelegramBot:
    """Telegram interface for Monarch AI — task submission and approval gates."""

    def __init__(self, db: Database, orchestrator: Orchestrator) -> None:
        self.db = db
        self.orchestrator = orchestrator
        self._app: Application | None = None

    def build_app(self) -> Application:
        self._app = (
            Application.builder()
            .token(config.telegram_bot_token)
            .build()
        )
        self._app.add_handler(CommandHandler("start", self._cmd_start))
        self._app.add_handler(CommandHandler("tasks", self._cmd_tasks))
        self._app.add_handler(CommandHandler("help", self._cmd_help))
        self._app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_task_input)
        )
        self._app.add_handler(CallbackQueryHandler(self._handle_callback))
        return self._app

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    async def _cmd_start(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "👑 *Monarch AI* — Multi-agent development pipeline\n\n"
            "Send me a feature description to kick off a task.\n"
            "Use /tasks to see active tasks.\n"
            "Use /help for more info.",
            parse_mode="Markdown",
        )

    async def _cmd_help(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "*Commands:*\n"
            "/start — Welcome message\n"
            "/tasks — List active tasks\n"
            "/help — This message\n\n"
            "*Usage:* Just type your feature request and I'll start the pipeline!",
            parse_mode="Markdown",
        )

    async def _cmd_tasks(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        tasks = await self.db.list_active_tasks()
        if not tasks:
            await update.message.reply_text("No active tasks.")
            return
        lines = []
        for t in tasks:
            emoji = _status_emoji(t.status)
            lines.append(f"{emoji} `{t.task_id}` — {t.raw_input[:50]}")
        await update.message.reply_text(
            "*Active Tasks:*\n" + "\n".join(lines),
            parse_mode="Markdown",
        )

    # ------------------------------------------------------------------
    # Task input
    # ------------------------------------------------------------------

    async def _handle_task_input(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        raw_input = update.message.text.strip()
        task = Task(raw_input=raw_input)
        await update.message.reply_text(
            f"🚀 Task `{task.task_id}` created.\nStarting pipeline…",
            parse_mode="Markdown",
        )
        asyncio.create_task(self._run_task(task, update.effective_chat.id))

    async def _run_task(self, task: Task, chat_id: int) -> None:
        try:
            result = await self.orchestrator.run(task)
            emoji = _status_emoji(result.status)
            msg = (
                f"{emoji} Task `{task.task_id}` finished: *{result.status.value}*\n"
            )
            if result.pr_url:
                msg += f"🔗 PR: {result.pr_url}"
            await self._send(chat_id, msg)
        except Exception as exc:
            logger.exception("Task failed: %s", task.task_id)
            await self._send(chat_id, f"❌ Task `{task.task_id}` failed: {exc}")

    # ------------------------------------------------------------------
    # Approval callbacks
    # ------------------------------------------------------------------

    async def _handle_callback(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        data: str = query.data

        if data.startswith(_APPROVAL_PREFIX):
            task_id = data[len(_APPROVAL_PREFIX):]
            await self.orchestrator.approve_task(task_id)
            await query.edit_message_text(f"✅ Task `{task_id}` *approved*.", parse_mode="Markdown")

        elif data.startswith(_REJECTION_PREFIX):
            task_id = data[len(_REJECTION_PREFIX):]
            await self.orchestrator.reject_task(task_id)
            await query.edit_message_text(f"❌ Task `{task_id}` *rejected*.", parse_mode="Markdown")

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    async def send_approval_request(self, task_id: str, stage: str, summary: str) -> None:
        """Send an approval keyboard to the configured Telegram chat."""
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"{_APPROVAL_PREFIX}{task_id}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"{_REJECTION_PREFIX}{task_id}"),
            ]
        ])
        text = (
            f"⏳ *Approval required* — stage: `{stage}`\n\n"
            f"Task: `{task_id}`\n"
            f"{summary}"
        )
        await self._send(int(config.telegram_chat_id), text, reply_markup=keyboard)

    async def _send(
        self,
        chat_id: int,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
    ) -> None:
        assert self._app is not None
        kwargs: dict[str, Any] = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        if reply_markup:
            kwargs["reply_markup"] = reply_markup
        await self._app.bot.send_message(**kwargs)

    async def start_polling(self) -> None:
        app = self.build_app()
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        logger.info("Telegram bot polling started")

    async def stop(self) -> None:
        if self._app:
            await self._app.updater.stop()
            await self._app.stop()
            await self._app.shutdown()


def _status_emoji(status: TaskStatus) -> str:
    return {
        TaskStatus.PENDING: "⏳",
        TaskStatus.RUNNING: "⚙️",
        TaskStatus.AWAITING_APPROVAL: "🔔",
        TaskStatus.DONE: "✅",
        TaskStatus.FAILED: "❌",
        TaskStatus.DISCARDED: "🗑️",
    }.get(status, "❓")
