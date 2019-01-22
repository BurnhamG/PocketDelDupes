#!/usr/bin/env python

import argparse
import datetime
import os
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
    if save_bad:
        file_directory = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(file_directory, 'BadItems.txt')) as bad:
            bad.writelines(list_of_bad)
    if print_bad:
        for item in list_of_bad:
            print(item)


def url_test(art_list):
    """This tests for invalid resolved urls and lists them for the user to fix, if the user so desires."""
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
    # TODO: Restructure this to match raw data style
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
          " total articles in your Pocket list.\n")
    return masterdict


def del_dupes(masterdict, instance):
    # This dictionary will hold only unique entries
    resolved_urls = []
    filtereddict = {}

    # This loop will find the duplicate URLs and delete them from the list
    delete_count = 0
    for k, v in masterdict.items():
        if v['resolved_url'] not in resolved_urls:
            resolved_urls.append(v['resolved_url'])
            filtereddict[k] = v
        else:
            print("Removing duplicate: " + v['resolved_url'])
            delete_count += 1
            instance.delete(str(k), wait=False)

    print(str(delete_count) + ' items were deleted.')
    print('There are now ' + str(len(filtereddict)) +
          " unique articles in your Pocket list.")
    return filtereddict


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


def sort_items(dict_of_articles, sort_category):
    direction = ""
    while not direction:
        direction = input("How would you like to sort the articles "
                          "([F]orward/[B]ackward)? )".lower())
        if direction == 'b':
            return sorted(dict_of_articles.items(),
                          key=lambda x: int(x[1][sort_category]),
                          reverse=True)
        elif direction == 'f':
            return sorted(dict_of_articles.items(),
                          key=lambda x: int(x[1][sort_category]))
        else:
            if try_again():
                direction = ''
            else:
                break


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
        if v_url not in ['y', 'n']:
            if not try_again():
                return
            else:
                v_url = ''
    while not art_disp:
        art_disp = input("How many articles would you like to view "
                         "at once? Type \"all\" to view all"
                         " articles. "
                         )
        if art_disp == 'all':
            for art in articles_in_account:
                print_items_info(articles_in_account, art, v_url)
        elif art_disp != '':
            try:
                art_disp = int(art_disp)
                # article = article_display_generator(sorted_articles)
                article = (x for x in articles_in_account)
                for count in range(art_disp):
                    art_id = next(article)
                    print_items_info(articles_in_account, art_id, v_url)
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
    key_list = {'n': 'resolved_title',
                'd': 'time_added',
                'l': 'word_count',
                'u': 'resolved_url'}

    while True:
        sort_order = input("What would you like to sort by "
                           "([N]ame/[D]ate/[L]ength/[U]RL)? ").lower()
        if sort_order not in key_list.keys():
            if not try_again():
                return
        else:
            sorted_names = dict(sort_items(art_dict, key_list[sort_order]))
            display_items(sorted_names)
            return


def tags_editing(instance, full_list):
    """Allows editing of the tags."""
    print()
    list_tags = input('Would you like to list all the tags? (y/n) ')
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

        print("Here are the tags, along with their frequency: ", sorted(dict_art_tags.items(), key=lambda x:x[1],
                                                                        reverse=True))

    edit_tags = input('Do you wish to remove all tags? (y/n) ')
    if edit_tags == 'y':
        for item_id in full_list:
            instance.tags_clear(item_id)
        instance.commit()


def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    pocket_instance = pocket_authenticate(args.api_key)
    items_list = pocket_instance.get(count=10, detailType='complete')
    full_list = items_list[0]['list']

    url_test(full_list)

    # Clean and parse data
    master_article_dictionary = clean_db(full_list)

    # Option to check for and delete duplicates
    check_dupes = input('Would you like to check for and delete any duplicate articles [y]es/[n]o? ')
    if check_dupes.lower() == 'y':
        master_article_dictionary = del_dupes(master_article_dictionary, pocket_instance)

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
