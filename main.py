"""
Simple telegram inline bot with an inline keyboard. Gets lyrics from AZ Lyrics.
"""

import asyncio

import telepot
from telepot.aio.delegate import per_inline_from_id, create_open, pave_event_space, intercept_callback_query_origin
from telepot.aio.helper import InlineUserHandler, AnswererMixin, InterceptCallbackQueryMixin
from telepot.aio.loop import MessageLoop

from AZScrapper import get_lyrics_as_inline_keyboard, get_lyric_body_from_id
from __TOKEN__ import TOKEN

__author__ = "Franco Cruces Ayala"


class InlineHandler(InlineUserHandler, AnswererMixin, InterceptCallbackQueryMixin):
    """
    Handler for the inline bot.
    """

    def __init__(self, *args, **kwargs):
        super(InlineHandler, self).__init__(*args, **kwargs)

    async def on_inline_query(self, msg):
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
            query_string = telepot.glance(msg, flavor='inline_query')
            return get_lyrics_as_inline_keyboard(query_string)

        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        """
        Console printing for debugging.
        :param msg: Telegram message. It's expected to be a chosen_inline_result
        """
        print(msg)
        # TODO: Store for impact measuring

    async def on_callback_query(self, msg):
        print(msg)
        in_id = msg['inline_message_id']
        await self.bot.editMessageText(str(in_id), get_lyric_body_from_id(msg['data']))


### ASYNC MAIN
bot = telepot.aio.DelegatorBot(TOKEN, [intercept_callback_query_origin(
    pave_event_space())(
    per_inline_from_id(), create_open, InlineHandler, timeout=20)
])

loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
