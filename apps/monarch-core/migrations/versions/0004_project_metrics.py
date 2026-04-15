"""Add project metrics table."""

from alembic import op
import sqlalchemy as sa


revision = "0004_project_metrics"
down_revision = "0003_executions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_metrics",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("metric_name", sa.String(length=120), nullable=False),
        sa.Column("metric_value", sa.Float(), nullable=False),
        sa.Column("metric_unit", sa.String(length=40), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_metrics_metric_name", "project_metrics", ["metric_name"], unique=False)
    op.create_index("ix_project_metrics_project_id", "project_metrics", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_project_metrics_project_id", table_name="project_metrics")
    op.drop_index("ix_project_metrics_metric_name", table_name="project_metrics")
    op.drop_table("project_metrics")
