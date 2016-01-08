"""add interpreted age tables

Revision ID: 3874acf6600c
Revises: 3f5681f0fc5d
Create Date: 2015-06-19 13:46:19.937856

"""

# revision identifiers, used by Alembic.
revision = '3874acf6600c'
down_revision = '3f5681f0fc5d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('InterpretedAgeTbl',
                    sa.Column('idinterpretedagetbl', sa.Integer(), nullable=False),
                    sa.Column('age_kind', sa.String(length=32), nullable=True),
                    sa.Column('kca_kind', sa.String(length=32), nullable=True),
                    sa.Column('age', sa.Float(), nullable=True),
                    sa.Column('age_err', sa.Float(), nullable=True),
                    sa.Column('display_age_units', sa.String(length=2), nullable=True),
                    sa.Column('kca', sa.Float(), nullable=True),
                    sa.Column('kca_err', sa.Float(), nullable=True),
                    sa.Column('mswd', sa.Float(), nullable=True),
                    sa.Column('age_error_kind', sa.String(length=80), nullable=True),
                    sa.Column('include_j_error_in_mean', sa.Boolean(), nullable=True),
                    sa.Column('include_j_error_in_plateau', sa.Boolean(), nullable=True),
                    sa.Column('include_j_error_in_individual_analyses', sa.Boolean(), nullable=True),
                    sa.PrimaryKeyConstraint('idinterpretedagetbl')
                    )
    # op.create_table('LoadPositionTbl',
    # sa.Column('idloadpositionTbl', sa.Integer(), nullable=False),
    # sa.Column('identifier', sa.String(length=45), nullable=True),
    # sa.Column('position', sa.Integer(), nullable=True),
    # sa.Column('loadName', sa.String(length=45), nullable=True),
    # sa.Column('weight', sa.Float(), nullable=True),
    # sa.Column('note', sa.BLOB(), nullable=True),
    # sa.ForeignKeyConstraint(['identifier'], ['IrradiationPositionTbl.identifier'], ),
    # sa.ForeignKeyConstraint(['loadName'], ['LoadTbl.name'], ),
    # sa.PrimaryKeyConstraint('idloadpositionTbl')
    # )
    # op.create_table('MeasuredPositionTbl',
    # sa.Column('idmeasuredpositionTbl', sa.Integer(), nullable=False),
    # sa.Column('position', sa.Integer(), nullable=True),
    # sa.Column('x', sa.Float(), nullable=True),
    # sa.Column('y', sa.Float(), nullable=True),
    # sa.Column('z', sa.Float(), nullable=True),
    # sa.Column('is_degas', sa.Boolean(), nullable=True),
    # sa.Column('analysisID', sa.Integer(), nullable=True),
    # sa.Column('loadName', sa.String(length=45), nullable=True),
    # sa.ForeignKeyConstraint(['analysisID'], ['AnalysisTbl.idanalysisTbl'], ),
    # sa.ForeignKeyConstraint(['loadName'], ['LoadTbl.name'], ),
    # sa.PrimaryKeyConstraint('idmeasuredpositionTbl')
    # )
    op.create_table('InterpretedAgeSetTbl',
                    sa.Column('idinterpretedagesettbl', sa.Integer(), nullable=False),
                    sa.Column('interpreted_ageID', sa.Integer(), nullable=True),
                    sa.Column('analysisID', sa.Integer(), nullable=True),
                    sa.Column('forced_plateau_step', sa.Boolean(), nullable=True),
                    sa.Column('plateau_step', sa.Boolean(), nullable=True),
                    sa.Column('tag', sa.String(length=80), nullable=True),
                    sa.ForeignKeyConstraint(['analysisID'], ['AnalysisTbl.idanalysisTbl'], ),
                    sa.ForeignKeyConstraint(['interpreted_ageID'], ['InterpretedAgeTbl.idinterpretedagetbl'], ),
                    sa.PrimaryKeyConstraint('idinterpretedagesettbl')
                    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('InterpretedAgeSetTbl')
    # op.drop_table('MeasuredPositionTbl')
    # op.drop_table('LoadPositionTbl')
    op.drop_table('InterpretedAgeTbl')
    ### end Alembic commands ###