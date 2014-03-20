# Copyright 2014 - Rackspace US, Inc.
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

from solum.objects import registry
from solum.objects.sqlalchemy import language_pack as lp
from solum.tests import base
from solum.tests import utils


class TestLanguagePack(base.BaseTestCase):
    def setUp(self):
        super(TestLanguagePack, self).setUp()
        self.db = self.useFixture(utils.Database())
        self.ctx = utils.dummy_context()

        attr_dict = {}
        attr_dict["runtime_versions"] = ["1.6", "1.7"]
        attr_dict["build_tool_chain"] = [{"type": "ant", "version": "1.7"},
                                         {"type": "maven", "version": "1.2"}]
        attr_dict["attributes"] = {"optional_attr1": "value",
                                   "admin_email": "someadmin@somewhere.com"}

        self.data = [{'project_id': 'test_id',
                      'user_id': 'fred',
                      'uuid': '123456789abcdefghi',
                      'name': 'languagepack1',
                      'description': 'test language pack',
                      'attr_blob': attr_dict}]

        utils.create_models_from_data(lp.LanguagePack, self.data, self.ctx)

    def test_objects_registered(self):
        self.assertTrue(registry.LanguagePack)
        self.assertTrue(registry.LanguagePackList)

    def test_get_all(self):
        lst = lp.LanguagePackList()
        self.assertEqual(1, len(lst.get_all(self.ctx)))

    def test_check_data(self):
        test_lp = lp.LanguagePack().get_by_id(self.ctx, self.data[0]['id'])
        for key, value in self.data[0].items():
            self.assertEqual(value, getattr(test_lp, key))

    def test_create(self):
        test_lp = lp.LanguagePack()
        test_lp.update(self.data[0])
        test_lp.uuid = '1234'
        test_lp.user_id = self.ctx.user
        test_lp.project_id = self.ctx.tenant
        test_lp.create(self.ctx)
        self.assertIsNotNone(test_lp.service_id)
