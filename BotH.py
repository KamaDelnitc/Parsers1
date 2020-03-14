import asyncio
import requests
import datetime
from CheckText import TextReader
import re
import os
import json
from livejournal import Livejournal
from DB import DBWork, LiveJournal_Query, Bot_History
from sqlalchemy import desc

import configparser

config = configparser.ConfigParser()
config.read(os.getcwd() + '\\config.ini')
# token = '714164842:AAEtzkdK-6Mf48GZGajbBWSqjCOQjPUM7y4'
proxies = {
    'http': '192.241.245.207:8080' ,
    'https': '217.182.75.229:8888'

}

# url = 'postgresql://{}:{}@{}:5432/{}'.format('youruser' ,
#                                              '13112019' , 'localhost' , 'postgres')
# con = sqlalchemy.create_engine(url , echo=True)
# meta = sqlalchemy.MetaData(bind=con , reflect=True , schema='public')

# parser.get_director(5041006160)
class GetUpdate():
    con=None
    last=None
    bot=None
    new_message=None
    def __init__(self):
        self.con=DBWork()
        self.bot=BotHandler(config['TOKEN']['token'])
    def check_update(self):
        self.last = self.con.get_last_message()[0]
        messages=self.bot.get_updates(offset=10)
        self.new_message=list(filter(lambda x: x['update_id']>self.last, messages))
        if self.new_message.__len__()>0:
            return True
        else:
            return False



class Handler():
    last=None
    bot=None
    text=None
    con=None
    new_message=None
    def __init__(self):
        # config = configparser.ConfigParser()
        # config.read(os.getcwd() + '\\config.ini')
        self.con=DBWork()
        self.text = TextReader()
        self.bot=BotHandler(config['TOKEN']['token'])

    def get_update(self):
        self.bot.get_updates(self.check_update())

    def filter_message(self, last, message):
        # messages=self.bot.get_updates(offset=10)
        new_message=list(filter(lambda x: x['update_id']>last, message))
        # new_message=[i for i in messages if i['update_id']>self.last]
        return new_message


    def check_greeteng(self, message):
        self.text.loadText(message['message']['text'])
        if self.text.readText()==1:
            live = LiveJournal_Query(id_message=message['message']['message_id'],
                                     state=0)
            self.con.Add_history(live)
            ioloop=asyncio.get_event_loop()
            search = Livejournal()
            tasks=[ioloop.create_task(search.find(self.text.search)),
                   ioloop.create_task(self.bot.send_message(message['message']['chat']['id'],
                                  'Начался сбор информации'))]
            wait_task=asyncio.wait(tasks)
            ioloop.run_until_complete(wait_task)
            ioloop.close()
            # search_answer=search.find(self.text.search)
            self.bot.send_message(a['message']['chat']['id'],
                                  'search_answer')

    def add_in_db(self, message):
                mes = Bot_History(message=message['message']['text'].encode('utf8'),
                                  id_chat=message['message']['chat']['id'], offset=message['update_id'],
                                  username=message['message']['chat']['first_name'].encode('utf8'),
                                  message_id=message['message']['message_id'])
                self.con.Add_history(mes)

    def talking(self, result_json):
        for a in result_json:
                self.add_in_db(a)
                self.check_greeteng(a)
                self.bot.send_message(a['message']['chat']['id'],
                            self.text.answer.replace('[username]', a['message']['chat']['first_name']))




class BotHandler:

    def __init__(self , token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self , offset , timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout , 'offset': offset}
        resp = requests.get(self.api_url + method , params )
        result_json = resp.json() [ 'result' ]
        return result_json

    @classmethod
    def check_in_db(cls, update):
        Check(update)

    async def send_message(self , chat_id , text):
        params = {'chat_id': chat_id , 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method , params)
        return resp

    def send_document(self , chat_id , file_inn):
        file = os.listdir('D:\\Data\\send\\')
        files_name = ''
        for item in file:
            if re.search(file_inn , item):
                files_name = item
                break
        if files_name == '':
            return -1
        method = 'sendDocument'
        files = open('D:\\Data\\send\\' + files_name , 'rb')

        resp = requests.post(self.api_url + method , data={'chat_id': chat_id} , files={'document': files} ,
                             proxies=proxies)
        return resp

    def send_keyboard(self , chat_id , text):
        reply_markup = {'keyboard': [ [ 'Скачать файл' ] , [ 'Пропустить' ] ] , 'resize_keyboard': True ,
                        'one_time_keyboard': True}
        reply_markup = json.dumps(reply_markup)

        params = {'chat_id': chat_id , 'text': text , 'reply_markup': reply_markup ,
                  'disable_web_page_preview': 'true' , }
        method = 'sendMessage'
        resp = requests.post(self.api_url + method , params )
        return resp




    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result [ -1 ]
        else:
            last_update = get_result [ len(get_result) ]

        return last_update


# greet_bot = BotHandler(token)
# now = datetime.datetime.now()


# def insert_send_message(text , info_message):
#     currency = meta.tables [ 'public.send_message' ]
#     inn = get_only_inn(info_message [ 'last_chat_text' ])
#     insert_data = dict(
#         id_message=info_message [ 'id_message' ] ,
#         message=text ,
#         dttm=datetime.datetime.now() ,
#         inn=int(inn) ,
#         id_chat=info_message [ 'last_chat_id' ]
#     )
#     cursor = currency.insert(insert_data)
#     con.execute(cursor)


# def get_last_inn(chat_id):
#     currency_inn = meta.tables [ 'public.send_message' ]
#     currency_id = meta.tables [ 'public.bot_data' ]
#     id_message = currency_inn.select().with_only_columns([ currency_inn.c.inn ]).where(
#         currency_inn.c.id_chat == chat_id).order_by(desc(currency_inn.c.dttm))
#     id_message = con.execute(id_message)
#     for item in id_message:
#         id_message = item
#         break
#     # select_db=currency_id.select().with_only_columns([currency_id.c.message]).where(currency_id.c.id_message==id_message[0])
#     # select_db=con.execute(select_db)
#     # for item in select_db:
#     #     inn_text=item
#     #     break
#     return id_message [ 0 ]

# def return_info_director(director):
#     result='Должность - {}. Фамилия И.О: {} {} {}'.format(director['position'],director['surnames'],director['name'],director['second_name'])
#     return result
#
# def get_only_inn(text):
#     temp = re.search('\d{10}' , text)
#     return temp.group(0)
#
# def return_info_founders(text):
#     result=''
#     for item in text:
#         result+='Фамилия И.О. - {} {} {}\n'.format(item['surnames'],item['name'],item['second_name'])
#     return result


def main():

    config = configparser.ConfigParser()
    config.read(os.getcwd() + '\\config.ini' , encoding='utf-8')


import time
check_last=GetUpdate()
# while True:
if (check_last.check_update()):
        try:
            handler=Handler()
            t=handler.filter_message(check_last.last, check_last.new_message)
            a=handler.talking(t)
            time.sleep(10)
        except Exception as e:
            print(e)

    # time.sleep(10)