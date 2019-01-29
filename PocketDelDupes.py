#!/usr/bin/env python

import argparse
import datetime
import os
import pickle
import re
import time
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

    # print('------ ')
    # print('Now opening a browser tab to authenticate with Pocket')
    # print('When finished, press ENTER here...')
    # print('------ ')

    # Open web browser tab to authenticate with Pocket
    webbrowser.open_new_tab(auth_url)

    # Wait for user to hit ENTER before proceeding
    # input()
    time.sleep(3)

    access_token = Pocket.get_access_token(
        consumer_key=con_key,
        code=request_token, )

    print('Got authenticated request token - ' + request_token)

    instance = Pocket(con_key, access_token)
    return instance


def output_bad(list_of_bad, save_bad=False, print_bad=False):
    if save_bad:
        file_directory = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(file_directory, 'BadItems.txt')) as bad:
            bad.writelines(list_of_bad)
    if print_bad:
        for item in list_of_bad:
            print(item)


def url_test(art_list):
    """This tests for invalid resolved urls and lists them for the user to fix, if the user so desires.
    TODO: Give the user the option to continue, ignoring the bad articles"""
    var_error = 0
    bad_list = []
    option = ''
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
            print('Would you like the bad URLs [p]rinted on screen, [s]aved to a file, [n]either, or [b]oth?')
            option = input('Leave empty to exit the program: ').lower()
            if option == '':
                exit_strategy()
            elif option not in processing_options:
                if not try_again():
                    return
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
            output_bad(art_list, save_bad=to_save, print_bad=to_print)


def filterurl(url, char):
    """ Function to prune off extra URL options """
    try:
        return url[:url.index(char)]
    except ValueError:
        return url


def clean_db(raw_article_list):
    # This dictionary is a straight copy of the data from Pocket, but
    # with only the ID and URL properties.
    # It will also strip all of the extra social media info from each URL.
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
    # This dictionary will hold only unique entries
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

    print("Here are the articles that are duplicates:")
    for i, (k, v) in enumerate(dupe_dict.items()):
        print(i + 1, k, '- IDs: ' + ', '.join(v))
        ids_to_delete.extend(v[:-1] if len(v) > 1 else v[0])
    while not confirm_delete:
        confirm_delete = input(
            "Do you want to delete these duplicates? The article(s) most recently added will be removed. (Y/N)").lower()
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
              " unique articles in your Pocket list.")
    return masterdict


def items_to_manipulate():
    """Gets the list of items to act on."""
    while True:
        items = input("What are the items? "
                      "Separate URLs or IDs with a comma,"
                      " or provide the path of a text file with each item "
                      "on a separate line. Leave empty to return to the main menu. ")
        manip = []
        if items[-4:].lower() == '.txt':
            try:
                with open(os.path.normcase(items), "r", encoding='utf-8') as al:
                    manip.append(line.rstrip() for line in al)
            except IOError:
                print("That file does not exist.")
                if not try_again():
                    return
        elif items == '':
            return
        else:
            manip = [x.strip() for x in items.split(',')]
        return manip


def try_again():
    decision = ''
    while decision == '':
        decision = input("That is not valid, would you like to try again? (y/n)").lower()
        if decision == 'n':
            return False
        elif decision == 'y':
            return True
        else:
            print('That is not a valid choice.')
            decision = ''


def sort_items(dict_of_articles):
    key_list = {'n': 'resolved_title',
                'd': 'time_added',
                'l': 'word_count',
                'u': 'resolved_url'}
    direction = ''

    while True:
        sort_order = input("What would you like to sort by "
                           "([N]ame/[D]ate/[L]ength/[U]RL)? ").lower()
        if sort_order not in key_list.keys():
            if not try_again():
                return
        else:
            while not direction:
                direction = input("How would you like to sort the articles "
                                  "([F]orward/[B]ackward)? )").lower()
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


# def article_display_generator(input_dict):
#     while True:
#         for art in input_dict:
#             yield art[0]


def display_items(articles_in_account):
    art_disp = ''
    v_url = ''
    while not v_url:
        v_url = input("Do you wish to view the URL with the article "
                      "information (y/n, default n)?").lower()
        if v_url == '':
            v_url = 'n'
        elif v_url not in ['y', 'n']:
            if not try_again():
                return
            else:
                v_url = ''
    while not art_disp:
        art_disp = input("How many articles would you like to view "
                         "at once? Type \"all\" to view all"
                         " articles. "
                         )
        print()
        if art_disp == 'all':
            for art in articles_in_account:
                print_items_info(articles_in_account, art, v_url)
        elif art_disp != '':
            try:
                print(
                    'Press enter to view another page of articles, or enter any character to return to the main menu.\n'
                )
                art_disp = int(art_disp)
                # article = article_display_generator(sorted_articles)
                article = (x for x in articles_in_account)
                article_groups = int(len(articles_in_account) / art_disp)
                article_groups_extra = len(articles_in_account) % art_disp
                for i in range(article_groups):
                    for count in range(art_disp):
                        art_id = next(article)
                        print_items_info(articles_in_account, art_id, v_url)
                    if article_groups > 1 and i != (article_groups - 1):
                        view_more_arts = input()
                        if view_more_arts != '':
                            return
                        else:
                            break
                    else:
                        print()
                if article_groups_extra != 0:
                    print()
                    for count in range(article_groups_extra):
                        art_id = next(article)
                        print_items_info(articles_in_account, art_id, v_url)
                    print()
            except ValueError:
                if not try_again():
                    return
                else:
                    art_disp = ''


def validate_url(link):
    if not link.startswith('/'):
        link_fixed = f'//{link}'
    else:
        link_fixed = link
    url = urlparse(link_fixed, scheme='http')
    if validators.url(url.geturl()):
        return url.geturl(), link
    else:
        return False, False


def get_article_url(id_url_dict, url, link):
    for article in id_url_dict:
        if id_url_dict[article]['resolved_url'] == url or id_url_dict[article]['resolved_url'] == link:
            return article
        else:
            print(str(link) +
                  " was not found in the list. "
                  "Nothing related to this item will be modified.")
            return False


def add_items(instance):
    """Allows adding items to the list"""
    while True:
        valid_count = 0
        add_list = items_to_manipulate()
        if not add_list:
            return
        elif add_list[0] != -1:
            for item in add_list:
                url, _ = validate_url(item)
                if url:
                    instance.add(url)
                    valid_count += 1
                else:
                    print(f"{item} is not a valid URL, "
                          "and will be disregarded.")
            if valid_count > 0:
                instance.commit()
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
                url, link = validate_url(item)
                if url:
                    item_id = get_article_url(id_url_dict, url, link)
                    if item_id:
                        instance.delete(item_id)
                        commit = True
                else:
                    if re.search(r'[\D]', item):
                        print(f'{item} is not a valid ID, please limit item IDs to numbers only.')
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


def tags_editing(instance, full_list):
    """Allows editing of the tags."""
    print()
    list_tags = input('Would you like to list tags for all articles? (y/n) ')
    if list_tags.lower() == 'y':
        dict_art_tags = {}
        for item in full_list:
            try:
                # print(full_list[item]['tags'])
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

            edit_tags = input('Do you wish to remove all tags? (y/n) ')
            if edit_tags == 'y':
                for item_id in full_list:
                    instance.tags_clear(item_id)
                instance.commit()
        else:
            print("None of the articles have tags!")


def load_articles_from_disk():
    if not os.path.exists('article_list'):
        print('No previous sync detected - proceeding by retrieving articles from website.')
        return
    else:
        with open('article_list', 'rb') as fin:
            current_list = pickle.loads(fin.read())
        with open('last_sync', 'rb') as lsin:
            last_sync = pickle.loads(lsin.read())
    return current_list, last_sync


def save_articles_to_disk(article_dict, last_sync_date):
    if os.path.exists('article_list'):
        os.replace('article_list', 'article_list.bak')
    with open('article_list', 'wb') as fout:
        pickle.dump(article_dict, fout)
    with open('last_sync', 'wb') as lsout:
        pickle.dump(last_sync_date, lsout)


def check_sync_date(sync_date):

    if datetime.datetime.fromtimestamp(int(sync_date)) < datetime.datetime.now() - datetime.timedelta(days=14):
        resync = input('The saved list of articles has not been synchronized in two weeks. '
                       'Would you like to update the saved list? (Y/N) ').lower()
        if resync == 'y':
            return True
        else:
            return False


def prepare_articles_dict(items):
    full_list = items[0]['list']
    retrieval_time = items[0]['since']
    url_test(full_list)
    # Clean and parse data
    cleaned_dict = clean_db(full_list)
    return cleaned_dict, retrieval_time


def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    pocket_instance = pocket_authenticate(args.api_key)
    retrieval_arguments = {'detailType': 'complete'}
    start_from = ''
    arts_to_retrieve = ''
    while not start_from:
        start_from = input(
            'Would you like to retrieve articles starting from the [O]ldest or [N]ewest? (Default is Newest) ').lower()
        if start_from == '' or start_from == 'n':
            start_from = 'n'
            retrieval_arguments['sort'] = 'newest'
        elif start_from == 'o':
            retrieval_arguments['sort'] = 'oldest'
        elif start_from not in ['o', 'n']:
            if not try_again():
                exit_strategy()
            else:
                start_from = ''
    while not arts_to_retrieve:
        arts_to_retrieve = input(
            f"How many of the {retrieval_arguments['sort']} articles would you like to get? (Default is all) ").lower()
        if arts_to_retrieve == '' or arts_to_retrieve == 'all':
            break
        else:
            try:
                arts_to_retrieve = int(arts_to_retrieve)
                retrieval_arguments['count'] = arts_to_retrieve
            except ValueError:
                if not try_again():
                    exit_strategy()
                else:
                    arts_to_retrieve = ''
    items_list = load_articles_from_disk()
    if not items_list:
        items_list = pocket_instance.get(**retrieval_arguments)
        master_article_dictionary, retrieval_time = prepare_articles_dict(items_list)
    else:
        if check_sync_date(items_list[1]):
            items_list = pocket_instance.get(**retrieval_arguments)
            master_article_dictionary, retrieval_time = prepare_articles_dict(items_list)
        else:
            master_article_dictionary = items_list[0]
            retrieval_time = items_list[1]

    # Option to check for and delete duplicates
    check_dupes = input('Would you like to check for and delete any duplicate articles [y]es/[n]o? ')
    if check_dupes.lower() == 'y':
        print()
        master_article_dictionary = del_dupes(master_article_dictionary, pocket_instance)

    save_articles_to_disk(master_article_dictionary, retrieval_time)

    while True:
        choice = input("What would you like to do ([A]dd/[D]elete/[V]iew/[T]ags/[E]xit)? ").lower()
        if choice == "e":
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


if __name__ == '__main__':
    main()
