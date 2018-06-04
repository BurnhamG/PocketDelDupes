#!/usr/bin/env python

import datetime
import os
import sys
import webbrowser
from operator import itemgetter

# Site here: https://github.com/tapanpandita/pocket
from pocket import Pocket


def pocket_authenticate():
    # Get consumer key from cmd line
    con_key = sys.argv[1]

    request_token = Pocket.get_request_token(
        consumer_key=con_key,
        redirect_uri='http://ddg.gg',
    )
    auth_url = Pocket.get_auth_url(
        code=request_token,
        redirect_uri='http://ddg.gg',
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
        with open('BadItems.txt') as bad:
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
            option = input('Leave empty to exit the program: ')
            if option == '':
                exit_strategy()
            elif option not in processing_options:
                print('That is not a valid option, please try again')
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

    for item in raw_article_list:
        article_id = raw_article_list[item]['item_id']
        article_url = raw_article_list[item]['resolved_url']
        # word_count = raw_article_list[item]['word_count']
        # try:
        #     article_tags = raw_article_list[item]['tags'].keys()
        # except KeyError:
        #     article_tags = 'Untagged'

        # Remove extra junk from URLS (DANGEROUS - don't remove too much!)
        article_url = filterurl(article_url, '?utm')
        article_url = filterurl(article_url, '?roi')
        article_url = filterurl(article_url, '?mc')

        # article_url = filterurl(article_url, '#')
        # url_id_dict[article_id] = article_url
        masterdict[article_id] = article_url

    print('\n' + str(len(masterdict)) +
          " total articles in your Pocket list.\n")
    return masterdict


def del_dupes(masterdict, instance):
    # This dictionary will hold only unique entries
    filtereddict = {}

    # This loop will find the duplicate URLs and delete them from the list
    delete_count = 0
    for k, v in masterdict.items():
        if v not in list(filtereddict.values()):
            filtereddict[k] = v
        else:
            print("Removing duplicate: " + v)
            delete_count += 1
            instance.delete(str(k), wait=False)

    print(str(delete_count) + ' items were deleted.')
    print('There are now ' + str(len(filtereddict)) +
          " unique articles in your Pocket list.")
    return filtereddict


def items_to_manipulate():
    """Gets the list of items to act on."""
    items = input("What are the items? " +
                  "Separate URLs or IDs with a comma," +
                  " or provide the path of a text file with each item " +
                  "on a separate line. ")
    manip = []
    if items[-4:].lower() == '.txt':
        try:
            with open(os.path.normcase(items), "r", encoding='utf-8') as al:
                manip.append(line.rstrip() for line in al)
        except IOError:
            print("That file does not exist.")
            try_again = input("Would you like to try again? (y/n)").lower()
            if try_again == 'n':
                return
            else:
                return [-1]
    else:
        manip = items.split(',')
    return manip


def sort_items(dict_of_articles, input_options):
    direction = ""
    key_list = {'name': 'resolved_title',
                'date': 'time_added',
                'length': 'word_count',
                'url': 'resolved_url'}
    while not direction:
        direction = input("How would you like to sort the articles "
                          "([F]orward/[B]ackward)? )".lower())
        if direction == 'b':
            return sorted([dict_of_articles[item] for item in dict_of_articles],
                          key=itemgetter(key_list[input_options]),
                          reverse=True)
        elif direction == 'f':
            return sorted([dict_of_articles[item] for item in dict_of_articles],
                          key=itemgetter(key_list[input_options]))
        else:
            direction = ''
            print("That is not a valid input. Please try again.")


def print_items_info(articles, count, v_url='n'):
    time_art_added = datetime.datetime. \
        fromtimestamp(articles[count]['time_added'])
    if v_url == 'y':
        output_end = f"URL is {articles[count]['resolved_url']}."
    else:
        output_end = ''
    print(f"{articles[count]['resolved_title']}, added {time_art_added}, with "
          f"{articles[count]['word_count']} words. {output_end}")


def exit_strategy():
    print('Goodbye!')
    raise SystemExit


def display_items(articles_in_account):
    art_disp = ''
    v_url = ''
    while not v_url:
        v_url = input("Do you wish to view the URL with the article "
                      "information (y/n, default n)?").lower()
        if v_url == '':
            v_url = 'n'
        if v_url not in ['y', 'n']:
            print('That was not a valid input, please try again.')
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
                for count in range(int(art_disp)):
                    print_items_info(articles_in_account, count, v_url)
            except ValueError:
                art_disp = ''
                print("That is not a valid answer, please try again.")


def add_items(instance):
    """Allows adding items to the list"""
    while True:
        add_list = items_to_manipulate()
        if not add_list:
            break
        elif add_list[0] != -1:
            if len(add_list) == 1:
                instance.add(add_list[0])
            else:
                for item in add_list:
                    if "." in item:
                        instance.add(item)
                    else:
                        print("This is not a valid URL, "
                              "the item will be disregarded.")
            instance.commit()
            break


def delete_items(instance, id_url_dict):
    """Allows removing items from the list"""
    while True:
        delete_list = items_to_manipulate()
        if not delete_list:
            break
        elif delete_list[0] != -1:
            for item in delete_list:
                if "." in item:
                    try:
                        instance.delete([aid for aid, u
                                         in id_url_dict.items()
                                         if u == item])
                    except KeyError:
                        print(str(item) +
                              " was not found in the list. "
                              "Nothing related to this item will be modified.")
                else:
                    instance.delete(item)
            instance.commit()
            break


def view_items(art_dict):
    """Allows the user to view information about their list items."""
    sort_order = input("What would you like to sort by "
                       "(Name/Date/Length/URL)? ").lower()
    sorted_names = sort_items(art_dict, sort_order)
    display_items(sorted_names)


def tags_editing(instance, full_list):
    """Allows editing of the tags."""
    print()
    list_tags = input('Would you like to list all the tags? (y/n) ')
    if list_tags.lower() == 'y':
        list_art_tags = []
        for item in full_list:
            try:
                article_tags = full_list[item]['tags'].keys()
                for t in list(article_tags):
                    list_art_tags.append(t)
            except KeyError:
                pass

        print(sorted(set(list_art_tags)))

    edit_tags = input('Do you wish to remove all tags? (y/n) ')
    if edit_tags == 'y':
        for item in full_list:
            instance.tags_clear(full_list[item]['item_id'])
    instance.commit()
    print("Done!")


def main():
    pocket_authenticate()
    pocket_instance = pocket_authenticate()
    items_list = pocket_instance.get(count=15000, detailType='complete')
    full_list = items_list[0]['list']

    url_test(full_list)

    # Clean and parse data
    master_article_dictionary = clean_db(full_list)

    # Option to check for and delete duplicates
    check_dupes = input('Would you like to check for and delete any duplicate articles [y]es/[n]o? ')
    if check_dupes.lower() == 'y':
        master_article_dictionary = (master_article_dictionary, pocket_instance)

    while True:
        choice = input("What would you like to do "
                       "([A]dd/[D]elete/[V]iew/[T]ags/[E]xit)? ").lower()
        if choice == "exit":
            exit_strategy()
        elif choice == 'a':
            add_items(pocket_instance)
        elif choice == 'd':
            delete_items(pocket_instance, master_article_dictionary)
        elif choice == 'v':
            view_items(master_article_dictionary)
        elif choice == 't':
            tags_editing(pocket_instance, master_article_dictionary)


if __name__ == '__main__':
    main()
