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
import shutil
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

        # print("Verify agents are running")
        # TODO Check for running agents


    def tearDown(self):
        # flush all test projects, user accounts, and data, but only if all tests passed,
        # else leave projects and data as-is so test project state can be inspected

        if self.success:
            print("(cleaning)")
            cmd = "sudo -u %s %s/tests/utils/initialize_test_accounts flush %s/tests/utils/single-project.config" % (self.config["HTTPD_USER"], self.config["ROOT"], self.config["ROOT"])
            os.system(cmd)
            if self.config["METAX_AVAILABLE"] != 1:
                print('')
                print("**************************************")
                print("*** METAX INTEGRATION NOT TESTED!! ***")
                print("**************************************")
                print('')


    def waitForPendingActions(self, project, user):
        print("(waiting for pending actions to fully complete)")
        print(".", end='', flush=True)
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

        # Override (disable) simulation of agents, no matter what might be defined in configuration
        headers = { 'X-SIMULATE-AGENTS': 'false' }

        print("--- Freeze Action Postprocessing")

        print("Freeze a folder")
        data = {"project": "test_project_a", "pathname": "/2017-08/Experiment_1"}
        response = requests.post("%s/freeze" % self.config["IDA_API_ROOT_URL"], headers=headers, json=data, auth=test_user_a, verify=False)
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
        self.assertTrue(os.path.exists("%s/projects/test_project_a/%s" % (self.config["DATA_REPLICATION_ROOT"], file_data['pathname'])))
        file_pid = file_data["pid"]

        # TODO if metax is available, verify frozen file is accessible in metax
        if self.config["METAX_AVAILABLE"] == 1:
            None

        # --------------------------------------------------------------------------------

        print("--- Unfreeze Action Postprocessing")

        print("Unfreeze single frozen file")
        data["pathname"] = "/2017-08/Experiment_1/test01.dat"
        response = requests.post("%s/unfreeze" % self.config["IDA_API_ROOT_URL"], headers=headers, json=data, auth=test_user_a, verify=False)
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

        # TODO if metax is available, verify unfrozen file is marked as removed in metax

        # --------------------------------------------------------------------------------

        print("--- Delete Action Postprocessing")

        print("Delete single frozen file")
        data["pathname"] = "/2017-08/Experiment_1/test02.dat"
        response = requests.post("%s/delete" % self.config["IDA_API_ROOT_URL"], headers=headers, json=data, auth=test_user_a, verify=False)
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

        # TODO if metax is available, verify deleted file is marked as removed in metax

        # --------------------------------------------------------------------------------

        print("--- Repair Action Postprocessing")

        print("Retrieve file details from already frozen file 1")
        data["pathname"] = "/2017-08/Experiment_1/baseline/test01.dat"
        response = requests.get("%s/files/byProjectPathname/%s" % (self.config["IDA_API_ROOT_URL"], data["project"]), json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_1_data = response.json()

        print("Retrieve file details from already frozen file 2")
        data["pathname"] = "/2017-08/Experiment_1/baseline/test02.dat"
        response = requests.get("%s/files/byProjectPathname/%s" % (self.config["IDA_API_ROOT_URL"], data["project"]), json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_2_data = response.json()

        print("Update frozen file 2 record to set size and checksum to null")
        data = {"size": "null", "checksum": "null"}
        response = requests.post("%s/files/%s" % (self.config["IDA_API_ROOT_URL"], file_2_data["pid"]), json=data, auth=pso_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_2_data = response.json()

        print("Retrieve file details from already frozen file 3")
        data = {"project": "test_project_a", "pathname": "/2017-08/Experiment_1/baseline/test03.dat"}
        response = requests.get("%s/files/byProjectPathname/%s" % (self.config["IDA_API_ROOT_URL"], data["project"]), json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_3_data = response.json()

        print("Update frozen file 3 record to set size to 999 and checksum to 'abcdef'")
        data = {"size": 999, "checksum": "abcdef"}
        response = requests.post("%s/files/%s" % (self.config["IDA_API_ROOT_URL"], file_3_data["pid"]), json=data, auth=pso_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_3_data = response.json()

        print("Move folder from staging to frozen area")
        result = shutil.move("%s/2017-08/Experiment_2" % (staging_area_root), "%s/2017-08/Experiment_2" % (frozen_area_root))
        self.assertEqual(result, "%s/2017-08/Experiment_2" % (frozen_area_root))
        cmd = "sudo -u %s %s/nextcloud/occ files:scan PSO_test_project_a" % (self.config['HTTPD_USER'], self.config["ROOT"])
        result = os.system(cmd)
        self.assertEqual(result, 0)

        print("Physically delete replication of file 3")
        pathname = "%s/projects/test_project_a/2017-08/Experiment_1/baseline/test03.dat" % (self.config["DATA_REPLICATION_ROOT"])
        result = os.remove(pathname)
        self.assertFalse(os.path.exists(pathname))

        print("Repair project")
        response = requests.post("%s/repair?project=test_project_a" % (self.config["IDA_API_ROOT_URL"]), headers=headers, auth=pso_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        action_data = response.json()

        self.waitForPendingActions("test_project_a", test_user_a)

        response = requests.get("%s/files/action/%s" % (self.config["IDA_API_ROOT_URL"], action_data["pid"]), auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_set_data = response.json()
        self.assertEqual(len(file_set_data), 20)

        print("Verify file details from previously frozen file 1 are unchanged")
        data = {"project": "test_project_a", "pathname": "/2017-08/Experiment_1/baseline/test01.dat"}
        response = requests.get("%s/files/byProjectPathname/%s" % (self.config["IDA_API_ROOT_URL"], data["project"]), json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_data = response.json()
        self.assertEqual(file_1_data['pid'], file_data['pid'])
        self.assertEqual(file_1_data['pathname'], file_data['pathname'])
        self.assertEqual(file_1_data['size'], file_data['size'])
        self.assertEqual(file_1_data['checksum'], file_data['checksum'])
        self.assertEqual(file_1_data['frozen'], file_data['frozen'])
        self.assertEqual(file_1_data['replicated'], file_data['replicated'])

        print("Retrieve file details from post-repair frozen file 2")
        data["pathname"] = "/2017-08/Experiment_1/baseline/test02.dat"
        response = requests.get("%s/files/byProjectPathname/%s" % (self.config["IDA_API_ROOT_URL"], data["project"]), json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_data = response.json()
        self.assertEqual(file_data["size"], 1531)
        self.assertEqual(file_data["checksum"], "c5a8e40a8afaebf3d8429266a6f54ef52eff14dcd22cb64a59a06e4d724eebb9")
        self.assertEqual(file_2_data['replicated'], file_data['replicated'])

        print("Retrieve file details from post-repair frozen file 3")
        data["pathname"] = "/2017-08/Experiment_1/baseline/test03.dat"
        response = requests.get("%s/files/byProjectPathname/%s" % (self.config["IDA_API_ROOT_URL"], data["project"]), json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_data = response.json()
        self.assertEqual(file_data["size"], 2263)
        self.assertEqual(file_data["checksum"], "8950fc9b4292a82cfd1b5e6bbaec578ed00ac9a9c27bf891130f198fef2f0168")
        pathname = "%s/projects/test_project_a/2017-08/Experiment_1/baseline/test03.dat" % (self.config["DATA_REPLICATION_ROOT"])
        self.assertTrue(os.path.exists(pathname))
        self.assertNotEqual(file_3_data['replicated'], file_data['replicated'])

        print("Retrieve file details from post-repair file manually moved to frozen space")
        data["pathname"] = "/2017-08/Experiment_2/baseline/test01.dat"
        response = requests.get("%s/files/byProjectPathname/%s" % (self.config["IDA_API_ROOT_URL"], data["project"]), json=data, auth=test_user_a, verify=False)
        self.assertEqual(response.status_code, 200)
        file_data = response.json()
        self.assertEqual(file_data["size"], 446)
        self.assertEqual(file_data["checksum"], "56293a80e0394d252e995f2debccea8223e4b5b2b150bee212729b3b39ac4d46")
        pathname = "%s/projects/test_project_a/2017-08/Experiment_2/baseline/test01.dat" % (self.config["DATA_REPLICATION_ROOT"])
        self.assertTrue(os.path.exists(pathname))

        # TODO If metax available, check only and all files associated with repair action are accesible in metax

        # --------------------------------------------------------------------------------
        # If all tests passed, record success, in which case tearDown will be done

        self.success = True

        # --------------------------------------------------------------------------------
        # TODO: consider which tests may be missing...
