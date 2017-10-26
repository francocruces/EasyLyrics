"""
Simple telegram bot
"""

import asyncio

import telepot
from telepot.aio.delegate import per_inline_from_id, create_open, pave_event_space, intercept_callback_query_origin
from telepot.aio.helper import InlineUserHandler, AnswererMixin, InterceptCallbackQueryMixin
from telepot.aio.loop import MessageLoop
from AZScrapper import get_lyrics
from __TOKEN__ import TOKEN

__author__ = "Franco Cruces Ayala"


class InlineHandler(InlineUserHandler, AnswererMixin, InterceptCallbackQueryMixin):
    """
    Handler for the inline bot.
    """
    def __init__(self, *args, **kwargs):
        super(InlineHandler, self).__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        """
        How to handle an inline query.
        :param msg: Telegram message. It's expected to be an inline_query
        :return: Results for the inline query
        """
        def compute_answer():
            """
            Function generating the answer for the handler.
            :return: Lyrics as articles
            """
            print(msg)
            query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
            print(self.id, ':', 'Inline Query:', query_id, from_id, query_string)
            return get_lyrics(query_string)

        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        """
        Console printing for debugging.
        :param msg: Telegram message. It's expected to be a chosen_inline_result
        """
        print(msg)
        print('inline_message_id' in msg)
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        print(from_id, ",", self.id, ':', 'Chosen Inline Result:', result_id, from_id, query_string)
        print("Message sent to " + str(from_id))


### ASYNC MAIN
bot = telepot.aio.DelegatorBot(TOKEN, [intercept_callback_query_origin(
    pave_event_space())(
    per_inline_from_id(), create_open, InlineHandler, timeout=20)
])

loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
