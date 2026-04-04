"""merge migration heads

Revision ID: 926fd9a286a1
Revises: 6a60a03fb87c, 706b7a1ca5fa, cfb28b567219, ed90e418d416
Create Date: 2026-04-04 07:25:59.861535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '926fd9a286a1'
down_revision = ('6a60a03fb87c', '706b7a1ca5fa', 'cfb28b567219', 'ed90e418d416')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
