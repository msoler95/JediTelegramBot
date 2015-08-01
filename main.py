import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = '26110609:AAEkRyqus_8JSEecx15MPgv1BBsLJtYLC3I'


BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Hello')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bye')
                setEnabled(chat_id, False)
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            elif text.startswith('/hola'):
                if text == '/hola buenas':
                    reply('Buenas que tal')
                elif text == '/hola malas':
                    reply('Buenas que te den')
            elif text.startswith('/question'):
                if text == '/question quien eres':
                    reply('Soy un bot creado por Marc Soler para JEDI Junior Empresa')
                elif text == '/question quien es el presi':
                    reply('El presi de Jedi es Joaquin Campos')
                elif text == '/question quien es el vicepresi':
                    reply('El vicepresi de Jedi es Albert Viñes')
                elif text == '/question quien es el cap de rrhh':
                    reply('El cap de RRHH de Jedi es Marc Soler')
                elif text == '/question quien es el cap de formacio':
                    reply('El cap de Formacio de Jedi es Joan Barroso')
                elif text == '/question quien es el cap de cofi':
                    reply('El cap de CoFi es Marc Soldevilla')
                elif text == '/question quien es el cap de marketing':
                    reply('El actual es Flor y los candidatos futuros son Guillem y Fredy')
                elif text == '/question quien es el cap de projectes':
                    reply('El cap de projectes es Xavi Pe...Marcos')
                elif text == '/question ha enviado fredy candidatura':
                    reply('Tiempo al tiempo')
                elif text == '/question es segarra muy guarra':
                    reply('Si, es un pussy')
                elif text == '/question quien es el de la foto del grupo':
                    reply('Creo que Joan...creo')
                elif text == '/question que es jedi':
                    reply('La mejor junior del mundo')
                elif text == '/question porque no te callas?':
                    reply('Porque los de BMA no me hacen callar')
                elif text == '/question quien ganara la candidatura de marketing':
                    reply('Frediento que estara muy empatado')


            else:
                reply('What command?')

        # CUSTOMIZE FROM HERE


        elif 'Quien es el vicepresi' in text:
            reply('El vicepresi de Jedi es Albert Viñes')

        elif 'Quien es el cap de rrhh' in text:
            reply('El cap de RRHH de Jedi es Marc Soler')

        elif 'Quien es el cap de formacio' in text:
            reply('El cap de Formacio de Jedi es Joan Barroso')

        elif 'Quien es el cap de cofi' in text:
            reply('El cap de CoFi es Marc Soldevilla')

        elif 'Quien es el cap de marketing' in text:
            reply('El actual es Flor y los candidatos futuros son Guillem y Fredy')

        elif 'Quien es el cap de projectes' in text:
            reply('El cap de projectes es Xavi Pe...Marcos')

        #elif 'Dame el logo de Jedi' in text:
            #reply(img="https://www.upc.edu/emprenupc/ca/imatges/logo_jedi.png")
            


        else:
            if getEnabled(chat_id):
                resp1 = json.load(urllib2.urlopen('http://www.simsimi.com/requestChat?lc=en&ft=1.0&req=' + urllib.quote_plus(text.encode('utf-8'))))
                back = resp1.get('res')
                if not back:
                    reply('okay...')
                elif 'Ni idea' in back:
                    reply('Has dicho algo sin sentido')
                else:
                    reply(back)
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
