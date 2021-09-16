import json
import logging
import os.path
import random
import unittest


class EdgeTestData:
    def __init__(self, filename=None):
        self.data = {"accounts": {}}
        self.filename = filename
        if self.filename is not None:
            if os.path.exists(filename):
                with open(self.filename, "r") as fd:
                    self.data = json.load(fd)
            else:
                self.save()

    def save(self, filename=None):
        if filename is not None:
            if os.path.exists(filename):
                logging.warning(f"File {filename} already exists. Overwriting it.")
            self.filename = filename
        if self.filename is None:
            raise Exception("Where should I save to?")
        with open(self.filename, "w") as fd:
            json.dump(self.data, fd)

    def info(self):
        return {
            "accounts_count": len(self.get_accounts()),
            "users_count": sum(len(self.get_users_for_account(a)) for a in self.get_accounts()),
            "applications_count": sum(
                len(self.get_applications_for_account(a)) for a in self.get_accounts()
            ),
        }

    def get_accounts(self):
        return list(self.data["accounts"].keys())

    def get_users_for_account(self, account):
        return self.data["accounts"][account]["users"]

    def get_applications_for_account(self, account):
        return self.data["accounts"][account]["applications"]

    def add_account(self, account, users=[], applications=[]):
        if account not in self.data["accounts"]:
            self.data["accounts"][account] = {
                "users": [],
                "applications": [],
            }
        self.data["accounts"][account]["users"] = list(
            set(self.data["accounts"][account]["users"] + users)
        )
        self.data["accounts"][account]["applications"] = list(
            set(self.data["accounts"][account]["applications"] + applications)
        )

    def pick_account(self):
        return random.choice(self.get_accounts())

    def pick_user_for_account(self, account):
        return random.choice(self.get_users_for_account(account))

    def pick_application_for_account(self, account):
        return random.choice(self.get_applications_for_account(account))


class TestRequestedInfo(unittest.TestCase):
    """
    Run the tests with:

    python3 -m unittest edge_utils.py
    """

    def test_empty(self):
        data = EdgeTestData()
        self.assertEqual(data.get_accounts(), [])

    def test_add_get(self):
        data = EdgeTestData()
        data.add_account("10001", ["aaa", "bbb"], ["xxx", "yyy", "zzz"])
        self.assertEqual(set(data.get_accounts()), {"10001"})
        self.assertEqual(set(data.get_users_for_account("10001")), {"aaa", "bbb"})
        self.assertEqual(set(data.get_applications_for_account("10001")), {"xxx", "yyy", "zzz"})

    def test_add_more(self):
        data = EdgeTestData()
        data.add_account("10001", ["aaa", "bbb"], ["xxx"])
        data.add_account("10002", ["ccc", "ddd"], ["yyy"])
        self.assertEqual(set(data.get_accounts()), {"10001", "10002"})
        self.assertEqual(set(data.get_users_for_account("10001")), {"aaa", "bbb"})
        self.assertEqual(set(data.get_users_for_account("10002")), {"ccc", "ddd"})

    def test_add_merge(self):
        data = EdgeTestData()
        data.add_account("10001", ["aaa", "bbb"], ["xxx"])
        data.add_account("10001", ["bbb", "ccc"], ["xxx", "yyy", "zzz"])
        self.assertEqual(set(data.get_accounts()), {"10001"})
        self.assertEqual(set(data.get_users_for_account("10001")), {"aaa", "bbb", "ccc"})
        self.assertEqual(set(data.get_applications_for_account("10001")), {"xxx", "yyy", "zzz"})

    def test_info(self):
        data = EdgeTestData()
        data.add_account("10001", ["aaa", "bbb"], ["xxx"])
        data.add_account("10002", ["ccc", "ddd"], ["yyy", "zzz"])
        data.add_account("10003", ["eee"], ["zzz"])
        info = data.info()
        self.assertEqual(info["accounts_count"], 3)
        self.assertEqual(info["users_count"], 5)
        self.assertEqual(info["applications_count"], 4)
