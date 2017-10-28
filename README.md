# Easy Lyrics Bot
This is an inline mode bot and retrieves lyrics from AZ Lyrics for the given query.

## How it works
This is an inline bot, that means that can be called from any chat by simply typing @EasyLyricsBot.

After @EasyLyricsBot you should write your lyric search, which could contain the artist's name for higher precision. An
inline result will pop up showing the amount of results loaded. By selecting the article result, a message will be sent
with an inline keyboard, where every button is a search result.

After selecting a result, the message will be edited so it no longer shows the inline keyboard and the text will be
the found lyrics.