import asyncio
import sys
import time
import urllib.error
import urllib.request

import requests
import requests.adapters
import telepot
from bs4 import BeautifulSoup
from telepot.aio.delegate import per_inline_from_id, create_open, pave_event_space, intercept_callback_query_origin
from telepot.aio.helper import InlineUserHandler, AnswererMixin, InterceptCallbackQueryMixin
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent

from __TOKEN__ import TOKEN

MAX_RETRIES = 20
MAX_INLINE_RESULTS = 1


def get_lyrics(query):
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
                            id=count  ## lurl.replace('https://www.azlyrics.com/lyrics/', '')
                            ,
                            title=title,
                            description=j.td.small.get_text(),
                            input_message_content=InputTextMessageContent(
                                message_text=get_lyric_body(lurl)
                            ),
                            # url=lurl
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
    time.sleep(2)
    print("Lyrics: " + url)
    page = urllib.request.urlopen(url)
    lyrics = BeautifulSoup(page.read(), 'lxml').html.body.find_all(
        "div", class_="col-xs-12 col-lg-8 text-center")[0].find_all("div")[6].get_text()
    print("Done: " + url)
    return lyrics


class InlineHandler(InlineUserHandler, AnswererMixin, InterceptCallbackQueryMixin):
    def __init__(self, *args, **kwargs):
        super(InlineHandler, self).__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        def compute_answer():
            print(msg)
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            print(self.id, ':', 'Inline Query:', query_id, from_id, query_string)
            return get_lyrics(query_string)

        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        print(msg)
        print('inline_message_id' in msg)
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print(from_id, ",", self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)
        print("Message sent to " + str(from_id))


def get_lyric_body_from_query(given_id, query):
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


bot = telepot.aio.DelegatorBot(TOKEN, [intercept_callback_query_origin(
    pave_event_space())(
    per_inline_from_id(), create_open, InlineHandler, timeout=20)
])

loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
