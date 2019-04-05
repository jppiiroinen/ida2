# --------------------------------------------------------------------------------
# This file is part of the IDA research data storage service
#
# Copyright (C) 2018 Ministry of Education and Culture, Finland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public
# License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# @author   CSC - IT Center for Science Ltd., Espoo Finland <servicedesk@csc.fi>
# @license  GNU Affero General Public License, version 3
# @link     https://research.csc.fi/
# --------------------------------------------------------------------------------
# Note regarding sequence of tests: this test case contains only a single test
# method, which utilizes the test projects, user accounts, and project data
# initialized during setup, such that the sequential actions in the single
# test method create side effects which subsequent actions and assertions may
# depend on. The state of the test accounts and data must be taken into account
# whenever adding tests at any particular point in that execution sequence.
# --------------------------------------------------------------------------------

import requests
import urllib
import subprocess
import unittest
import time
import os
from tests.common.utils import load_configuration


class TestAgents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("=== tests/agents/test_agents")

    def setUp(self):
        # load service configuration variables
        self.config = load_configuration()

        # keep track of success, for reference in tearDown
        self.success = False

        # timeout when waiting for actions to complete
        self.timeout = 3600

        print("(initializing)")

        # ensure we start with a fresh setup of projects, user accounts, and data

        cmd = "sudo -u %s %s/tests/utils/initialize_test_accounts %s/tests/utils/single-project.config" % (self.config["HTTPD_USER"], self.config["ROOT"], self.config["ROOT"])
        result = os.system(cmd)
        self.assertEquals(result, 0)

        cmd = "sudo -u %s %s/tests/utils/initialize_max_files test_project_a" % (self.config["HTTPD_USER"], self.config["ROOT"])
        result = os.system(cmd)
        self.assertEquals(result, 0)


    def tearDown(self):
        # flush all test projects, user accounts, and data, but only if all tests passed,
        # else leave projects and data as-is so test project state can be inspected

        if self.success:
            print("(cleaning)")
            cmd = "sudo -u %s %s/tests/utils/initialize_test_accounts flush %s/tests/utils/single-project.config" % (self.config["HTTPD_USER"], self.config["ROOT"], self.config["ROOT"])
            os.system(cmd)


    def waitForPendingActions(self, project, user):
        print("(waiting for pending actions to fully complete)")
        response = requests.get("%s/actions?project=%s&status=pending" % (self.config["IDA_API_ROOT_URL"], project), auth=user, verify=False)
        self.assertEqual(response.status_code, 200)
        actions = response.json()
        max_time = time.time() + self.timeout
        while len(actions) > 0 and time.time() < max_time:
            print(".", end='', flush=True)
            time.sleep(1)
            response = requests.get("%s/actions?project=%s&status=pending" % (self.config["IDA_API_ROOT_URL"], project), auth=user, verify=False)
            self.assertEqual(response.status_code, 200)
            actions = response.json()
        print("")
        self.assertEqual(len(actions), 0, "Timed out waiting for pending actions to fully complete")


    def test_agents(self):

        admin_user = (self.config["NC_ADMIN_USER"], self.config["NC_ADMIN_PASS"])
        pso_user_a = (self.config["PROJECT_USER_PREFIX"] + "test_project_a", self.config["PROJECT_USER_PASS"])
        test_user_a = ("test_user_a", self.config["TEST_USER_PASS"])

        frozen_area_root = "%s/PSO_test_project_a/files/test_project_a" % (self.config["STORAGE_OC_DATA_ROOT"])
        staging_area_root = "%s/PSO_test_project_a/files/test_project_a%s" % (self.config["STORAGE_OC_DATA_ROOT"], self.config["STAGING_FOLDER_SUFFIX"])

        print("--- Freeze Action Postprocessing")

        print("Freeze a folder")
        data = {"project": "test_project_a", "pathname": "/2017-08/Experiment_1"}
        response = requests.post("%s/freeze" % self.config["IDA_API_ROOT_URL"], json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        action_data = response.json()
        action_pid = action_data["pid"]
        self.assertEqual(action_data["action"], "freeze")
        self.assertEqual(action_data["project"], data["project"])
        self.assertEqual(action_data["pathname"], data["pathname"])

        print("Verify folder was physically moved from frozen to staging area")
        self.assertFalse(os.path.exists("%s/2017-08/Experiment_1" % (staging_area_root)))
        self.assertTrue(os.path.exists("%s/2017-08/Experiment_1" % (frozen_area_root)))

        self.waitForPendingActions("test_project_a", test_user_a)

        print("Retrieve completed freeze action details")
        response = requests.get("%s/actions/%s" % (self.config["IDA_API_ROOT_URL"], action_pid), auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        action_data = response.json()
        self.assertIsNotNone(action_data.get("metadata", None))
        self.assertIsNotNone(action_data.get("replication", None))
        self.assertIsNotNone(action_data.get("completed", None))

        print("Retrieve frozen file details")
        response = requests.get("%s/files/action/%s" % (self.config["IDA_API_ROOT_URL"], action_pid), auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_set_data = response.json()
        self.assertTrue(len(file_set_data) > 0)
        file_data = file_set_data[0]
        self.assertEqual(file_data["action"], action_pid)
        self.assertIsNotNone(file_data.get("checksum", None))
        self.assertIsNotNone(file_data.get("frozen", None))
        self.assertIsNone(file_data.get("removed", None))
        self.assertIsNone(file_data.get("cleared", None))
        file_pid = file_data["pid"]

        # TODO if metax is available, verify metadata in metax
        # TODO verify physical file replication

        # --------------------------------------------------------------------------------

        print("--- Unfreeze Action Postprocessing")

        print("Unfreeze single frozen file")
        data["pathname"] = "/2017-08/Experiment_1/test01.dat"
        response = requests.post("%s/unfreeze" % self.config["IDA_API_ROOT_URL"], json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        action_data = response.json()
        action_pid = action_data["pid"]
        self.assertEqual(action_data["action"], "unfreeze")
        self.assertEqual(action_data["project"], data["project"])
        self.assertEqual(action_data["pathname"], data["pathname"])

        print("Verify file was physically moved from frozen to staging area")
        self.assertFalse(os.path.exists("%s/2017-08/Experiment_1/test01.dat" % (frozen_area_root)))
        self.assertTrue(os.path.exists("%s/2017-08/Experiment_1/test01.dat" % (staging_area_root)))

        self.waitForPendingActions("test_project_a", test_user_a)

        print("Retrieve completed unfreeze action details")
        response = requests.get("%s/actions/%s" % (self.config["IDA_API_ROOT_URL"], action_pid), auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        action_data = response.json()
        self.assertIsNotNone(action_data.get("metadata", None))
        self.assertIsNotNone(action_data.get("completed", None))

        print("Retrieve unfrozen file details")
        response = requests.get("%s/files/action/%s" % (self.config["IDA_API_ROOT_URL"], action_pid), auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_set_data = response.json()
        self.assertTrue(len(file_set_data) > 0)
        file_data = file_set_data[0]
        self.assertEqual(file_data["action"], action_pid)
        self.assertIsNotNone(file_data.get("removed", None))
        self.assertIsNone(file_data.get("cleared", None))
        file_pid = file_data["pid"]

        # TODO if metax is available, verify metadata inactive in metax

        # --------------------------------------------------------------------------------

        print("--- Delete Action Postprocessing")

        print("Delete single frozen file")
        data["pathname"] = "/2017-08/Experiment_1/test02.dat"
        response = requests.post("%s/delete" % self.config["IDA_API_ROOT_URL"], json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        action_data = response.json()
        action_pid = action_data["pid"]
        self.assertEqual(action_data["action"], "delete")
        self.assertEqual(action_data["pathname"], data["pathname"])

        print("Verify file was physically removed from frozen area")
        self.assertFalse(os.path.exists("%s/2017-08/Experiment_1/test02.dat" % (frozen_area_root)))

        self.waitForPendingActions("test_project_a", test_user_a)

        print("Retrieve completed delete action details")
        response = requests.get("%s/actions/%s" % (self.config["IDA_API_ROOT_URL"], action_pid), auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        action_data = response.json()
        self.assertIsNotNone(action_data.get("metadata", None))
        self.assertIsNotNone(action_data.get("completed", None))

        print("Retrieve deleted file details")
        response = requests.get("%s/files/action/%s" % (self.config["IDA_API_ROOT_URL"], action_pid), auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_set_data = response.json()
        self.assertTrue(len(file_set_data) > 0)
        file_data = file_set_data[0]
        self.assertEqual(file_data["action"], action_pid)
        self.assertIsNotNone(file_data.get("removed", None))
        self.assertIsNone(action_data.get("cleared", None))
        file_pid = file_data["pid"]

        # TODO if metax is available, verify metadata inactive in metax

        # --------------------------------------------------------------------------------
        # If all tests passed, record success, in which case tearDown will be done

        self.success = True

        # --------------------------------------------------------------------------------
        # TODO: consider which tests may be missing...
