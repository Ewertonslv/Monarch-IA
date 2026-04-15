"""Add agent profiles and roadmap items tables."""

from alembic import op
import sqlalchemy as sa


revision = "0005_agents_and_roadmap"
down_revision = "0004_project_metrics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column("capabilities", sa.Text(), nullable=True),
        sa.Column("pipeline_name", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_agent_profiles_pipeline_name", "agent_profiles", ["pipeline_name"], unique=False)
    op.create_index("ix_agent_profiles_slug", "agent_profiles", ["slug"], unique=False)
    op.create_index("ix_agent_profiles_status", "agent_profiles", ["status"], unique=False)

    op.create_table(
        "roadmap_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("phase", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_roadmap_items_phase", "roadmap_items", ["phase"], unique=False)
    op.create_index("ix_roadmap_items_priority", "roadmap_items", ["priority"], unique=False)
    op.create_index("ix_roadmap_items_project_id", "roadmap_items", ["project_id"], unique=False)
    op.create_index("ix_roadmap_items_status", "roadmap_items", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_roadmap_items_status", table_name="roadmap_items")
    op.drop_index("ix_roadmap_items_project_id", table_name="roadmap_items")
    op.drop_index("ix_roadmap_items_priority", table_name="roadmap_items")
    op.drop_index("ix_roadmap_items_phase", table_name="roadmap_items")
    op.drop_table("roadmap_items")

    op.drop_index("ix_agent_profiles_status", table_name="agent_profiles")
    op.drop_index("ix_agent_profiles_slug", table_name="agent_profiles")
    op.drop_index("ix_agent_profiles_pipeline_name", table_name="agent_profiles")
    op.drop_table("agent_profiles")
