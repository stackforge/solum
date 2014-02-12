#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Add Plan

Revision ID: a42f578cef8
Revises: 594288b1585a
Create Date: 2014-01-24 10:43:32.134145

"""
from alembic import op
import sqlalchemy as sa

from solum.openstack.common import timeutils

# revision identifiers, used by Alembic.
revision = 'a42f578cef8'
down_revision = '594288b1585a'


def upgrade():
    op.create_table(
        'plan',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime, default=timeutils.utcnow),
        sa.Column('updated_at', sa.DateTime, onupdate=timeutils.utcnow),
        sa.Column('project_id', sa.String(length=36)),
        sa.Column('user_id', sa.String(length=36)),
        sa.Column('raw_content', sa.Text),
    )


def downgrade():
    op.drop_table('plan')
