from phidias.Types import *
import threading
import telegram
import configparser

class TIMEOUT(Reactor): pass
class message(Reactor): pass

config = configparser.ConfigParser()
config.read('config.ini')
TELEGRAM_TOKEN = config.get('AGENT', 'TELEGRAM_TOKEN')

class Timer(Sensor):

    def on_start(self, uTimeout):
        evt = threading.Event()
        self.event = evt
        self.timeout = uTimeout()
        self.do_restart = False

    def on_restart(self, uTimeout):
        self.do_restart = True
        self.event.set()


    def on_stop(self):
        self.do_restart = False
        self.event.set()

    def sense(self):
        while True:
            self.event.wait(self.timeout)
            self.event.clear()
            if self.do_restart:
                self.do_restart = False
                continue
            if self.stopped:
                return
            else:
                self.assert_belief(TIMEOUT("ON"))
                return


class Chatbot(Sensor):

    def on_start(self):
        global BOT
        BOT = telegram.Bot(TELEGRAM_TOKEN)

        self.update_id = None
        self.msgs = [ ]

    def sense(self):
        global BOT
        while True:
            if self.msgs == []:
                for m in BOT.get_updates(offset=self.update_id, timeout=10):
                    if self.update_id is None:
                        self.update_id = m.update_id
                    self.update_id = self.update_id + 1
                    if m.message:
                        self.msgs.append(m)
            if self.msgs == []:
                continue
            m = self.msgs[0]
            del self.msgs[0]
            print(m.message.text)
            if m.message.text is None:
                continue

            message_data = m.message.text.lower().split()
            message_data.insert(0, m.message.chat.id)
            print(message_data)

            self.assert_belief(message(m.message.chat.id, m.message.text))


class Reply(Action):

    def execute(self, *args):
        m = []
        sender = args[0]()
        for v in args[1:]:
            m.append(v())
        message = " ".join(m)
        BOT.sendMessage(sender, message)

