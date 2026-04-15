"""Add executions table."""

from alembic import op
import sqlalchemy as sa


revision = "0003_executions"
down_revision = "0002_tasks_and_approvals"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "executions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=True),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("execution_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("input_payload", sa.Text(), nullable=True),
        sa.Column("output_summary", sa.Text(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_executions_project_id", "executions", ["project_id"], unique=False)
    op.create_index("ix_executions_status", "executions", ["status"], unique=False)
    op.create_index("ix_executions_task_id", "executions", ["task_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_executions_task_id", table_name="executions")
    op.drop_index("ix_executions_status", table_name="executions")
    op.drop_index("ix_executions_project_id", table_name="executions")
    op.drop_table("executions")
