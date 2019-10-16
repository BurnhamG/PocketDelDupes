import sqlite3
from sqlite3 import Error


def connect_db():
    try:
        con = sqlite3.connect("articles.db")
    except Error:
        print(Error)
        raise SystemExit
    return con


def create_table(con):
    cursor = con.cursor()
    cursor.execute(
        """
        CREATE TABLE if not exists articles (id integer PRIMARY KEY, item_id integer, resolved_id 
        integer, given_url text, resolved_url text, given_title text, resolved_title text, favorite integer, 
        status integer, time_added integer, time_updated integer, time_read integer, time_favorited integer, 
        excerpt text, is_article integer, is_index integer, has_image integer, has_video integer, word_count integer, 
        lang text, time_to_read integer, top_image_url text, authors text, image text, images text, 
        listen_duration_estimate integer, tags text, authors text, images text, videos text)
        """
    )
    con.commit()
    cursor.close()


def add_to_db(con, arts):
    cursor = con.cursor()
    cursor.executemany(
        "INSERT INTO articles VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        arts,
    )
    cursor.close()


def load_articles():
    cursor = connect_db()
    cursor.execute("""SELECT * FROM articles""")
