import datetime
import random
import time
import unittest
from unittest.mock import DEFAULT, patch

import PocketDelDupes


class PocketConsoleTest(unittest.TestCase):

    @staticmethod
    def create_large_dict(items):
        i = 1
        while i <= items:
            yield i, {'item_id': str(i), 'resolved_id': str(i), 'given_url': f'http://www.example{i}.com',
                      'given_title': f'Example Title {i}', 'favorite': '0', 'status': '0',
                      'time_added': '1461738821', 'time_updated': '1522220665', 'time_read': '0',
                      'time_favorited': '0', 'sort_id': i - 1, 'resolved_title': f'Example Title {i}',
                      'resolved_url': f'http://www.example{i}.com',
                      'word_count': str(int((i * (random.random() * 10 if i < 1000 else random.random())))),
                      }
            i += 1

    def setUp(self):
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

        self.example_articles_cleaned_no_tags = {
            '1': {'resolved_url': 'http://www.example.com', 'word_count': '1250', 'tags': {},
                  'resolved_title': 'Example Title', 'time_added': '1461738821'},
            '2': {'resolved_url': 'http://www.example2.com', 'word_count': '10000',
                  'tags': {}, 'resolved_title': 'Another Example Article',
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
            '3': {'item_id': '3', 'resolved_id': '3', 'given_url': 'http://www.example.com',
                  'given_title': 'Example Title', 'favorite': '0', 'status': '0',
                  'time_added': '1461742845', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 0, 'resolved_title': 'Example Title',
                  'resolved_url': 'http://www.example.com', 'word_count': '1250',
                  },
            '4': {'item_id': '4', 'resolved_id': '4', 'given_url': 'https://www.example2.com',
                  'given_title': 'Another Example', 'favorite': '0', 'status': '0',
                  'time_added': '1461738822', 'time_updated': '1522220665', 'time_read': '0',
                  'time_favorited': '0', 'sort_id': 1,
                  'resolved_title': 'Another Example Article',
                  'resolved_url': 'http://www.example2.com',
                  'tags': {'Example_tag': {'item_id': '2', 'tag': 'Example_tag'}}, 'word_count': '10000'
                  }
        }

        self.large_article_list = {}
        for k, v in self.create_large_dict(15000):
            self.large_article_list[k] = v

        PocketDelDupes.print = replace_print

    @patch('PocketDelDupes.Pocket.get_access_token', spec=PocketDelDupes.Pocket.get_access_token)
    @patch('PocketDelDupes.webbrowser.open', spec=PocketDelDupes.webbrowser.open)
    @patch('PocketDelDupes.Pocket.get_auth_url', spec=PocketDelDupes.Pocket.get_auth_url)
    @patch('PocketDelDupes.Pocket.get_request_token', spec=PocketDelDupes.Pocket.get_request_token)
    def test_authenticate(self, mock_pocket_request, mock_pocket_auth, mock_browser, mock_access_token):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.return_value = ''
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
        with patch('PocketDelDupes.open', mo):
            PocketDelDupes.output_bad(example_list, True, True)
            mo.assert_called_once()
            mo().writelines.assert_called_once()
            mock_print.assert_called()
            mo.reset_mock()
            mock_print.reset_mock()

            PocketDelDupes.output_bad(example_list, False, True)
            mo.assert_not_called()
            mo().writelines.assert_not_called()
            mock_print.assert_called()
            mo.reset_mock()
            mock_print.reset_mock()

            PocketDelDupes.output_bad(example_list, True, False)
            mo.assert_called_once()
            mo().writelines.assert_called_once()
            mock_print.assert_not_called()
            mo.reset_mock()
            mock_print.reset_mock()

            PocketDelDupes.output_bad(example_list, False, False)
            mo.assert_not_called()
            mo().writelines.assert_not_called()
            mock_print.assert_not_called()

    @patch('PocketDelDupes.output_bad')
    @patch('PocketDelDupes.input')
    def test_url_test(self, mock_input, mock_output):
        id_list = ['https://getpocket.com/a/read/' + self.example_bad_article_list['1']['item_id'],
                   'https://getpocket.com/a/read/' + self.example_bad_article_list['2']['item_id']]

        mock_input.side_effect = ['p', 'n']
        with self.assertRaises(SystemExit):
            PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(id_list, save_bad=False, print_bad=True)

        mock_output.reset_mock()

        PocketDelDupes.url_test(self.example_articles)
        mock_output.assert_not_called()

        mock_output.reset_mock()

        mock_input.side_effect = ['s', 'y']
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(id_list, save_bad=True, print_bad=False)

        mock_output.reset_mock()

        mock_input.side_effect = ['n', 'y']
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_not_called()

        mock_output.reset_mock()

        mock_input.side_effect = ['b', 'y']
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(id_list, save_bad=True, print_bad=True)

        mock_output.reset_mock()

        mock_input.side_effect = ['q', 'n']
        with self.assertRaises(SystemExit):
            PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_not_called()

        mock_output.reset_mock()

        mock_input.side_effect = ['']
        with self.assertRaises(SystemExit):
            PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_not_called()

        mock_output.reset_mock()

        mock_input.side_effect = ['x', 'y', 'b', 'y']
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(id_list, save_bad=True, print_bad=True)

        mock_output.reset_mock()

        mock_input.side_effect = ['x', 'y', 'b', 'x', 'y', 'y']
        PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(id_list, save_bad=True, print_bad=True)

        mock_output.reset_mock()

        mock_input.side_effect = ['x', 'y', 'b', 'x', 'y', 'n']
        with self.assertRaises(SystemExit):
            PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(id_list, save_bad=True, print_bad=True)

        mock_output.reset_mock()

        mock_input.side_effect = ['x', 'y', 'b', 'x', 'n']
        with self.assertRaises(SystemExit):
            PocketDelDupes.url_test(self.example_bad_article_list)
        mock_output.assert_called_with(id_list, save_bad=True, print_bad=True)

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

        with patch.multiple('PocketDelDupes', **{'input': DEFAULT, 'print': DEFAULT}) as mocks:
            for input_val in [['n'], ['y'], ['x', 'y', 'y'], [''], ['w', 'n'], ['']]:
                dup_arts = dict(self.duplicate_articles)
                mock_instance.reset_mock()
                mocks['input'].side_effect = input_val
                mock_filtered_dict = PocketDelDupes.del_dupes(dup_arts, mock_instance)
                if 'n' in input_val[::2] or '' in input_val[::2]:
                    self.assertEqual(mock_filtered_dict, self.duplicate_articles)
                    mock_instance.delete.assert_not_called()
                    mock_instance.commit.assert_not_called()
                elif 'n' in input_val[1::2]:
                    self.assertEqual(mock_filtered_dict, None)
                    mock_instance.delete.assert_not_called()
                    mock_instance.commit.assert_not_called()
                else:
                    self.assertEqual(mock_filtered_dict, self.example_articles, msg=f"{input_val}")
                    mock_instance.delete.assert_called()
                    mock_instance.commit.assert_called()

            dup_arts = dict(self.example_articles_cleaned)
            mocks['input'].reset_mock()
            mock_instance.reset_mock()
            mocks['input'].side_effect = ['']
            mock_filtered_dict = PocketDelDupes.del_dupes(dup_arts, mock_instance)
            self.assertEqual(mock_filtered_dict, self.example_articles_cleaned)
            mock_instance.delete.assert_not_called()
            mock_instance.commit.assert_not_called()
            mocks['print'].assert_called_with('No duplicates found!\n')

    @patch('PocketDelDupes.input', return_value='items to edit.txt')
    def test_items_to_manipulate_text_file(self, mock_input):
        mo = unittest.mock.mock_open()
        with patch('PocketDelDupes.open', mo, create=True):
            PocketDelDupes.items_to_manipulate()
            mo.assert_called_once()
            mo.reset_mock()

            mock_input.side_effect = ['test.txt', 'n']
            mo.side_effect = IOError
            self.assertEqual(None, PocketDelDupes.items_to_manipulate())
            mo.reset_mock()

            mock_input.side_effect = ['']
            self.assertEqual(None, PocketDelDupes.items_to_manipulate())

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

            mock_input.side_effect = ['r', 'y']
            self.assertTrue(PocketDelDupes.try_again())

    def test_sort_items(self):
        # example_articles_sorted = sorted(self.example_articles.items(),
        #                                  key=lambda x: x[1]['time_added'])
        # example_articles_sorted_reverse = sorted(self.example_articles.items(),
        #                                          key=lambda x: x[1]['time_added'],
        #                                          reverse=True)
        with patch('PocketDelDupes.input') as mock_input:
            key_list = {'n': 'resolved_title',
                        'd': 'time_added',
                        'l': 'word_count',
                        'u': 'resolved_url'}
            for v in key_list:
                mock_input.side_effect = [v, 'b']
                example_return = PocketDelDupes.sort_items(self.example_articles)
                if v == 'l':
                    example_articles_sorted = sorted(self.example_articles.items(),
                                                     key=lambda x: int(x[1][key_list[v]]),
                                                     reverse=True)
                else:
                    example_articles_sorted = sorted(self.example_articles.items(),
                                                     key=lambda x: x[1][key_list[v]],
                                                     reverse=True)
                self.assertEqual(example_return, example_articles_sorted,
                                 msg=f"The sorted lists are not equal when sorted backward using {key_list[v]}.")

                mock_input.side_effect = [v, 'f']
                example_return = PocketDelDupes.sort_items(self.example_articles)
                if v == 'l':
                    example_articles_sorted = sorted(self.example_articles.items(),
                                                     key=lambda x: int(x[1][key_list[v]]))
                else:
                    example_articles_sorted = sorted(self.example_articles.items(),
                                                     key=lambda x: x[1][key_list[v]])
                self.assertEqual(example_return, example_articles_sorted,
                                 msg=f"The sorted lists are not equal when sorted forward using {key_list[v]}.")

                mock_input.side_effect = ['x', 'y', v, 't', 'y', 'f']
                example_return = PocketDelDupes.sort_items(self.example_articles)
                if v == 'l':
                    example_articles_sorted = sorted(self.example_articles.items(),
                                                     key=lambda x: int(x[1][key_list[v]]))
                else:
                    example_articles_sorted = sorted(self.example_articles.items(),
                                                     key=lambda x: x[1][key_list[v]])
                self.assertEqual(example_return, example_articles_sorted,
                                 msg=(f"The sorted lists are not equal when retrying "
                                      f"and sorting forward using {key_list[v]}."))

                mock_input.side_effect = ['q', 'n']
                example_return = PocketDelDupes.sort_items(self.example_articles)
                self.assertEqual(example_return, None)

                mock_input.side_effect = [v, 'h', 'n']
                example_return = PocketDelDupes.sort_items(self.example_articles)
                self.assertEqual(example_return, None)

    @patch('PocketDelDupes.print')
    def test_print_items_info(self, mock_print):
        art_timestamp = datetime.datetime.fromtimestamp(int(self.example_articles['1']['time_added']))
        PocketDelDupes.print_items_info(self.example_articles, '1', v_url='y')
        mock_print.assert_called_with(f"{self.example_articles['1']['resolved_title']}, added {art_timestamp}, with "
                                      f"{self.example_articles['1']['word_count']} words. "
                                      f"URL is {self.example_articles['1']['resolved_url']}.")
        mock_print.reset_mock()

        art_timestamp = datetime.datetime.fromtimestamp(int(self.example_articles['2']['time_added']))
        PocketDelDupes.print_items_info(self.example_articles, '2', v_url='n')
        mock_print.assert_called_with(f"{self.example_articles['2']['resolved_title']}, added {art_timestamp}, with "
                                      f"{self.example_articles['2']['word_count']} words. ")

    def test_exit_strategy(self):
        self.assertRaises(SystemExit, PocketDelDupes.exit_strategy)

    @patch('PocketDelDupes.print_items_info')
    def test_display_items(self, mock_print_info):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['y', 'all']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '1', 'y')
            mock_print_info.assert_any_call(self.example_articles, '2', 'y')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', 'all']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '1', 'n')
            mock_print_info.assert_any_call(self.example_articles, '2', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', '1', '', '']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '1', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['y', 'all']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '1', 'y')
            mock_print_info.assert_any_call(self.example_articles, '2', 'y')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', 'all']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '1', 'n')
            mock_print_info.assert_any_call(self.example_articles, '2', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', '3', '']
            PocketDelDupes.display_items(self.duplicate_articles)
            mock_print_info.assert_any_call(self.duplicate_articles, '1', 'n')
            mock_print_info.assert_any_call(self.duplicate_articles, '2', 'n')
            mock_print_info.assert_any_call(self.duplicate_articles, '3', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['n', '2', '']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '2', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['', '2', '']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '2', 'n')

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['', 'two', 'n']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_not_called()

            mock_print_info.reset_mock()
            mock_input.reset_mock()
            mock_input.side_effect = ['q', 'n']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_not_called()

    @patch('PocketDelDupes.try_again', return_value=True)
    @patch('PocketDelDupes.print_items_info')
    def test_display_items_retry(self, mock_print_info, mock_try):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['x', '', '1', '', '', ]
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_called()
            mock_print_info.assert_any_call(self.example_articles, '1', 'n')

            mock_print_info.reset_mock()

            mock_input.side_effect = ['x', 'q', '', '2', '']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_called()
            mock_print_info.assert_any_call(self.example_articles, '1', 'n')

            mock_print_info.reset_mock()

            mock_input.side_effect = ['', '1', 'x']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_called_once()

            mock_print_info.reset_mock()

            mock_input.side_effect = ['x', '', '2', '']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '2', 'n')

            mock_print_info.reset_mock()

            mock_input.side_effect = ['', 'b', '2', '']
            PocketDelDupes.display_items(self.example_articles)
            mock_print_info.assert_any_call(self.example_articles, '2', 'n')

    def test_validate_url(self):
        return_value = PocketDelDupes.validate_url("www.example.com")
        self.assertEqual(return_value, "http://www.example.com")

        return_value = PocketDelDupes.validate_url("//www.example.com")
        self.assertEqual(return_value, "http://www.example.com")

        return_value = PocketDelDupes.validate_url("/www.example.com")
        self.assertEqual(return_value, "http://www.example.com")

        return_value = PocketDelDupes.validate_url("bad_url")
        self.assertEqual(return_value, False)

    @patch('PocketDelDupes.items_to_manipulate')
    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    def test_add_items(self, mock_instance, mock_items):
        mock_items.return_value = None
        PocketDelDupes.add_items(mock_instance)
        mock_instance.add.assert_not_called()
        mock_instance.commit.assert_not_called()

        mock_instance.reset_mock()

        mock_items.return_value = ["www.example.com"]
        PocketDelDupes.add_items(mock_instance)
        mock_instance.bulk_add.assert_called_with(url='http://' + mock_items.return_value[0])
        mock_instance.commit.assert_called()

        mock_instance.reset_mock()

        mock_items.return_value = ["//www.example.com"]
        PocketDelDupes.add_items(mock_instance)
        mock_instance.bulk_add.assert_called_with(url='http:' + mock_items.return_value[0])
        mock_instance.commit.assert_called()

        mock_instance.reset_mock()

        with patch('PocketDelDupes.input') as mock_input:
            mock_input.return_value = 'n'
            mock_items.return_value = ["x"]
            with patch('PocketDelDupes.print') as mock_print:
                PocketDelDupes.add_items(mock_instance)
                self.assertEqual(mock_print.call_count, 2)
                mock_instance.bulk_add.assert_not_called()
                mock_instance.commit.assert_not_called()

    @patch('PocketDelDupes.items_to_manipulate')
    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    def test_delete_items_url(self, mock_instance, mock_items):
        mock_items.return_value = None
        PocketDelDupes.delete_items(mock_instance, self.example_articles)
        mock_instance.delete.assert_not_called()
        mock_instance.commit.assert_not_called()

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
        returned_article = PocketDelDupes.get_article_url(self.example_articles, 'http://www.example.com')
        self.assertEqual(returned_article, '1')

    def test_get_article_url_bad(self):
        returned_article = PocketDelDupes.get_article_url(self.example_articles, 'http://www.example.co')
        self.assertEqual(returned_article, False)

    @patch('PocketDelDupes.display_items')
    def test_view_items_name(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['n', 'f']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_title'], reverse=False))
            mock_display.assert_called_with(resolved_title_sorted_dict)

            mock_input.reset_mock()

            mock_input.side_effect = ['n', 'b']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_title'], reverse=True))
            mock_display.assert_called_with(resolved_title_sorted_dict)

    @patch('PocketDelDupes.display_items')
    def test_view_items_time(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['d', 'f']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['time_added'], reverse=False))
            mock_display.assert_called_with(resolved_title_sorted_dict)

            mock_input.reset_mock()

            mock_input.side_effect = ['d', 'b']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['time_added'], reverse=True))
            mock_display.assert_called_with(resolved_title_sorted_dict)

    # noinspection PyTypeChecker
    @patch('PocketDelDupes.display_items')
    def test_view_items_words(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['l', 'f']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['word_count'], reverse=False))
            mock_display.assert_called_with(resolved_title_sorted_dict)

            mock_input.reset_mock()

            mock_input.side_effect = ['l', 'b']
            PocketDelDupes.view_items(self.example_articles)
            # noinspection PyTypeChecker,PyTypeChecker
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_title'], reverse=True))
            mock_display.assert_called_with(resolved_title_sorted_dict)

    # noinspection PyTypeChecker
    @patch('PocketDelDupes.display_items')
    def test_view_items_url(self, mock_display):
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['u', 'f']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_url'], reverse=False))
            mock_display.assert_called_with(resolved_title_sorted_dict)

            mock_input.reset_mock()

            mock_input.side_effect = ['u', 'b']
            PocketDelDupes.view_items(self.example_articles)
            resolved_title_sorted_dict = dict(
                sorted(self.example_articles.items(), key=lambda x: x[1]['resolved_title'], reverse=True))
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
        mock_input.side_effect = ['y']
        PocketDelDupes.tags_editing(mock_instance, self.example_articles)
        mock_print.assert_called_with("Here are the tags, along with their frequency: ",
                                      [('Example_tag', 1), ('Second_tag', 1)])
        mock_instance.tags_clear.assert_any_call(self.example_articles['1']['item_id'])
        mock_instance.tags_clear.assert_any_call(self.example_articles['2']['item_id'])
        mock_instance.commit.assert_called_once()

        mock_input.reset_mock()
        mock_instance.reset_mock()

        mock_input.side_effect = ['n']
        PocketDelDupes.tags_editing(mock_instance, self.example_articles)
        mock_print.assert_called_with("Here are the tags, along with their frequency: ",
                                      [('Example_tag', 1), ('Second_tag', 1)])
        mock_instance.tags_clear.assert_not_called()
        mock_instance.commit.assert_not_called()

        mock_input.reset_mock()
        mock_instance.reset_mock()

        mock_input.side_effect = ['n']
        PocketDelDupes.tags_editing(mock_instance, self.duplicate_articles)
        mock_print.assert_called_with("Here are the tags, along with their frequency: ",
                                      [('Example_tag', 2), ('Second_tag', 1)])
        mock_instance.tags_clear.assert_not_called()
        mock_instance.commit.assert_not_called()

        mock_input.reset_mock()
        mock_instance.reset_mock()

        mock_input.side_effect = ['y']
        PocketDelDupes.tags_editing(mock_instance, self.example_articles_cleaned_no_tags)
        mock_instance.tags_clear.assert_not_called()
        mock_instance.commit.assert_not_called()
        mock_print.assert_called_with("None of the articles have tags!")

    @patch('PocketDelDupes.pickle')
    @patch('PocketDelDupes.os.path.exists')
    @patch('PocketDelDupes.print')
    def test_load_articles_from_disk(self, mock_print, mock_exists, mock_pickle):
        mo = unittest.mock.mock_open()
        with patch('PocketDelDupes.open', mo):
            mock_exists.return_value = False
            PocketDelDupes.load_articles_from_disk()
            mock_print.assert_called_with('No previous sync detected - proceeding by retrieving articles from website.')

            mock_print.reset_mock()

            mock_exists.return_value = True
            PocketDelDupes.load_articles_from_disk()
            mo.assert_called_with('article_list', 'rb')
            mock_pickle.loads.assert_called()

            mock_pickle.reset_mock()

            mock_pickle.loads.side_effect = EOFError
            return_val = PocketDelDupes.load_articles_from_disk()
            mo.assert_called_with('article_list', 'rb')
            mock_print.assert_called_with('No previous sync detected - proceeding by retrieving articles from website.')
            self.assertEqual(return_val, None)

    @patch('PocketDelDupes.os')
    @patch('PocketDelDupes.pickle')
    def test_save_articles_to_disk(self, mock_pickle, mock_os):
        mo = unittest.mock.mock_open()
        with patch('PocketDelDupes.open', mo):
            mock_os.path.exists.return_value = True
            PocketDelDupes.save_articles_to_disk(self.example_articles, str(int(time.time())))
            mock_os.replace.assert_called_once()
            mock_pickle.dump.assert_called_once()

            mock_pickle.reset_mock()
            mock_os.reset_mock()
            mock_os.path.exists.return_value = False
            PocketDelDupes.save_articles_to_disk(self.example_articles, str(int(time.time())))
            mock_os.replace.assert_not_called()
            mock_pickle.dump.assert_called_once()

    @patch('PocketDelDupes.input')
    def test_check_sync_date(self, mock_input):
        old_list = ('The saved list of articles has not been synchronized in two weeks. ' +
                    'Would you like to update the saved list? (Y/N) ')
        new_list = ('The saved list of articles has been synchronized in the past two weeks. ' +
                    'Would you like to update the saved list anyway? (Y/N) ')
        resync_msg = ('By default, we will show you all saved articles. Do you want to update ALL articles?\n'
                      'WARNING: This will potentially take a long time, as it will retrieve ALL articles from '
                      'Pocket. (Y/N) ')

        def set_more_list(length):
            return (f'You are requesting more articles than the {length} that are currently saved.'
                    ' Would you like to update the saved list? (Y/N) ')

        mock_input.return_value = 'y'

        test_date = datetime.datetime.now() - datetime.timedelta(days=15)
        list_length = 10
        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val=5, is_offline=False)
        self.assertEqual(return_val, True)
        mock_input.assert_called_with(old_list)

        test_date = datetime.datetime.now() - datetime.timedelta(days=12)
        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val=5, is_offline=False)
        self.assertEqual(return_val, True)
        mock_input.assert_called_with(new_list)

        list_length = 4
        more_list = set_more_list(list_length)
        test_date = datetime.datetime.now() - datetime.timedelta(days=12)
        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val=5, is_offline=False)
        self.assertEqual(return_val, True)
        mock_input.assert_called_with(more_list)

        mock_input.return_value = 'n'

        list_length = 10
        test_date = datetime.datetime.now() - datetime.timedelta(days=15)
        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val=5, is_offline=False)
        self.assertEqual(return_val, False)
        mock_input.assert_called_with(old_list)

        test_date = datetime.datetime.now() - datetime.timedelta(days=12)
        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val=5, is_offline=False)
        self.assertEqual(return_val, False)
        mock_input.assert_called_with(new_list)

        mock_input.reset_mock()
        mock_input.side_effect = ['x', 'y', 'y']

        test_date = datetime.datetime.now() - datetime.timedelta(days=15)
        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val=5, is_offline=False)
        self.assertEqual(return_val, True)
        mock_input.assert_called_with(old_list)

        mock_input.reset_mock()
        mock_input.side_effect = ['x', 'y', 'y']

        test_date = datetime.datetime.now() - datetime.timedelta(days=12)
        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val=5, is_offline=False)
        self.assertEqual(return_val, True)
        mock_input.assert_called_with(new_list)

        mock_input.reset_mock()
        mock_input.side_effect = ['x', 'y', 'y']

        list_length = 4
        more_list = set_more_list(list_length)
        test_date = datetime.datetime.now() - datetime.timedelta(days=12)
        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val=5, is_offline=False)
        self.assertEqual(return_val, True)
        mock_input.assert_called_with(more_list)

        mock_input.reset_mock()
        mock_input.side_effect = ['x', 'n']

        list_length = 10
        test_date = datetime.datetime.now() - datetime.timedelta(days=15)
        with self.assertRaises(SystemExit):
            PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                           ret_val=5, is_offline=False)
        mock_input.assert_any_call(old_list)

        mock_input.reset_mock()
        mock_input.side_effect = ['x', 'n']

        test_date = datetime.datetime.now() - datetime.timedelta(days=12)
        with self.assertRaises(SystemExit):
            PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                        ret_val=5, is_offline=False)
        mock_input.assert_any_call(new_list)

        mock_input.reset_mock()
        mock_input.side_effect = ['x', 'n']

        list_length = 4
        more_list = set_more_list(list_length)
        test_date = datetime.datetime.now() - datetime.timedelta(days=12)
        with self.assertRaises(SystemExit):
            PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                           ret_val=5, is_offline=False)
        mock_input.assert_any_call(more_list)

        mock_input.reset_mock()
        mock_input.side_effect = ['y']

        return_val = PocketDelDupes.check_sync_date(test_date.timestamp(), length_of_current_list=list_length,
                                                    ret_val='all', is_offline=False)
        self.assertEqual(return_val, True)
        mock_input.assert_called_with(resync_msg)

    @patch('PocketDelDupes.clean_db')
    @patch('PocketDelDupes.url_test')
    def test_prepare_articles_dict(self, mock_url_test, mock_clean_db):
        mock_clean_db.return_value = self.example_articles_cleaned
        sync_time = str(int(time.time()))
        ret_val = PocketDelDupes.prepare_articles_dict(({'list': self.example_articles, 'since': sync_time},
                                                        {'header': 'HTTP'}))
        mock_url_test.assert_called()
        mock_clean_db.assert_called()
        self.assertEqual(ret_val, (sync_time, self.example_articles_cleaned))

    def test_get_starting_side(self):
        start_args = {'detailType': 'complete'}
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['']
            result = PocketDelDupes.get_starting_side(start_args)
            self.assertEqual(result, {'detailType': 'complete', 'sort': 'newest'})

            mock_input.side_effect = ['n']
            result = PocketDelDupes.get_starting_side(start_args)
            self.assertEqual(result, {'detailType': 'complete', 'sort': 'newest'})

            mock_input.side_effect = ['o']
            result = PocketDelDupes.get_starting_side(start_args)
            self.assertEqual(result, {'detailType': 'complete', 'sort': 'oldest'})

            mock_input.side_effect = ['x', 'y', 'o']
            result = PocketDelDupes.get_starting_side(start_args)
            self.assertEqual(result, {'detailType': 'complete', 'sort': 'oldest'})

            mock_input.side_effect = ['x', 'n']
            with self.assertRaises(SystemExit):
                PocketDelDupes.get_starting_side(start_args)

    def test_article_retrieval_quantity(self):
        start_args = {'detailType': 'complete', 'sort': 'oldest'}
        with patch('PocketDelDupes.input') as mock_input:
            mock_input.side_effect = ['all']
            result = PocketDelDupes.article_retrieval_quantity(start_args)
            self.assertEqual(result, 'all')

            mock_input.side_effect = ['1']
            result = PocketDelDupes.article_retrieval_quantity(start_args)
            self.assertEqual(result, 1)

            mock_input.side_effect = ['x', 'y', '1']
            result = PocketDelDupes.article_retrieval_quantity(start_args)
            self.assertEqual(result, 1)

            mock_input.side_effect = ['x', 'n']
            with self.assertRaises(SystemExit):
                PocketDelDupes.article_retrieval_quantity(start_args)

    @patch('PocketDelDupes.article_retrieval_quantity')
    @patch('PocketDelDupes.get_starting_side')
    @patch('PocketDelDupes.load_articles_from_disk')
    @patch('PocketDelDupes.Pocket')
    def test_retrieve_articles(self, mock_instance, mock_load, mock_start, mock_quantity):
        sync_time = str(int(time.time()))

        def set_mock_start(start='oldest'):
            mock_start.return_value = {'detailType': 'complete', 'sort': f'{start}'}

        def set_instance_response(value='all'):
            divide_mod = 0
            responses = []
            large_art_length = len(self.large_article_list)
            if value == 'all':
                value = 5000
            if value < 5000 or value >= large_art_length:
                divide = 1
            else:
                divide_mod = large_art_length % value
                divide = large_art_length / value
                if divide_mod != 0:
                    divide += 1

            loop = int(divide)

            for x in range(loop):
                responses.append(
                    ({'list': {z: k for i, (z, k) in enumerate(self.large_article_list.items()) if
                               (value * x) <= i < (value * x * 2 if x > 0 else value)}, 'since': sync_time},
                     {'header': 'HTTP'})
                )
            if divide_mod == 0:
                responses.append(
                    ({'list': {}, 'since': sync_time},
                     {'header': 'HTTP'})
                )

            return tuple(responses)

        with patch('PocketDelDupes.input') as mock_input:
            for num in [1, 50, 100, 500, 1025, 5173, 12863, 14928, 15184, 23497, 25530, 'all']:
                mock_load.return_value = None
                set_mock_start()
                mock_quantity.return_value = num
                get_resp = set_instance_response(mock_quantity.return_value)
                mock_instance.get.side_effect = get_resp
                clean_arts = PocketDelDupes.clean_db(get_resp[0][0]['list'])
                result = PocketDelDupes.retrieve_articles(mock_instance, False)
                self.assertEqual(result, (sync_time, clean_arts))

                mock_instance.reset_mock()

                mock_load.return_value = (sync_time, clean_arts)
                set_mock_start()
                mock_quantity.return_value = num
                mock_input.side_effect = ['n']
                result = PocketDelDupes.retrieve_articles(mock_instance, False)
                if num == 'all':
                    expected_result = {k: v for k, v in clean_arts.items()}
                else:
                    expected_result = {k: v for k, v in clean_arts.items() if int(k) <= num}

                self.assertEqual(result, (sync_time, expected_result), msg=f"Not equal when num is {num}.")
                mock_instance.get.assert_not_called()

                mock_instance.reset_mock()

                for side in ['newest', 'oldest']:
                    mock_load.return_value = (sync_time, clean_arts)
                    set_mock_start(side)
                    mock_quantity.return_value = num
                    get_resp = set_instance_response(mock_quantity.return_value)
                    mock_instance.get.side_effect = get_resp
                    mock_input.side_effect = ['y']
                    result = PocketDelDupes.retrieve_articles(mock_instance, False)
                    if num == 'all':
                        expected_result = {k: v for k, v in clean_arts.items()}
                    else:
                        expected_result = {k: v for k, v in clean_arts.items() if int(k) <= num}

                    self.assertEqual(result, (sync_time, expected_result), msg=f"Not equal when num is {num}.")

                    mock_instance.reset_mock()

            mock_load.return_value = None
            set_mock_start()
            mock_quantity.return_value = 57
            mock_input.side_effect = 'y'
            get_resp = set_instance_response(mock_quantity.return_value)
            mock_instance.get.side_effect = get_resp

            # Very large tests - not for normal testing!
            # self.large_article_list = {}
            # for k, v in self.create_large_dict(1000000):
            #     self.large_article_list[k] = v
            #
            # for num in [1000, 5000, 10000, 15000, 20000, 25000, 50000, 100000, 500000, 1000000, 5000000, 10000000]:
            #     mock_load.return_value = None
            #     mock_start.return_value = {'detailType': 'complete', 'sort': 'oldest'}
            #     mock_quantity.return_value = num
            #     get_resp = set_instance_response(mock_quantity.return_value)
            #     mock_instance.get.side_effect = get_resp
            #     clean_arts = PocketDelDupes.clean_db(get_resp[0][0]['list'])
            #     # mock_input.side_effect = ['y']
            #     result = PocketDelDupes.retrieve_articles(mock_instance)
            #     self.assertEqual(result, (sync_time, clean_arts))
            #
            #     mock_instance.reset_mock()

        mock_load.return_value = (sync_time, self.example_articles_cleaned)
        mock_start.return_value = {'detailType': 'complete', 'sort': 'oldest'}
        mock_quantity.return_value = 0
        with self.assertRaises(SystemExit):
            PocketDelDupes.retrieve_articles(mock_instance, False)

    @patch('PocketDelDupes.Pocket', autospec=PocketDelDupes.Pocket)
    def test_main(self, mock_instance):
        in_mocks = {'create_arg_parser': DEFAULT, 'pocket_authenticate': DEFAULT, 'retrieve_articles': DEFAULT,
                    'del_dupes': DEFAULT, 'save_articles_to_disk': DEFAULT, 'add_items': DEFAULT,
                    'delete_items': DEFAULT, 'view_items': DEFAULT, 'tags_editing': DEFAULT, 'exit_strategy': DEFAULT}
        with patch.multiple('PocketDelDupes', **in_mocks) as mocks:
            def reset_mocks(m):
                for x in m:
                    m[x].reset_mock()

            def assertion_tests(side_effects):
                mocks['create_arg_parser'].return_value = PocketDelDupes.create_arg_parser().parse_args(['key'])
                mocks['create_arg_parser'].reset_mock()
                mocks['pocket_authenticate'].return_value = mock_instance
                mocks['retrieve_articles'].return_value = (str(int(time.time())), self.example_articles)
                mocks['del_dupes'].return_value = self.example_articles_cleaned
                mocks['exit_strategy'].side_effect = SystemExit

                with patch('PocketDelDupes.input') as mock_input:
                    mock_input.side_effect = side_effects
                    with self.assertRaises(SystemExit):
                        PocketDelDupes.main()

                self.assertEqual(mocks['create_arg_parser'].call_count, 1)
                mocks['pocket_authenticate'].assert_called_once()
                mocks['save_articles_to_disk'].assert_called_once()
                if side_effects[0] == 'y':
                    mocks['del_dupes'].assert_called_with(self.example_articles, mock_instance)
                    article_list = self.example_articles_cleaned
                else:
                    mocks['del_dupes'].assert_not_called()
                    article_list = self.example_articles
                mocks['add_items'].assert_called_with(mock_instance)
                mocks['delete_items'].assert_called_with(mock_instance, article_list)
                mocks['view_items'].assert_called_with(article_list)
                mocks['tags_editing'].assert_called_with(mock_instance, article_list)
                mocks['exit_strategy'].assert_called()

            assertion_tests(['y', 'a', 'd', 'v', 't', 'x', 'y', 'e'])
            reset_mocks(mocks)
            assertion_tests(['n', 'a', 'd', 'v', 't', 'x', 'y', 'e'])
            reset_mocks(mocks)
            assertion_tests(['n', 'a', 'd', 'v', 't', 'x', 'n'])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
