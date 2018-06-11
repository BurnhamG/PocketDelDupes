import unittest
from unittest.mock import patch

import PocketDelDupes


class PocketConsoleTest(unittest.TestCase):

    def setUp(self):
        def replace_input(value=None):
            return value

        def replace_print(*args, **kwargs):
            return 'n'

        self.example_bad_article_list = {
            '1': {'item_id': '1', 'resolved_id': '1', 'given_url': 'http://www.example.com',
                  'given_title': 'Example Title', 'favorite': '0', 'status': '0',
                  'time_added': '1461738821', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 0, 'resolved_title': 'Example Title',
                  },
            '2': {'item_id': '2', 'resolved_id': '2', 'given_url': 'https://www.example2.com',
                  'given_title': 'Another Example', 'favorite': '0', 'status': '0',
                  'time_added': '1461742844', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 1,
                  'resolved_title': 'Another Example Article',
                  'tags': {'Example_tag': {'item_id': '2', 'tag': 'Example_tag'}}
                  }
        }

        self.example_articles = {
            '1': {'item_id': '1', 'resolved_id': '1', 'given_url': 'http://www.example.com',
                  'given_title': 'Example Title', 'favorite': '0', 'status': '0',
                  'time_added': '1461738821', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 0, 'resolved_title': 'Example Title',
                  'resolved_url': 'http://www.example.com', 'word_count': '1250',
                  },
            '2': {'item_id': '2', 'resolved_id': '2', 'given_url': 'https://www.example2.com',
                  'given_title': 'Another Example', 'favorite': '0', 'status': '0',
                  'time_added': '1461742844', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 1,
                  'resolved_title': 'Another Example Article',
                  'resolved_url': 'http://www.example2.com',
                  'tags': {'Example_tag': {'item_id': '2', 'tag': 'Example_tag'},
                           'Second_tag': {'item_id': '2', 'tag': 'Second_tag'}}, 'word_count': '10000'
                  }
        }

        self.example_articles_cleaned = {
            '1': {'resolved_url': 'http://www.example.com', 'word_count': '1250', 'tags': {},
                  'resolved_title': 'Example Title', 'time_added': '1461738821'},
            '2': {'resolved_url': 'http://www.example2.com', 'word_count': '10000',
                  'tags': ['Example_tag', 'Second_tag'], 'resolved_title': 'Another Example Article',
                  'time_added': '1461742844'}
        }

        self.duplicate_articles = {
            '1': {'item_id': '1', 'resolved_id': '1', 'given_url': 'http://www.example.com',
                  'given_title': 'Example Title', 'favorite': '0', 'status': '0',
                  'time_added': '1461738821', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 0, 'resolved_title': 'Example Title',
                  'resolved_url': 'http://www.example.com', 'word_count': '1250',
                  },
            '2': {'item_id': '2', 'resolved_id': '2', 'given_url': 'https://www.example2.com',
                  'given_title': 'Another Example', 'favorite': '0', 'status': '0',
                  'time_added': '1461742844', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 1,
                  'resolved_title': 'Another Example Article',
                  'resolved_url': 'http://www.example2.com',
                  'tags': {'Example_tag': {'item_id': '2', 'tag': 'Example_tag'},
                           'Second_tag': {'item_id': '2', 'tag': 'Second_tag'}}, 'word_count': '10000'
                  },
            '3': {'item_id': '1', 'resolved_id': '1', 'given_url': 'http://www.example.com',
                  'given_title': 'Example Title', 'favorite': '0', 'status': '0',
                  'time_added': '1461742845', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 0, 'resolved_title': 'Example Title',
                  'resolved_url': 'http://www.example.com', 'word_count': '1250',
                  },
            '4': {'item_id': '2', 'resolved_id': '2', 'given_url': 'https://www.example2.com',
                  'given_title': 'Another Example', 'favorite': '0', 'status': '0',
                  'time_added': '1461738822', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 1,
                  'resolved_title': 'Another Example Article',
                  'resolved_url': 'http://www.example2.com',
                  'tags': {'Example_tag': {'item_id': '2', 'tag': 'Example_tag'}}, 'word_count': '10000'
                  }
        }

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

    @patch('PocketDelDupes.output_bad')
    @patch('PocketDelDupes.input', return_value='p')
    def test_url_test_print(self, mock_input, mock_output):
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(self.example_bad_article_list, save_bad=False, print_bad=True)

    @patch('PocketDelDupes.output_bad')
    @patch('PocketDelDupes.input', return_value='p')
    def test_url_test_good(self, mock_input, mock_output):
        PocketDelDupes.url_test(self.example_articles)
        mock_output.assert_not_called()

    @patch('PocketDelDupes.output_bad')
    @patch('PocketDelDupes.input', return_value='s')
    def test_url_test_save(self, mock_input, mock_output):
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(self.example_bad_article_list, save_bad=True, print_bad=False)

    @patch('PocketDelDupes.output_bad')
    @patch('PocketDelDupes.input', return_value='n')
    def test_url_test_neither(self, mock_input, mock_output):
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_not_called()

    @patch('PocketDelDupes.output_bad')
    @patch('PocketDelDupes.input', return_value='b')
    def test_url_test_both(self, mock_input, mock_output):
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(self.example_bad_article_list, save_bad=True, print_bad=True)

    @patch('PocketDelDupes.exit_strategy')
    @patch('PocketDelDupes.output_bad')
    @patch('PocketDelDupes.input', return_value='')
    def test_url_test_exit(self, mock_input, mock_output, mock_exit):
        mock_exit.side_effect = SystemExit
        with self.assertRaises(SystemExit):
            PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_not_called()
        mock_exit.assert_called()
        self.assertRaises(SystemExit, mock_exit)

    def test_filterurl(self):
        urls = ['www.example.com/test', 'www.example.com/test?utm=referrer', 'www.example.com/test?mc=referrer',
                'www.example.com/test?roi=referrer']
        for i in urls:
            self.assertEqual(PocketDelDupes.filterurl(i, '?'), 'www.example.com/test')
        self.assertEqual(PocketDelDupes.filterurl(urls[1], '?utm'), urls[0])
        self.assertEqual(PocketDelDupes.filterurl(urls[2], '?mc'), urls[0])
        self.assertEqual(PocketDelDupes.filterurl(urls[3], '?roi'), urls[0])

    def test_clean_db(self):
        test_dict = PocketDelDupes.clean_db(self.example_articles)
        for i in test_dict.keys():
            self.assertEqual(test_dict[i]['resolved_url'], self.example_articles[i]['resolved_url'])
            self.assertEqual(test_dict[i]['word_count'], self.example_articles[i]['word_count'])
            self.assertEqual(test_dict[i]['resolved_title'], self.example_articles[i]['resolved_title'])
            self.assertEqual(test_dict[i]['time_added'], self.example_articles[i]['time_added'])

        self.assertEqual(test_dict['1']['tags'], {})
        self.assertEqual(test_dict['2']['tags'], list(self.example_articles['2']['tags'].keys()))
        self.assertEqual(len(test_dict['1'].items()), 5)
        self.assertEqual(len(test_dict['2'].items()), 5)

    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    def test_del_dupes(self, mock_instance):
        mock_filtered_dict = PocketDelDupes.del_dupes(self.duplicate_articles, mock_instance)
        self.assertEqual(mock_filtered_dict, self.example_articles)
        mock_instance.delete.assert_called()

    @patch('PocketDelDupes.input', return_value='items to edit.txt')
    def test_items_to_manipulate_text_file(self, mock_input):
        mo = unittest.mock.mock_open()
        with patch('PocketDelDupes.open', mo, create=True):
            PocketDelDupes.items_to_manipulate()
            mo.assert_called_once()
            mo.reset_mock()

            mock_input.side_effect = IOError
            self.assertRaises(IOError, PocketDelDupes.items_to_manipulate)

            mock_input.side_effect = None
            mock_input.return_value = '12345, 123456'
            test_item_list = PocketDelDupes.items_to_manipulate()
            self.assertEqual(test_item_list, ['12345', '123456'])

            mock_input.reset_mock()
            mock_input.return_value = 'www.example.com, www.example2.com, www.example3.com/test'
            test_item_list = PocketDelDupes.items_to_manipulate()
            self.assertEqual(test_item_list, ['www.example.com', 'www.example2.com', 'www.example3.com/test'])

    def test_try_again(self):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.return_value = 'n'
            self.assertFalse(PocketDelDupes.try_again())

            mock_input.return_value = 'y'
            self.assertTrue(PocketDelDupes.try_again())

    def test_sort_items(self):
        with patch('PocketDelDupes.input') as mock_input:
            for v in {'n': 'resolved_title', 'd': 'time_added', 'l': 'word_count', 'u': 'resolved_url'}.values():
                mock_input.return_value = 'b'
                example_return = PocketDelDupes.sort_items(self.example_articles, v)
                example_articles_sorted = sorted(self.example_articles.items(),
                                                 key=lambda x: x[1][v],
                                                 reverse=True)
                self.assertEqual(example_return, example_articles_sorted)

                mock_input.return_value = 'f'
                example_return = PocketDelDupes.sort_items(self.example_articles, v)
                example_articles_sorted = sorted(self.example_articles.items(),
                                                 key=lambda x: x[1][v])
                self.assertEqual(example_return, example_articles_sorted)

    def test_exit_strategy(self):
        self.assertRaises(SystemExit, PocketDelDupes.exit_strategy)

    @patch('PocketDelDupes.print_items_info')
    def test_display_items(self, mock_print_info):
        with patch('PocketDelDupes.input') as mock_input:
            example_articles_sorted = sorted(self.example_articles.items(),
                                             key=lambda x: x[1]['time_added'])
            example_articles_sorted_reverse = sorted(self.example_articles.items(),
                                                     key=lambda x: x[1]['time_added'],
                                                     reverse=True)

            mock_input.side_effect = ['y', 'f', 'all']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted, '1', 'y')
            mock_print_info.assert_any_call(example_articles_sorted, '2', 'y')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', 'f', 'all']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted, '1', 'n')
            mock_print_info.assert_any_call(example_articles_sorted, '2', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', 'f', '1']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_called_with(example_articles_sorted, '1', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['y', 'b', 'all']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted_reverse, '1', 'y')
            mock_print_info.assert_any_call(example_articles_sorted_reverse, '2', 'y')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', 'b', 'all']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted_reverse, '1', 'n')
            mock_print_info.assert_any_call(example_articles_sorted_reverse, '2', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', 'b', '1']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted_reverse, '2', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['', 'b', '1']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted_reverse, '2', 'n')

    @patch('PocketDelDupes.try_again', return_value=True)
    @patch('PocketDelDupes.print_items_info')
    def test_display_items_retry(self, mock_print_info, mock_try):
        with patch('PocketDelDupes.input') as mock_input:
            example_articles_sorted = sorted(self.example_articles.items(),
                                             key=lambda x: x[1]['time_added'])
            example_articles_sorted_reverse = sorted(self.example_articles.items(),
                                                     key=lambda x: x[1]['time_added'],
                                                     reverse=True)

            mock_input.side_effect = ['x', '', 'f', '1']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_called()
            mock_print_info.assert_called_with(example_articles_sorted, '1', 'n')

            mock_input.side_effect = ['', 'b', 'f', '1']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted, '1', 'n')

            mock_input.side_effect = ['x', '', 'b', '1']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted_reverse, '2', 'n')

            mock_input.side_effect = ['', 'b', 'x', '1']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(example_articles_sorted_reverse, '2', 'n')

    @patch('PocketDelDupes.items_to_manipulate')
    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    def test_add_items(self, mock_instance, mock_items):
        mock_items.return_value = ["www.example.com"]
        PocketDelDupes.add_items(mock_instance)
        mock_instance.add.assert_called_with('http://' + mock_items.return_value[0])
        mock_instance.commit.assert_called()

        mock_instance.reset_mock()

        with patch('PocketDelDupes.input') as mock_input:
            mock_input.return_value = 'n'
            mock_items.return_value = ["x"]
            with patch('PocketDelDupes.print') as mock_print:
                PocketDelDupes.add_items(mock_instance)
                mock_print.assert_called_once()
                mock_instance.add.assert_not_called()
                mock_instance.commit.assert_not_called()

    @patch('PocketDelDupes.items_to_manipulate')
    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    def test_delete_items_url(self, mock_instance, mock_items):
        mock_items.return_value = ["www.example.com"]
        PocketDelDupes.delete_items(mock_instance, self.example_articles)
        for item in self.example_articles:
            if self.example_articles[item]['resolved_url'] == 'http://' + mock_items.return_value[0]:
                mock_id = item
                mock_instance.delete.assert_called_with(mock_id)
                mock_instance.commit.assert_called()

        mock_instance.reset_mock()

        with patch('PocketDelDupes.input') as mock_input:
            mock_input.return_value = 'n'
            mock_items.return_value = ["x"]
            with patch('PocketDelDupes.print') as mock_print:
                PocketDelDupes.delete_items(mock_instance, self.example_articles)
                mock_print.assert_called_once()
                mock_instance.delete.assert_not_called()
                mock_instance.commit.assert_not_called()

    @patch('PocketDelDupes.items_to_manipulate')
    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    def test_delete_items_id(self, mock_instance, mock_items):
        mock_items.return_value = ["1"]
        PocketDelDupes.delete_items(mock_instance, self.example_articles)
        mock_instance.delete.assert_called_with("1")
        mock_instance.commit.assert_called()

        mock_instance.reset_mock()
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.return_value = 'n'
            mock_items.return_value = ["1,"]
            with patch('PocketDelDupes.print') as mock_print:
                PocketDelDupes.delete_items(mock_instance, self.example_articles)
                mock_print.assert_called_once()
                mock_instance.delete.assert_not_called()
                mock_instance.commit.assert_not_called()

        mock_instance.reset_mock()
        mock_print.reset_mock()
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.return_value = 'y'
            mock_items.side_effect = [["1,"], ['1']]
            with patch('PocketDelDupes.print') as mock_print:
                PocketDelDupes.delete_items(mock_instance, self.example_articles)
                mock_print.assert_called_once()
                mock_instance.delete.assert_called()
                mock_instance.commit.assert_called_once()

    def test_get_article_url(self):
        returned_article = PocketDelDupes.get_article_url(self.example_articles, 'http://www.example.com',
                                                          'www.example.com')
        self.assertEqual(returned_article, '1')

    def test_get_article_url_bad(self):
        returned_article = PocketDelDupes.get_article_url(self.example_articles, 'http://www.example.co',
                                                          'www.example.co')
        self.assertEqual(returned_article, False)

    @patch('PocketDelDupes.display_items')
    def test_view_items_name(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['n', 'f']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_title'],
                       reverse=False))
            mock_display.assert_called_with(resolved_title_sorted_dict)

            mock_input.reset_mock()

            mock_input.side_effect = ['n', 'b']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_title'],
                       reverse=True))
            mock_display.assert_called_with(resolved_title_sorted_dict)

    @patch('PocketDelDupes.display_items')
    def test_view_items_time(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['d', 'f']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['time_added'],
                       reverse=False))
            mock_display.assert_called_with(resolved_title_sorted_dict)

            mock_input.reset_mock()

            mock_input.side_effect = ['d', 'b']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['time_added'],
                       reverse=True))
            mock_display.assert_called_with(resolved_title_sorted_dict)

    @patch('PocketDelDupes.display_items')
    def test_view_items_words(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['l', 'f']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['word_count'],
                       reverse=False))
            mock_display.assert_called_with(resolved_title_sorted_dict)

            mock_input.reset_mock()

            mock_input.side_effect = ['l', 'b']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_title'],
                       reverse=True))
            mock_display.assert_called_with(resolved_title_sorted_dict)

    @patch('PocketDelDupes.display_items')
    def test_view_items_url(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['u', 'f']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_url'],
                       reverse=False))
            mock_display.assert_called_with(resolved_title_sorted_dict)

            mock_input.reset_mock()

            mock_input.side_effect = ['u', 'b']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_title'],
                       reverse=True))
            mock_display.assert_called_with(resolved_title_sorted_dict)

    @patch('PocketDelDupes.display_items')
    def test_view_items_invalid(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['x', 'n']
            PocketDelDupes.view_items(self.example_articles)
            mock_display.assert_not_called()

    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    @patch('PocketDelDupes.print')
    @patch('PocketDelDupes.input')
    def test_tags_editing(self, mock_input, mock_print, mock_instance):
        mock_input.side_effect = ['y', 'y']
        PocketDelDupes.tags_editing(mock_instance, self.example_articles)
        mock_print.assert_called_with(sorted(['Example_tag', 'Second_tag']))
        mock_instance.tags_clear.assert_any_call(self.example_articles['1']['item_id'])
        mock_instance.tags_clear.assert_any_call(self.example_articles['2']['item_id'])
        mock_instance.commit.assert_called_once()

    @patch('PocketDelDupes.exit_strategy')
    @patch('PocketDelDupes.try_again')
    @patch('PocketDelDupes.tags_editing')
    @patch('PocketDelDupes.view_items')
    @patch('PocketDelDupes.delete_items')
    @patch('PocketDelDupes.add_items')
    @patch('PocketDelDupes.del_dupes')
    @patch('PocketDelDupes.clean_db')
    @patch('PocketDelDupes.url_test')
    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    @patch('PocketDelDupes.pocket_authenticate')
    @patch('PocketDelDupes.create_arg_parser')
    def test_main(self, mock_parser, mock_authenticate, mock_instance, mock_url_test, mock_clean, mock_del_dupes,
                  mock_add, mock_delete, mock_view, mock_tags, mock_try_again, mock_exit):
        mock_parser.return_value = PocketDelDupes.create_arg_parser().parse_args(['key'])
        mock_authenticate.return_value = mock_instance
        mock_instance.get.return_value = [{'list': self.example_articles}]
        test_master_article_dictionary = self.example_articles_cleaned
        mock_clean.return_value = test_master_article_dictionary
        mock_del_dupes.return_value = self.example_articles_cleaned
        mock_try_again.return_value = 'y'
        mock_exit.side_effect = SystemExit

        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['y', 'a', 'd', 'v', 't', 'x', 'e']
            with self.assertRaises(SystemExit):
                PocketDelDupes.main()

        self.assertEqual(mock_parser.call_count, 2)
        mock_authenticate.assert_called_once()
        mock_instance.get.assert_called_once()
        mock_url_test.assert_called_once()
        mock_clean.assert_called_with(self.example_articles)
        mock_del_dupes.assert_called_with(test_master_article_dictionary, mock_instance)
        mock_add.assert_called_with(mock_instance)
        mock_delete.assert_called_with(mock_instance, test_master_article_dictionary)
        mock_view.assert_called_with(test_master_article_dictionary)
        mock_tags.assert_called_with(mock_instance, test_master_article_dictionary)
        mock_try_again.assert_called_once()
        mock_exit.assert_called()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
