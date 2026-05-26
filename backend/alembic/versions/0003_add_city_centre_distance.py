from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("apartments", sa.Column("centre_distance", sa.Float(), nullable=True))
    op.add_column("apartments", sa.Column("city", sa.String(100), nullable=True))
    op.create_index("ix_apartments_city", "apartments", ["city"])
    op.drop_column("apartments", "district")


def downgrade() -> None:
    op.add_column("apartments", sa.Column("district", sa.String(100), nullable=True))
    op.drop_index("ix_apartments_city", table_name="apartments")
    op.drop_column("apartments", "city")
    op.drop_column("apartments", "centre_distance")
