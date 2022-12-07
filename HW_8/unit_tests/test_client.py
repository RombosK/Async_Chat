import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from HW_8.config import TIME, ACTION, PRESENCE, USER, ACCOUNT_NAME, RESPONSE, STATUS, ERROR, DEFAULT_PORT, \
    DEFAULT_IP_ADDRESS
from HW_8.client import create_presence, process_ans, parse_args


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
