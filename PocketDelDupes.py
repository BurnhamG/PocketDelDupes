#!/usr/bin/env python

import argparse
import datetime
import os
import pickle
import re
import webbrowser
from urllib.parse import urlparse

import validators
# Site here: https://github.com/tapanpandita/pocket
from pocket import Pocket


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("api_key", help="Your api key for Pocket's website.")
    return parser


def pocket_authenticate(con_key):
    request_token = Pocket.get_request_token(
        consumer_key=con_key,
        redirect_uri='https://ddg.gg',
    )
    auth_url = Pocket.get_auth_url(
        code=request_token,
        redirect_uri='https://ddg.gg',
    )

    print('------ ')
    print('Now opening a browser tab to authenticate with Pocket')
    print('When finished, press ENTER here...')
    print('------ ')

    # Open web browser tab to authenticate with Pocket
    webbrowser.open_new_tab(auth_url)

    # Wait for user to hit ENTER before proceeding
    input()

    access_token = Pocket.get_access_token(
        consumer_key=con_key,
        code=request_token, )

    print('Got authenticated request token - ' + request_token)

    instance = Pocket(con_key, access_token)
    return instance


def output_bad(list_of_bad, save_bad=False, print_bad=False):
    """Saves and/or displays bad articles"""
    if save_bad:
        file_directory = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(file_directory, 'BadItems.txt')) as bad:
            bad.writelines(list_of_bad)
    if print_bad:
        for item in list_of_bad:
            print(item)


def url_test(art_list):
    """Tests for invalid resolved urls and lists them for the user to fix, if the user so desires."""
    var_error = 0
    bad_list = []
    option = ''
    to_continue = ''
    to_print = False
    to_save = False
    processing_options = ['b', 'n', 'p', 's']
    for item in art_list:
        try:
            art_list[item]['resolved_url']
        except KeyError:
            bad_list.append('https://getpocket.com/a/read/' + item)
            var_error = 1
    if var_error == 1:
        print('There were some articles with bad URLs.')
        while not option:
            print('Would you like the bad URLs [P]rinted on screen, [S]aved to a file, [N]either, or [B]oth?')
            option = input('Leave empty to exit the program: ').lower()
            if option == '':
                exit_strategy()
            elif option not in processing_options:
                if not try_again():
                    exit_strategy()
                else:
                    option = ''
            elif option == 'n':
                break
            elif option == 'p':
                to_print = True
            elif option == 's':
                to_save = True
            elif option == 'b':
                to_print = to_save = True
            output_bad(bad_list, save_bad=to_save, print_bad=to_print)
        while not to_continue:
            to_continue = input('Would you like to continue the program? [Y]es/[N]o').lower()
            if to_continue == 'y':
                return
            elif to_continue == 'n':
                exit_strategy()
            else:
                if not try_again():
                    exit_strategy()
                else:
                    to_continue = ''


def filterurl(url, char):
    """Prunes off extra URL options"""
    try:
        return url[:url.index(char)]
    except ValueError:
        return url


def clean_db(raw_article_list):
    """Returns only the article information and strips all of the extra social media info from each URL."""
    masterdict = {}
    # url_id_dict = {}

    print(raw_article_list)
    for item in raw_article_list:
        article_id = raw_article_list[item]['item_id']
        article_time = raw_article_list[item]['time_added']
        article_title = raw_article_list[item]['resolved_title']
        article_url = raw_article_list[item]['resolved_url']
        word_count = raw_article_list[item]['word_count']
        try:
            article_tags = list(raw_article_list[item]['tags'].keys())
        except KeyError:
            article_tags = {}

        # Remove extra junk from URLS (DANGEROUS - don't remove too much!)
        article_url = filterurl(article_url, '?utm')
        article_url = filterurl(article_url, '&utm')
        article_url = filterurl(article_url, '?roi')
        article_url = filterurl(article_url, '?mc')

        # article_url = filterurl(article_url, '#')
        # url_id_dict[article_id] = article_url
        masterdict[article_id] = {}
        masterdict[article_id]['resolved_url'] = article_url
        masterdict[article_id]['word_count'] = word_count
        masterdict[article_id]['tags'] = article_tags
        masterdict[article_id]['resolved_title'] = article_title
        masterdict[article_id]['time_added'] = article_time

    print('\n' + str(len(masterdict)) +
          " total articles retrieved from your Pocket list.\n")
    return masterdict


def del_dupes(masterdict, instance):
    """Removes duplicate items from the user's list."""
    ids_to_delete = []
    reversed_dict = {}
    confirm_delete = ''
    for k, v in masterdict.items():
        if v['resolved_url'] in reversed_dict.keys():
            reversed_dict[v['resolved_url']].append(k)
        else:
            reversed_dict[v['resolved_url']] = [k]

    dupe_dict = {masterdict[v[0]]['resolved_title']: sorted(v, reverse=True) for k, v in reversed_dict.items() if
                 len(reversed_dict[k]) > 1}

    if len(dupe_dict) > 0:
        print('Here are the articles that are duplicates:')
        for i, (k, v) in enumerate(dupe_dict.items()):
            print(i + 1, k, '- IDs: ' + ', '.join(v))
            ids_to_delete.extend(v[:-1] if len(v) > 1 else v[0])
        while not confirm_delete:
            confirm_delete = input('Do you want to delete these duplicates? '
                                   'The article(s) most recently added will be removed. (Y/N)').lower()
            if confirm_delete == '':
                confirm_delete = 'n'
            elif confirm_delete not in ['y', 'n']:
                if not try_again():
                    return
                else:
                    confirm_delete = ''
        if confirm_delete == 'y':
            # This loop will delete duplicates from the list
            for x in ids_to_delete:
                instance.delete(x)
                del masterdict[x]
            instance.commit()
            print(str(len(ids_to_delete)) + ' items were deleted.')
            print('There are now ' + str(len(masterdict)) +
                  ' unique articles in your Pocket list.')
    else:
        print('No duplicates found!\n')
    return masterdict


def items_to_manipulate():
    """Gets the list of items to act on."""
    while True:
        items = input('What are the items? '
                      'Separate URLs or IDs with a comma, '
                      'or provide the path of a text file with each item '
                      'on a separate line. Leave empty to return to the main menu. ')
        manip = []
        if validators.url(items.split(',')[0]) is not True:
            try:
                with open(os.path.normcase(items), "r", encoding='utf-8') as al:
                    manip = [line.strip() for line in al]
            except IOError:
                print('That file does not exist.')
                if not try_again():
                    return
        elif items == '':
            return
        else:
            manip = [x.strip() for x in items.split(',')]
        return manip


def try_again():
    """Gives user the option to quit or retry."""
    decision = ''
    while decision == '':
        decision = input('That is not valid, would you like to try again? (Y/N)').lower()
        if decision == 'n':
            return False
        elif decision == 'y':
            return True
        else:
            print('That is not a valid choice.')
            decision = ''


def sort_items(dict_of_articles):
    """Sorts the items for display."""
    key_list = {'n': 'resolved_title',
                'd': 'time_added',
                'l': 'word_count',
                'u': 'resolved_url'}
    direction = ''
    reverse_opt = False

    while True:
        sort_order = input('What would you like to sort by '
                           '([N]ame/[D]ate/[L]ength/[U]RL)? ').lower()
        if sort_order not in key_list.keys():
            if not try_again():
                return
        else:
            while not direction:
                direction = input('How would you like to sort the articles '
                                  '([F]orward/[B]ackward)? )').lower()
                if direction == 'b':
                    reverse_opt = True
                elif direction == 'f':
                    reverse_opt = False
                else:
                    if not try_again():
                        return
                    direction = ''
            if sort_order == 'l':
                return sorted(dict_of_articles.items(), key=lambda x: int(x[1][key_list[sort_order]]),
                              reverse=reverse_opt)
            else:
                return sorted(dict_of_articles.items(), key=lambda x: x[1][key_list[sort_order]], reverse=reverse_opt)


def print_items_info(all_articles, article, v_url='n'):
    """Prints information for each article."""
    time_art_added = datetime.datetime.fromtimestamp(int(all_articles[article]['time_added']))
    if v_url == 'y':
        output_end = f"URL is {all_articles[article]['resolved_url']}."
    else:
        output_end = ''
    print(f"{all_articles[article]['resolved_title']}, added {time_art_added}, with "
          f"{all_articles[article]['word_count']} words. {output_end}")


def exit_strategy():
    print('Goodbye!')
    raise SystemExit


def display_items(articles_in_account):
    art_disp = ''
    v_url = ''
    view_more_arts = ''
    while not v_url:
        v_url = input("Do you wish to view the URL with the article "
                      "information (Y/N, default N)?").lower()
        if v_url == '':
            v_url = 'n'
        elif v_url not in ['y', 'n']:
            if not try_again():
                return
            else:
                v_url = ''
    while not art_disp:
        art_disp = input("How many articles would you like to view "
                         "at once? Type \"ALL\" to view all"
                         " articles. "
                         ).lower()
        print()
        if art_disp == 'all':
            for art in articles_in_account:
                print_items_info(articles_in_account, art, v_url)
        elif art_disp != '':
            try:
                while not view_more_arts:
                    art_disp = int(art_disp)
                    print(
                        'Press enter to view another page of articles, '
                        'or any other character to return to the main menu.\n'
                    )
                    article = (x for x in articles_in_account)
                    article_groups = int(len(articles_in_account) / art_disp)
                    article_groups_extra = len(articles_in_account) % art_disp
                    for i in range(article_groups):
                        for count in range(art_disp):
                            art_id = next(article)
                            print_items_info(articles_in_account, art_id, v_url)
                        view_more_arts = input()
                        if view_more_arts != '':
                            return
                    print()
                    if article_groups_extra != 0:
                        print()
                        for count in range(article_groups_extra):
                            art_id = next(article)
                            print_items_info(articles_in_account, art_id, v_url)
                        print()
                    view_more_arts = -1

            except ValueError:
                if not try_again():
                    return
                else:
                    art_disp = ''


def validate_url(link):
    link = link.strip()
    if not link.startswith('http') and not link.startswith('//'):
        if link.startswith('/'):
            link_fixed = f"/{link}"
        else:
            link_fixed = f"//{link}"
    else:
        link_fixed = link
    url = urlparse(link_fixed, scheme='http')
    if validators.url(url.geturl()):
        return url.geturl()
    else:
        return False


def get_article_url(id_url_dict, url):
    for article in id_url_dict:
        if id_url_dict[article]['resolved_url'] == url:
            return article
        else:
            print(str(url) +
                  ' was not found in the list. '
                  'Nothing related to this item will be modified.')
            return False


def add_items(instance):
    """Allows adding items to the list"""
    while True:
        valid_count = 0
        add_list = items_to_manipulate()
        if not add_list:
            return
        elif add_list[0] != -1:
            print('Processing items...')
            for item in add_list:
                art_url = validate_url(item)
                if art_url:
                    instance.bulk_add(url=art_url)
                    valid_count += 1
                else:
                    print(f"{item} is not a valid URL, "
                          "and will be disregarded.")
            if valid_count > 0:
                instance.commit()
                print(f"{valid_count} items successfully added!")
                return
            else:
                if not try_again():
                    return


def delete_items(instance, id_url_dict):
    """Allows removing items from the list"""
    commit = False
    while True:
        delete_list = items_to_manipulate()
        if not delete_list:
            return
        elif delete_list[0] != -1:
            for item in delete_list:
                url = validate_url(item)
                if url:
                    item_id = get_article_url(id_url_dict, url)
                    if item_id:
                        instance.delete(item_id)
                        commit = True
                else:
                    if re.search(r'[\D]', item):
                        print(f"{item} is not a valid ID, please limit item IDs to numbers only.")
                        if not try_again():
                            return
                    else:
                        instance.delete(item)
                        commit = True
        if commit:
            instance.commit()
            return


def view_items(art_dict):
    """Allows the user to view information about their list items."""

    sorted_names = sort_items(art_dict)
    if sorted_names:
        display_items(dict(sorted_names))
    return


def tags_editing(instance, full_list, is_offline=False):
    """Allows editing of the tags."""
    print()
    dict_art_tags = {}
    for item in full_list:
        try:
            article_tags = full_list[item]['tags']
            for t in article_tags:
                if t not in dict_art_tags.keys():
                    dict_art_tags[t] = 1
                else:
                    dict_art_tags[t] += 1
        except KeyError:
            pass
    if dict_art_tags:
        print("Here are the tags, along with their frequency: ", sorted(dict_art_tags.items(), key=lambda x: x[1],
                                                                        reverse=True))
        if not is_offline:
            edit_tags = input('Do you wish to remove all tags? (Y/N) ').lower()
            if edit_tags == 'y':
                for item_id in full_list:
                    instance.tags_clear(item_id)
                instance.commit()
    else:
        print("None of the articles have tags!")


def load_articles_from_disk():
    def no_load():
        print('No previous sync detected - proceeding by retrieving articles from website.')

    if not os.path.exists('article_list'):
        no_load()
        return
    else:
        with open('article_list', 'rb') as fin:
            try:
                sync_and_articles = pickle.loads(fin.read())
                print(f"{len(sync_and_articles[1])} items loaded from disk.")
            except EOFError:
                no_load()
                return

    return sync_and_articles[0], sync_and_articles[1]


def save_articles_to_disk(article_dict, last_sync_date):
    if os.path.exists('article_list'):
        os.replace('article_list', 'article_list.bak')
    with open('article_list', 'wb') as fout:
        pickle.dump([last_sync_date, article_dict], fout)


def check_sync_date(sync_date, length_of_current_list, ret_val, is_offline):
    resync = ''
    if not is_offline:
        if ret_val == 'all':
            resync_string = ('By default, we will show you all saved articles. Do you want to update ALL articles?\n'
                             'WARNING: This will potentially take a long time, as it will retrieve ALL articles from '
                             'Pocket. (Y/N) ')
        elif datetime.datetime.fromtimestamp(int(sync_date)) < datetime.datetime.now() - datetime.timedelta(days=14):
            resync_string = ('The saved list of articles has not been synchronized in two weeks. '
                             'Would you like to update the saved list? (Y/N) ')
        elif type(ret_val) == int and ret_val > length_of_current_list:
            resync_string = (
                f"You are requesting more articles than the {length_of_current_list} that are currently saved."
                ' Would you like to update the saved list? (Y/N) ')
        else:
            resync_string = ('The saved list of articles has been synchronized in the past two weeks. '
                             'Would you like to update the saved list anyway? (Y/N) ')

        while not resync:
            resync = input(resync_string).lower()
            if resync == 'y':
                return True
            elif resync == 'n':
                return False
            else:
                if not try_again():
                    exit_strategy()
                else:
                    resync = ''
    else:
        print('You are offline, unable to sync at this time.')
        print(f"The last synchronization was {datetime.datetime.fromtimestamp(int(sync_date))}.")
        return False


def prepare_articles_dict(items):
    full_list = items[0]['list']
    retrieval_time = items[0]['since']
    url_test(full_list)
    # Clean and parse data
    cleaned_dict = clean_db(full_list)
    return retrieval_time, cleaned_dict


def get_starting_side(ret_args):
    start_from = ''
    while not start_from:
        start_from = input(
            'Would you like to retrieve articles starting from the [O]ldest or [N]ewest? (Default is Newest) ').lower()
        if start_from == '' or start_from == 'n':
            ret_args['sort'] = 'newest'
            return ret_args
        elif start_from == 'o':
            ret_args['sort'] = 'oldest'
            return ret_args
        elif start_from not in ['o', 'n']:
            if not try_again():
                exit_strategy()
            else:
                start_from = ''


def article_retrieval_quantity(sort_type):
    arts_to_retrieve = ''
    while not arts_to_retrieve:
        arts_to_retrieve = input(f"How many of the {sort_type} articles would you like to get? "
                                 '(Default is all, 0 exits the program) ').lower()
        if arts_to_retrieve == '' or arts_to_retrieve == 'all':
            return 'all'
        else:
            try:
                arts_to_retrieve = int(arts_to_retrieve)
                return arts_to_retrieve
            except ValueError:
                if not try_again():
                    exit_strategy()
                else:
                    arts_to_retrieve = ''


def retrieve_articles(instance, is_offline):
    get_all = False
    art_dict = None
    items_list = load_articles_from_disk()
    if not items_list and is_offline:
        print('Unfortunately there are no saved articles to retrieve.')
        exit_strategy()
    ret_args = {'detailType': 'complete'}
    ret_args = get_starting_side(ret_args)
    art_count = article_retrieval_quantity(ret_args['sort'])
    if art_count == 0:
        exit_strategy()
    elif art_count != 'all':
        ret_args['count'] = art_count
    else:
        ret_args['count'] = 5000
        ret_args['offset'] = 0
        get_all = True

    length = ret_args['count']
    if not items_list and not get_all:
        items_list = instance.get(**ret_args)
    elif not items_list and get_all:
        items_list = []
        while length == ret_args['count']:
            items_list.append(instance.get(**ret_args)[0])
            ret_args['offset'] += ret_args['count']
            length = len(items_list[-1]['list'])
    elif not get_all and items_list:
        if check_sync_date(items_list[0], len(items_list[1]), art_count, is_offline):
            if ret_args['sort'] != 'oldest':
                ret_args['since'] = items_list[0]
            items_list = instance.get(**ret_args)
        else:
            art_dict = {k: v for i, (k, v) in enumerate(items_list[1].items()) if i < art_count}
    else:
        if check_sync_date(items_list[0], len(items_list[1]), art_count, is_offline):
            if ret_args['sort'] != 'oldest':
                ret_args['since'] = items_list[0]
            items_list = []
            while length == ret_args['count']:
                items_list.append(instance.get(**ret_args)[0])
                ret_args['offset'] += ret_args['count']
                length = len(items_list[-1]['list'])

    try:
        int(items_list[0])
        ret_time = items_list[0]
        if not art_dict:
            art_dict = items_list[1]
    except TypeError:
        ret_time, art_dict = prepare_articles_dict(items_list)

    return ret_time, art_dict


def main():
    offline = False
    parser = create_arg_parser()
    args = parser.parse_args()
    try:
        pocket_instance = pocket_authenticate(args.api_key)
    except ConnectionError:
        while cont not in ['y', 'n']:
            cont = input(
                'There has been a connection error. Would you like to continue with only the saved articles? (Y/N) ').lower()
            if cont == 'n':
                exit_strategy()
            elif cont != 'y':
                print('That is not a valid option.')
            offline = True

    retrieval_time, master_article_dictionary = retrieve_articles(pocket_instance, offline)

    # Option to check for and delete duplicates
    check_dupes = input('Would you like to check for and delete any duplicate articles? '
                        'Type "y" to check, any other character to skip. ').lower()
    if check_dupes == 'y':
        print()
        master_article_dictionary = del_dupes(master_article_dictionary, pocket_instance)

    save_articles_to_disk(master_article_dictionary, retrieval_time)
    if not offline:
        while True:
            choice = input('What would you like to do ([A]dd/[D]elete/[V]iew/[T]ags/[E]xit)? ').lower()
            if choice == 'e':
                exit_strategy()
            elif choice == 'a':
                add_items(pocket_instance)
            elif choice == 'd':
                delete_items(pocket_instance, master_article_dictionary)
            elif choice == 'v':
                view_items(master_article_dictionary)
            elif choice == 't':
                tags_editing(pocket_instance, master_article_dictionary)
            else:
                if not try_again():
                    exit_strategy()
    else:
        print('You are in offline mode, functionality is limited.\n')
        while True:
            choice = input('What would you like to do ([V]iew/[T]ags/[E]xit)? ').lower()
            if choice == 'e':
                exit_strategy()
            elif choice == 'v':
                view_items(master_article_dictionary)
            elif choice == 't':
                tags_editing(pocket_instance, master_article_dictionary, offline)
            else:
                if not try_again():
                    exit_strategy()


if __name__ == '__main__':
    main()
