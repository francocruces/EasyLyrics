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
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from Config import MAX_INLINE_RESULTS

__author__ = "Franco Cruces Ayala"


def get_lyrics(query):
    """
    Get lyrics from AZLyrics. First search and then generate Articles as a Inline Query Result.
    :param query: A query for searching @https://search.azlyrics.com/
    :return: Array with InlineQueryResultArticle
    """
    print("Loading lyrics:" + query)
    url = 'https://search.azlyrics.com/search.php?q=' + query
    page = requests.get(url)
    panels = BeautifulSoup(page.content, 'lxml').find_all("div", class_='panel')
    print("Search results loaded: " + query)
    result = []
    count = 1
    for i in panels:
        if "Song" in i.div.text:
            for j in i.table.find_all("tr"):
                try:
                    song = j.td.find_all("b")
                    if len(song) == 2:
                        lurl = j.a.get('href')
                        print(lurl)
                        title = song[0].get_text() + " by " + song[1].get_text()
                        jsong = InlineQueryResultArticle(
                            id=lurl.replace('https://www.azlyrics.com/lyrics/', ''),
                            title=title,
                            description=j.td.small.get_text(),
                            input_message_content=InputTextMessageContent(
                                message_text=get_lyric_body(lurl)
                            ), # url=lurl
                        )
                        count += 1
                        result.append(jsong)
                        print("Result " + str(count) + " loaded " + lurl)
                except urllib.error.HTTPError:
                    print("Page unreachable")
                    sys.exit(1)
                if count > MAX_INLINE_RESULTS:
                    break
    if len(result) == 0:
        result.append(InlineQueryResultArticle(
            id=0, title="NO RESULTS", input_message_content=InputTextMessageContent(
                message_text="No results :c")
        ))
    return result


def get_lyric_body(url):
    """
    Get lyric body from given url.
    :param url: AZ Lyrics' URL
    :return: Lyrics as a string
    """
    time.sleep(2)
    print("Lyrics: " + url)
    page = urllib.request.urlopen(url)
    lyrics = BeautifulSoup(page.read(), 'lxml').html.body.find_all(
        "div", class_="col-xs-12 col-lg-8 text-center")[0].find_all("div")[6].get_text()
    print("Done: " + url)
    return lyrics


def get_lyric_body_from_query(given_id, query):
    """
    Currently not used.
    """
    print("Loading lyrics:" + query)
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
                    count += 1

    return "Couldn't fetch lyrics"
