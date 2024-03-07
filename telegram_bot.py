from telegram import Bot
import asyncio

class TelegramBot:
    def __init__(self, chat_id, token) -> None:
        self.bot = Bot(token=token)
        self.chat_id = chat_id
    
    def postMessage(self, content: str):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self.bot.send_message(chat_id=self.chat_id, 
                                  text=content,
                                  parse_mode = 'MarkdownV2')
            )