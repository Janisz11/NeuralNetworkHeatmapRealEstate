from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "apartments",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lon", sa.Float, nullable=False),
        sa.Column("price_per_m2", sa.Float, nullable=False),
        sa.Column("area_m2", sa.Float, nullable=False),
        sa.Column("floor", sa.Integer, nullable=False),
        sa.Column("build_year", sa.Integer, nullable=False),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "model_runs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("epochs", sa.Integer, nullable=False),
        sa.Column("learning_rate", sa.Float, nullable=False),
        sa.Column("hidden_layers", sa.Text, nullable=False, server_default="[64, 32]"),
        sa.Column("mse_loss", sa.Float, nullable=True),
        sa.Column("r2_score", sa.Float, nullable=True),
        sa.Column("weights_path", sa.String(500), nullable=True),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("picture", sa.String(500), nullable=True),
        sa.Column("provider", sa.String(50), server_default="google"),
        sa.Column("provider_id", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), server_default="admin"),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("model_runs")
    op.drop_table("apartments")
