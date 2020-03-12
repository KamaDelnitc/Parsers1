from DB import DBWork
import configparser
import os
config = configparser.ConfigParser()
config.read(os.getcwd() + '\\config.ini'))

class ChecText:
    answer=None
    text=None
    def __init__(self):
        self.answer=''
        self.text=''
        self.con=DBWork()

    def loadText(self, text):
        self.text=text

    def checkNewmessage(self):
        self.last = self.con.get_last_message()[0]
        messages = self.bot.get_updates(offset=10)
        new_message = list(filter(lambda x: x['update_id'] > self.last, messages))
        if new_message.__len__>0:
            return True
        else:
            return False


    def checkMessage(self):
        if (self.text in config['GREETING']['words']):
            self.answer='Здравствуйте, [username]'