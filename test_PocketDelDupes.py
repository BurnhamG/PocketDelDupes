import unittest
from unittest.mock import patch

import PocketDelDupes


class PocketConsoleTest(unittest.TestCase):

    def setUp(self):
        def replace_input():
            return None

        def replace_print(*args, **kwargs):
            return None

        PocketDelDupes.input = replace_input
        PocketDelDupes.print = replace_print

    @patch('PocketDelDupes.Pocket.get_access_token', spec=PocketDelDupes.Pocket.get_access_token)
    @patch('PocketDelDupes.webbrowser.open', spec=PocketDelDupes.webbrowser.open)
    @patch('PocketDelDupes.Pocket.get_auth_url', spec=PocketDelDupes.Pocket.get_auth_url)
    @patch('PocketDelDupes.Pocket.get_request_token', spec=PocketDelDupes.Pocket.get_request_token)
    def test_authenticate(self, mock_pocket_request, mock_pocket_auth, mock_browser, mock_access_token):
        test_con_key = 'key'

        req_token = '987zyxwv-ut65-s432-1r0q-p1o23n'
        mock_pocket_request.return_value = req_token

        fake_auth_url = ('https://getpocket.com/auth/authorize?request_token='
                         f'{req_token}&redirect_uri=https://example.com')

        mock_pocket_auth.return_value = fake_auth_url

        mock_browser.return_value = True

        acc_token = '1a234b56-7c89-d098-e765-f4g321'
        mock_access_token.return_value = acc_token

        PocketDelDupes.pocket_authenticate(test_con_key)

        mock_pocket_request.assert_called()
        mock_pocket_request.assert_called_with(test_con_key, redirect_uri='https://ddg.gg')
        mock_pocket_auth.assert_called()
        mock_pocket_auth.assert_called_with(req_token, redirect_uri='https://ddg.gg')
        mock_browser.assert_called()
        mock_access_token.assert_called()
        mock_access_token.assert_called_with(test_con_key, req_token)

    def test_arg_parser_creation(self):
        test_parser = PocketDelDupes.create_arg_parser()
        parsed = test_parser.parse_args(['key_here'])
        self.assertEqual(parsed.api_key, 'key_here')

    @patch('PocketDelDupes.print')
    def test_output_bad(self, mock_print):
        mo = unittest.mock.mock_open()
        example_list = [1, 2, 3, 4]
        with patch('PocketDelDupes.open', mo, create=True):
            PocketDelDupes.output_bad(example_list, True, True)
            mo.assert_called_once()
            handle = mo()
            handle.writelines.assert_called_once()
            mock_print.assert_called()
            mo.reset_mock()
            mock_print.reset_mock()

            PocketDelDupes.output_bad(example_list, False, True)
            mo.assert_not_called()
            handle = mo()
            handle.writelines.assert_not_called()
            mock_print.assert_called()
            mo.reset_mock()
            mock_print.reset_mock()

            PocketDelDupes.output_bad(example_list, True, False)
            mo.assert_called_once()
            handle = mo()
            handle.writelines.assert_called_once()
            mock_print.assert_not_called()


if __name__ == '__main__':
    unittest.main()
