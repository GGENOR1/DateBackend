"""change type colomn tags

Revision ID: ec49456f4d54
Revises: b1df117fbe22
Create Date: 2024-07-19 17:57:48.523947

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ec49456f4d54'
down_revision = 'b1df117fbe22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('spatial_ref_sys')
    # op.alter_column('user_details', 'tags',
    #            existing_type=postgresql.JSON(astext_type=sa.Text()),
    #            type_=sa.ARRAY(sa.String()),
    #            existing_nullable=True)
    # op.drop_index('idx_user_details_geolocation2', table_name='user_details', postgresql_using='gist')
    # ### end Alembic commands ###

    op.execute("""
        ALTER TABLE user_details 
        ALTER COLUMN tags 
        TYPE VARCHAR[] 
        USING string_to_array(tags::text, ',')
    """)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.create_index('idx_user_details_geolocation2', 'user_details', ['geolocation'], unique=False, postgresql_using='gist')
    # op.alter_column('user_details', 'tags',
    #            existing_type=sa.ARRAY(sa.String()),
    #            type_=postgresql.JSON(astext_type=sa.Text()),
    #            existing_nullable=True)
    op.execute("""
        ALTER TABLE user_details 
        ALTER COLUMN tags 
        TYPE JSON 
        USING array_to_json(tags)
    """)
    # op.create_table('spatial_ref_sys',
    # sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    # sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    # sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    # sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    # sa.CheckConstraint('srid > 0 AND srid <= 998999', name='spatial_ref_sys_srid_check'),
    # sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    # )
    # ### end Alembic commands ###
