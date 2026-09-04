"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-04

MySQL 5.0 compatible: DATETIME (no fractional seconds), utf8, no JSON columns.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_departments_code", "departments", ["code"])

    op.create_table(
        "trains",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("train_number", sa.String(length=16), nullable=False),
        sa.Column("train_name", sa.String(length=128), nullable=False),
        sa.Column("train_type", sa.String(length=16), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("operating_status", sa.String(length=16), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("train_number"),
    )
    op.create_index("ix_trains_train_number", "trains", ["train_number"])
    op.create_index("ix_trains_train_type", "trains", ["train_type"])
    op.create_index("ix_trains_priority", "trains", ["priority"])

    op.create_table(
        "maintenance_blocks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("block_code", sa.String(length=64), nullable=False),
        sa.Column("section", sa.String(length=32), nullable=False),
        sa.Column("start_time", sa.DateTime(), nullable=False),
        sa.Column("end_time", sa.DateTime(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("block_type", sa.String(length=32), nullable=False),
        sa.Column("optimization_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("block_code"),
    )
    op.create_index("ix_maintenance_blocks_section", "maintenance_blocks", ["section"])
    op.create_index("ix_maintenance_blocks_status", "maintenance_blocks", ["status"])
    op.create_index("ix_maintenance_blocks_block_code", "maintenance_blocks", ["block_code"])

    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("asset_code", sa.String(length=64), nullable=False),
        sa.Column("asset_type", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("section", sa.String(length=32), nullable=False),
        sa.Column("location", sa.String(length=128), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("installation_date", sa.Date(), nullable=True),
        sa.Column("last_maintenance_date", sa.Date(), nullable=True),
        sa.Column("next_maintenance_due", sa.Date(), nullable=True),
        sa.Column("condition_score", sa.Float(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("criticality", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("asset_code"),
    )
    op.create_index("ix_assets_asset_code", "assets", ["asset_code"])
    op.create_index("ix_assets_section", "assets", ["section"])
    op.create_index("ix_assets_department_id", "assets", ["department_id"])
    op.create_index("ix_assets_criticality", "assets", ["criticality"])
    op.create_index("ix_assets_status", "assets", ["status"])

    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("resource_code", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=32), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("available_from", sa.DateTime(), nullable=True),
        sa.Column("available_until", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("resource_code"),
    )
    op.create_index("ix_resources_resource_code", "resources", ["resource_code"])
    op.create_index("ix_resources_resource_type", "resources", ["resource_type"])
    op.create_index("ix_resources_department_id", "resources", ["department_id"])
    op.create_index("ix_resources_section", "resources", ["section"])
    op.create_index("ix_resources_status", "resources", ["status"])

    op.create_table(
        "maintenance_tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_code", sa.String(length=64), nullable=False),
        sa.Column("asset_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("source_system", sa.String(length=16), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("section", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.String(length=16), nullable=False),
        sa.Column("estimated_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("required_resource_type", sa.String(length=64), nullable=True),
        sa.Column("risk_score", sa.Float(), nullable=True),
        sa.Column("block_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["block_id"], ["maintenance_blocks.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_code"),
    )
    op.create_index("ix_maintenance_tasks_task_code", "maintenance_tasks", ["task_code"])
    op.create_index("ix_maintenance_tasks_asset_id", "maintenance_tasks", ["asset_id"])
    op.create_index("ix_maintenance_tasks_department_id", "maintenance_tasks", ["department_id"])
    op.create_index("ix_maintenance_tasks_source_system", "maintenance_tasks", ["source_system"])
    op.create_index("ix_maintenance_tasks_section", "maintenance_tasks", ["section"])
    op.create_index("ix_maintenance_tasks_priority", "maintenance_tasks", ["priority"])
    op.create_index("ix_maintenance_tasks_due_date", "maintenance_tasks", ["due_date"])
    op.create_index("ix_maintenance_tasks_status", "maintenance_tasks", ["status"])
    op.create_index("ix_maintenance_tasks_block_id", "maintenance_tasks", ["block_id"])

    op.create_table(
        "train_schedules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("train_id", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=32), nullable=False),
        sa.Column("arrival_time", sa.DateTime(), nullable=False),
        sa.Column("departure_time", sa.DateTime(), nullable=False),
        sa.Column("schedule_date", sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(["train_id"], ["trains.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_train_schedules_train_id", "train_schedules", ["train_id"])
    op.create_index("ix_train_schedules_section", "train_schedules", ["section"])
    op.create_index("ix_train_schedules_schedule_date", "train_schedules", ["schedule_date"])

    op.create_table(
        "weather_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("section", sa.String(length=32), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("weather_type", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("rainfall", sa.Float(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("visibility", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weather_records_section", "weather_records", ["section"])
    op.create_index("ix_weather_records_date", "weather_records", ["date"])
    op.create_index("ix_weather_records_weather_type", "weather_records", ["weather_type"])


def downgrade() -> None:
    op.drop_table("weather_records")
    op.drop_table("train_schedules")
    op.drop_table("maintenance_tasks")
    op.drop_table("resources")
    op.drop_table("assets")
    op.drop_table("maintenance_blocks")
    op.drop_table("trains")
    op.drop_table("departments")
