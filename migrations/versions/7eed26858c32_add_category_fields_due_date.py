"""add_category_fields_due_date

Revision ID: 7eed26858c32
Revises: f278000b4812
Create Date: 2026-05-10 07:20:58.616763

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7eed26858c32'
down_revision = 'f278000b4812'
branch_labels = None
depends_on = None


def upgrade():
    # Drop category_item table (unused) - may not exist in all environments
    try:
        op.drop_table('category_item')
    except Exception:
        pass

    with op.batch_alter_table('category', schema=None) as batch_op:
        # Add user_id as nullable first so existing rows don't fail
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('icon', sa.String(length=50), nullable=True, server_default='fa-folder'))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('archived', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True, server_default=sa.text('NOW()')))
        # Drop the old unique index on name (if it exists)
        try:
            batch_op.drop_index('name')
        except Exception:
            pass

    # Backfill user_id: assign all existing categories to the first user in the DB
    bind = op.get_bind()
    first_user = bind.execute(sa.text('SELECT id FROM user ORDER BY id LIMIT 1')).fetchone()
    if first_user:
        bind.execute(
            sa.text('UPDATE category SET user_id = :uid WHERE user_id IS NULL'),
            {'uid': first_user[0]}
        )

    # Now set NOT NULL and add FK
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.alter_column('user_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key('fk_category_user_id', 'user', ['user_id'], ['id'])

    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('due_date', sa.Date(), nullable=True))


def downgrade():
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_column('due_date')

    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_constraint('fk_category_user_id', type_='foreignkey')
        batch_op.create_index('name', ['name'], unique=True)
        batch_op.drop_column('created_at')
        batch_op.drop_column('archived')
        batch_op.drop_column('description')
        batch_op.drop_column('icon')
        batch_op.drop_column('user_id')

    op.create_table('category_item',
        sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('title', mysql.VARCHAR(length=100), nullable=False),
        sa.Column('selected', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
        sa.Column('category_id', mysql.INTEGER(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], name=op.f('category_item_ibfk_1')),
        sa.PrimaryKeyConstraint('id'),
        mysql_collate='utf8mb4_0900_ai_ci',
        mysql_default_charset='utf8mb4',
        mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
