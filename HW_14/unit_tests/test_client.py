import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from HW_13.tools.config import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, STATUS, ERROR
from HW_13.client import create_presence, process_ans


class TestClient(unittest.TestCase):

    def test_create_presence(self):
        test = create_presence()
        test[TIME] = 1
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1, USER: {ACCOUNT_NAME: 'Guest', STATUS: 'online'}})

    def test_request_ok(self):
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')

    def test_bad_request(self):
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'BAD REQUEST'}), '400 : BAD REQUEST')

    def test_no_response(self):
        self.assertRaises(ValueError, process_ans, {ERROR: 'BAD REQUEST'})


if __name__ == '__main__':
    unittest.main()
