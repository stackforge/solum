# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import mock
from oslo.db import exception as db_exc
import pecan
import yaml

from solum.api.controllers.v1.datamodel import plan as planmodel
from solum.api.controllers.v1 import plan
from solum.api.handlers import plan_handler
from solum.common import exception
from solum import objects
from solum.tests import base
from solum.tests import fakes


class TestPlanModuleFunctions(base.BaseTestCase):

    @mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
    def test_yaml_content(self, mock_req):
        m = fakes.FakePlan()
        ref_content = plan.yaml_content(m)
        self.assertEqual(ref_content['uri'], '%s/v1/plans/%s' %
                                             (pecan.request.host_url, m.uuid))

    @mock.patch('solum.api.controllers.v1.plan.init_plan_v1')
    def test_init_plan_by_version(self, init_plan_v1):
        yml_input_plan = {'version': 1, 'name': 'plan1', 'description': 'dsc'}
        plan.init_plan_by_version(yml_input_plan)
        init_plan_v1.assert_called_once()

    @mock.patch('solum.api.controllers.v1.plan.init_plan_v1')
    def test_init_plan_by_version_missing(self, init_plan_v1):
        yml_input_plan = {'name': 'plan1', 'description': 'dsc'}
        self.assertRaises(exception.BadRequest, plan.init_plan_by_version,
                          yml_input_plan)
        init_plan_v1.assert_called_once()

    @mock.patch('solum.api.controllers.v1.plan.init_plan_v1')
    def test_init_plan_by_version_not_existing(self, init_plan_v1):
        yml_input_plan = {'version': 424242424242424242, 'name': 'plan1',
                          'description': 'dsc'}
        self.assertRaises(exception.BadRequest, plan.init_plan_by_version,
                          yml_input_plan)
        init_plan_v1.assert_called_once()

    @mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
    def test_init_plan_v1(self, mock_req):
        yml_input_plan = {'version': 1, 'name': 'plan1', 'description': 'dsc'}
        hand_v1, plan_v1 = plan.init_plan_v1(yml_input_plan)
        self.assertIsInstance(hand_v1, plan_handler.PlanHandler)
        self.assertIsInstance(plan_v1, planmodel.Plan)


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.plan_handler.PlanHandler')
class TestPlanController(base.BaseTestCase):
    def setUp(self):
        super(TestPlanController, self).setUp()
        objects.load()

    def test_plan_get(self, PlanHandler, resp_mock, request_mock):
        hand_get = PlanHandler.return_value.get
        fake_plan = fakes.FakePlan()
        hand_get.return_value = fake_plan
        cont = plan.PlanController('test_id')
        resp = cont.get()
        self.assertIsNotNone(resp)
        resp_yml = yaml.load(resp)
        self.assertEqual(fake_plan.raw_content['name'], resp_yml['name'])
        hand_get.assert_called_with('test_id')
        self.assertEqual(200, resp_mock.status)

    def test_plan_get_not_found(self, PlanHandler, resp_mock, request_mock):
        hand_get = PlanHandler.return_value.get
        hand_get.side_effect = exception.ResourceNotFound(name='plan',
                                                          id='test_id')
        plan.PlanController('test_id').get()
        hand_get.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_plan_put_none(self, PlanHandler, resp_mock, request_mock):
        request_mock.content_type = 'application/x-yaml'
        request_mock.body = ''
        hand_update = PlanHandler.return_value.update
        hand_update.return_value = fakes.FakePlan()
        plan.PlanController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_plan_put_invalid_yaml(self, PlanHandler, resp_mock, request_mock):
        request_mock.content_type = 'application/x-yaml'
        request_mock.body = 'invalid yaml file'
        hand_update = PlanHandler.return_value.update
        hand_update.return_value = fakes.FakePlan()
        plan.PlanController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_plan_put_empty_yaml(self, PlanHandler, resp_mock, request_mock):
        request_mock.content_type = 'application/x-yaml'
        request_mock.body = '{}'
        hand_update = PlanHandler.return_value.update
        hand_update.return_value = fakes.FakePlan()
        plan.PlanController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_plan_put_not_found(self, PlanHandler, resp_mock, request_mock):
        data = 'version: 1\nname: ex_plan1\ndescription: dsc1.'
        request_mock.body = data
        request_mock.content_type = 'application/x-yaml'
        hand_update = PlanHandler.return_value.update
        hand_update.side_effect = exception.ResourceNotFound(
            name='plan', plan_id='test_id')
        plan.PlanController('test_id').put()
        hand_update.assert_called_with('test_id', {'name': 'ex_plan1',
                                                   'description': u'dsc1.'})
        self.assertEqual(404, resp_mock.status)

    def test_plan_put_ok(self, PlanHandler, resp_mock, request_mock):
        data = 'version: 1\nname: ex_plan1\ndescription: dsc1.'
        request_mock.body = data
        request_mock.content_type = 'application/x-yaml'
        hand_update = PlanHandler.return_value.update
        hand_update.return_value = fakes.FakePlan()
        plan.PlanController('test_id').put()
        hand_update.assert_called_with('test_id', {'name': 'ex_plan1',
                                                   'description': u'dsc1.'})
        self.assertEqual(200, resp_mock.status)

    def test_plan_put_version_not_found(self, PlanHandler,
                                        resp_mock, request_mock):
        data = 'name: ex_plan1\ndescription: yaml plan1.\nversion: 2'
        request_mock.body = data
        request_mock.content_type = 'application/x-yaml'
        hand_update = PlanHandler.return_value.update
        hand_update.return_value = fakes.FakePlan()
        plan.PlanController('test_id').put()
        self.assertEqual(400, resp_mock.status)

    def test_plan_delete_not_found(self, PlanHandler, resp_mock, request_mock):
        hand_delete = PlanHandler.return_value.delete
        hand_delete.side_effect = exception.ResourceNotFound(
            name='plan', plan_id='test_id')
        obj = plan.PlanController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(404, resp_mock.status)

    def test_plan_delete_ok(self, PlanHandler, resp_mock, request_mock):
        hand_delete = PlanHandler.return_value.delete
        hand_delete.return_value = None
        obj = plan.PlanController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(204, resp_mock.status)

    def test_plan_delete_dbreferror(self, PlanHandler, resp_mock,
                                    request_mock):
        hand_delete = PlanHandler.return_value.delete
        hand_delete.side_effect = db_exc.DBReferenceError(
            mock.ANY, mock.ANY, mock.ANY, mock.ANY)
        obj = plan.PlanController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(409, resp_mock.status)

    def test_plan_delete_othererror(self, PlanHandler, resp_mock,
                                    request_mock):
        hand_delete = PlanHandler.return_value.delete
        hand_delete.side_effect = db_exc.DBError()
        obj = plan.PlanController('test_id')
        obj.delete()
        hand_delete.assert_called_with('test_id')
        self.assertEqual(500, resp_mock.status)


@mock.patch('pecan.request', new_callable=fakes.FakePecanRequest)
@mock.patch('pecan.response', new_callable=fakes.FakePecanResponse)
@mock.patch('solum.api.handlers.plan_handler.PlanHandler')
class TestPlansController(base.BaseTestCase):
    def setUp(self):
        super(TestPlansController, self).setUp()
        objects.load()

    def test_plans_get_all(self, PlanHandler, resp_mock, request_mock):
        hand_get = PlanHandler.return_value.get_all
        fake_plan = fakes.FakePlan()
        hand_get.return_value = [fake_plan]
        resp = plan.PlansController().get_all()
        self.assertIsNotNone(resp)
        resp_yml = yaml.load(resp)
        self.assertEqual(fake_plan.raw_content['name'], resp_yml[0]['name'])
        self.assertEqual(200, resp_mock.status)
        hand_get.assert_called_with()

    def test_plans_post(self, PlanHandler, resp_mock, request_mock):
        request_mock.body = 'version: 1\nname: ex_plan1\ndescription: dsc1.'
        request_mock.content_type = 'application/x-yaml'
        hand_create = PlanHandler.return_value.create
        hand_create.return_value = fakes.FakePlan()
        plan.PlansController().post()
        hand_create.assert_called_with({'name': 'ex_plan1',
                                        'description': 'dsc1.'})
        self.assertEqual(201, resp_mock.status)

    def test_plans_post_version_not_found(self, PlanHandler,
                                          resp_mock, request_mock):
        request_mock.body = 'version: 2\nname: ex_plan1\ndescription: dsc1.'
        request_mock.content_type = 'application/x-yaml'
        hand_create = PlanHandler.return_value.create
        hand_create.return_value = fakes.FakePlan()
        plan.PlansController().post()
        self.assertEqual(400, resp_mock.status)

    def test_plans_post_nodata(self, handler_mock, resp_mock, request_mock):
        request_mock.body = ''
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakePlan()
        plan.PlansController().post()
        self.assertEqual(400, resp_mock.status)

    def test_plans_post_invalid_yaml(self, handler_mock,
                                     resp_mock, request_mock):
        request_mock.body = 'invalid yaml file'
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakePlan()
        plan.PlansController().post()
        self.assertEqual(400, resp_mock.status)

    def test_plans_post_empty_yaml(self, handler_mock,
                                   resp_mock, request_mock):
        request_mock.body = '{}'
        request_mock.content_type = 'application/json'
        handler_create = handler_mock.return_value.create
        handler_create.return_value = fakes.FakePlan()
        plan.PlansController().post()
        self.assertEqual(400, resp_mock.status)


class TestPlanAsDict(base.BaseTestCase):

    scenarios = [
        ('none', dict(data=None)),
        ('one', dict(data={'name': 'foo'})),
        ('full', dict(data={'uri': 'http://example.com/v1/plans/x1',
                            'name': 'Example-plan',
                            'type': 'plan'}))
    ]

    def test_as_dict(self):
        objects.load()
        if self.data is None:
            s = planmodel.Plan()
            self.data = {}
        else:
            s = planmodel.Plan(**self.data)
        if 'uri' in self.data:
            del self.data['uri']
        if 'type' in self.data:
            del self.data['type']

        self.assertEqual(self.data, s.as_dict(objects.registry.Plan))
