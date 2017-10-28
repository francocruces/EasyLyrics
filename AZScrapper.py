"""
Scrapper for AZ Lyrics website (https://www.azlyrics.com/).
Please don't request various lyrics without sleep in between or you'll get blocked.
"""

import sys
import time
import urllib.error
import urllib.request

import requests
import requests.adapters
from bs4 import BeautifulSoup
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, \
    InlineKeyboardMarkup

from Config import MAX_RESULTS, NO_RESULTS_ALERT

__author__ = "Franco Cruces Ayala"


def get_lyrics_as_inline_keyboard(query):
    """
    Return a InlineQueryResultArticle object. The selection sends a message with an inline keyboard, where every button
    is a search result.
    :param query: A query for searching @https://search.azlyrics.com/
    :return: an InlineQueryResultArticle object
    """
    buttons = get_inline_keyboard_buttons(query)
    if len(buttons) > 0:
        return [InlineQueryResultArticle(
            id=query,
            title="Search for " + query,
            description=str(len(buttons)) + " results found",
            input_message_content=InputTextMessageContent(message_text='Results for "' + query + '".\n' + str(
                len(buttons)) + ' results found.\n' + 'Choose a result to load.'),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
        )]
        # TODO: Add a cancel button.
    else:
        return [InlineQueryResultArticle(
            id=0, title="NO RESULTS", input_message_content=InputTextMessageContent(
                message_text=NO_RESULTS_ALERT,
                parse_mode="Markdown")
        )]


def get_search_result(query):
    """
    Search given query at https://search.azlyrics.com/. Return array of songs where each element is a dictionary
    :param query: A query for searching @https://search.azlyrics.com/
    :return: Array with dictionaries
    """
    print("Loading lyrics: " + str(query))
    url = 'https://search.azlyrics.com/search.php?q=' + str(query)
    page = requests.get(url)
    panels = BeautifulSoup(page.content, 'lxml').find_all("div", class_='panel')
    print("Search results loaded: " + str(query))
    result = []
    count = 0
    for i in panels:
        if "Song" in i.div.text:
            for j in i.table.find_all("tr"):
                try:
                    song = j.td.find_all("b")
                    if len(song) == 2:
                        result.append({
                            'title': song[0].get_text(),
                            'artist': song[1].get_text(),
                            'url': j.a.get('href')
                        })
                    count = count + 1
                except urllib.error.HTTPError:
                    print("Page unreachable")
                    sys.exit(1)
                if count > MAX_RESULTS != -1:
                    break
    return result


def get_inline_keyboard_buttons(query):
    """
    Get lyrics from AZLyrics. First search and then generate Articles as a Inline Query Result.
    :param query: A query for searching @https://search.azlyrics.com/
    :return: Array with InlineKeyboardButtons
    """
    buttons = []
    search_results = get_search_result(query)
    for song in search_results:
        title = song['title'] + " by " + song['artist']
        buttons.append([InlineKeyboardButton(
            text=title,
            callback_data=song['url'].replace('https://www.azlyrics.com/lyrics/', ''),
        )])
    return buttons


def get_lyric_body(url):
    """
    Get lyric body from given url.
    :param url: AZ Lyrics' URL
    :return: Lyrics as a string
    """
    time.sleep(2)
    print("Getting lyrics body: " + url)
    page = urllib.request.urlopen(url)
    lyrics = BeautifulSoup(page.read(), 'lxml').html.body.find_all(
        "div", class_="col-xs-12 col-lg-8 text-center")[0].find_all("div")[6].get_text()
    print("Done: " + url)
    return lyrics


def get_lyric_body_from_id(an_id):
    return get_lyric_body('https://www.azlyrics.com/lyrics/' + an_id)


def get_lyric_body_from_query(given_id, query):
    """
    Deprecated. Currently not used.
    """
    print("Loading lyrics: " + query)
    url = 'https://search.azlyrics.com/search.php?q=' + query
    page = requests.get(url)
    panels = BeautifulSoup(page.content, 'lxml').find_all("div", class_='panel')
    print("Search results loaded: " + query)
    count = 1
    for i in panels:
        if "Song" in i.div.text:
            for j in i.table.find_all("tr"):
                if len(j.td.find_all("b")) == 2:
                    if count == int(given_id):
                        return get_lyric_body(j.a.get('href'))

    return "Couldn't fetch lyrics"


def get_lyrics(query):
    """
    Deprecated. Get lyrics from AZLyrics. First search and then generate Articles as a Inline Query Result.
    :param query: A query for searching @https://search.azlyrics.com/
    :return: Array with InlineQueryResultArticle
    """
    result = []
    search_results = get_search_result(query)
    for song in search_results:
        title = song['title'] + " by " + song['artist']
        result.append(InlineQueryResultArticle(
            id=song['url'].replace('https://www.azlyrics.com/lyrics/', ''),
            title=title,
            description="",
            input_message_content=InputTextMessageContent(
                message_text="Won't load too many lyrics at once",  # This method is deprecated
                parse_mode="Markdown"
            )))
    if len(result) == 0:
        result.append(InlineQueryResultArticle(
            id=0, title="NO RESULTS", input_message_content=InputTextMessageContent(
                message_text=NO_RESULTS_ALERT,
                parse_mode="Markdown")
        ))
    return result
