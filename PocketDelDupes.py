#!/usr/bin/env python

from pocket import Pocket
# Site here: https://github.com/tapanpandita/pocket
import webbrowser
import sys
import os

# Get consumer key from cmd line
consumer_key = sys.argv[1]

request_token = Pocket.get_request_token(
    consumer_key=consumer_key,
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
    consumer_key=consumer_key,
    code=request_token,
)
print('Got authenticated request token - ' + request_token)

pocket_instance = Pocket(consumer_key, access_token)

# Retrieve list items
items_list = pocket_instance.get(count=15000, detailType='complete')
varQuit = 0
full_list = items_list[0]['list']

for item in full_list:
    try:
        test = full_list[item]['resolved_url']
    except Exception as e:
        bad_list = []
        bad_list.append('https://getpocket.com/a/read/' + item)
        varQuit = 1
if varQuit == 1:
    print('There were some articles with bad URLs.')
    print('The program will save the list of bad items and then exit.')
    print('Please press enter to proceed.')
    input()
    with open('BadItems.txt') as bad:
        bad.write(bad_list)
    print(bad_list)
    sys.exit()


def filterurl(url, char):
    ''' Function to prune off extra URL options '''
    try:
        return url[:url.index(char)]
    except ValueError:
        return url

# This dictionary is a straight copy of the data from Pocket, but
# with only the ID and URL properties.
# It will also strip all of the extra social media info from each URL.
masterdict = {}
list_art_tags = []

for item in full_list:
    article_id = full_list[item]['item_id']
    article_url = full_list[item]['resolved_url']
    word_count = full_list[item]['word_count']
    reverse_lookup = {article_url: article_id}
    try:
        article_tags = full_list[item]['tags'].keys()
    except KeyError:
        article_tags = 'Untagged'

    # Remove extra crap from URLS (DANGEROUS - don't remove too much!)
    article_url = filterurl(article_url, '?utm')
    article_url = filterurl(article_url, '?roi')

    # article_url = filterurl(article_url, '#')

    masterdict[article_id] = article_url
    if article_tags != 'Untagged':
        for t in list(article_tags):
            list_art_tags.append(t)
        print(article_url, word_count, list(article_tags))

print('\n' + str(len(masterdict)) + " total articles in your Pocket list.\n")

# This dictionary will hold only unique entries
filtereddict = {}

# This loop will find the duplicate URLs and delete them from the list
deleteCount = 0
for k, v in masterdict.items():
    if not v in list(filtereddict.values()):
        filtereddict[k] = v
    else:
        print("Removing duplicate: " + v)
        deleteCount += 1
        pocket_instance.delete(str(k), wait=False)

print(str(deleteCount) + ' items were deleted.')
print('There are now ' + str(len(filtereddict)) +
        " unique articles in your Pocket list.")


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


def sort_direction(items):
    direction = input(f"How would you like to sort the {items} (Forward/Backward)? ").lower()
    if direction == 'backward':
        sorted_names = sorted([full_list[item]['resolved_name'] for item in full_list], reverse=True)
    elif direction == 'forward':
        sorted_names = sorted([full_list[item]['resolved_name'] for item in full_list])
    else:
        direction = ''
        print("That is not a valid input. Please try again.")
    return direction


def add_items():
    """Allows adding items to the list"""
    while True:
        add_list = items_to_manipulate()
        if not add_list():
            break
        elif add_list[0] != -1:
            if len(add_list) == 1:
                pocket_instance.add(add_list[0])
            else:
                for item in add_list:
                    if "." in item:
                        pocket_instance.bulk_add(url=item)
                    else:
                        pocket_instance.bulk_add(item)
                break
            pocket_instance.commit()
            break


def delete_items():
    """Allows removing items from the list"""
    while True:
        delete_list = items_to_manipulate()
        if not delete_list():
            break
        elif delete_list[0] != -1:
            for item in delete_list:
                if "." in item:
                    try:
                        pocket_instance.delete(reverse_lookup[item])
                    except KeyError:
                        print(str(item) +
                                " was not found in the list. " +
                                "Nothing related to this item will be modified.")
                else:
                    pocket_instance.delete(item)
            pocket_instance.commit()
            break


def view_items():
    """Allows the user to view information about their list items."""
    direction = ""
    sort_order = input("How would you like to sort the articles (Name/Date/Length)? ").lower()
    if sort_order == 'name':
        while not direction:
            direction = sort_direction('names')

        chunk = input("How many articles would you like to view at a time (Number/All)? ").lower()

        if chunk != 'all':
            for counter in range(int(chunk)):
                print(sorted_names[counter])
        else:
            for item in sorted_names:
                print(item)
    elif sort_order == 'date':
        direction = input("How would you like to sort the dates (OTN/NTO)? ").lower()


def tags_editing():
    """Allows editing of the tags."""
    print()
    list_tags = input('Would you like to list all the tags? (y/n) ')
    if list_tags.lower() == 'y':
        print(sorted(set(list_art_tags)))

    edit_tags = input('Do you wish to remove all tags? (y/n) ')
    if edit_tags == 'y':
        for item in full_list:
            pocket_instance.tags_clear(full_list[item]['item_id'])
    pocket_instance.commit()
    print("Done!")


options = {"add": add_items(),
            "delete": delete_items(),
            "view": view_items(),
            "tags": tags_editing(),
            }

while True:
    choice = input("What would you like to do? (Add/Delete/View/Tags/Exit) ").lower()
    if choice.lower() == "exit":
        break
    else:
        options[choice]
        if not options[choice]:
            break
