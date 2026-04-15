"""Initial schema for Monarch Phase 1 core API."""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_units",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_business_units_slug", "business_units", ["slug"], unique=False)

    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("business_unit_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("project_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("stage", sa.String(length=40), nullable=False),
        sa.Column("source_path", sa.Text(), nullable=True),
        sa.Column("repo_url", sa.Text(), nullable=True),
        sa.Column("main_goal", sa.Text(), nullable=True),
        sa.Column("current_focus", sa.Text(), nullable=True),
        sa.Column("next_action", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["business_unit_id"], ["business_units.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_projects_business_unit_id", "projects", ["business_unit_id"], unique=False)
    op.create_index("ix_projects_priority", "projects", ["priority"], unique=False)
    op.create_index("ix_projects_slug", "projects", ["slug"], unique=False)
    op.create_index("ix_projects_status", "projects", ["status"], unique=False)

    op.create_table(
        "ideas",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("raw_input", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("classification", sa.String(length=40), nullable=True),
        sa.Column("business_unit_id", sa.Uuid(), nullable=True),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("priority_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["business_unit_id"], ["business_units.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ideas_business_unit_id", "ideas", ["business_unit_id"], unique=False)
    op.create_index("ix_ideas_classification", "ideas", ["classification"], unique=False)
    op.create_index("ix_ideas_project_id", "ideas", ["project_id"], unique=False)
    op.create_index("ix_ideas_status", "ideas", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_ideas_status", table_name="ideas")
    op.drop_index("ix_ideas_project_id", table_name="ideas")
    op.drop_index("ix_ideas_classification", table_name="ideas")
    op.drop_index("ix_ideas_business_unit_id", table_name="ideas")
    op.drop_table("ideas")
    op.drop_index("ix_projects_status", table_name="projects")
    op.drop_index("ix_projects_slug", table_name="projects")
    op.drop_index("ix_projects_priority", table_name="projects")
    op.drop_index("ix_projects_business_unit_id", table_name="projects")
    op.drop_table("projects")
    op.drop_index("ix_business_units_slug", table_name="business_units")
    op.drop_table("business_units")
