import shelve
from telegram.ext import Updater, CommandHandler, Job
from parser import OlxListParser
from parse_times import now
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = ''

link = """
https://www.olx.ua/nedvizhimost/arenda-kvartir/odessa/?search%5Bfilter_float_price%3Afrom%5D=8000&search%5Bfilter_float_price%3Ato%5D=11000&search%5Bfilter_float_number_of_rooms%3Afrom%5D=2&search%5Bfilter_float_number_of_rooms%3Ato%5D=3&page=1
"""

update_each = 10  # Update each 10 minutes


def get_db():
    return shelve.open('db', writeback=True)


def get_until():
    with get_db() as db:
        return db.get('until')


def set_until(dtime):
    with get_db() as db:
        db['until'] = dtime


def store_chat_id(chat_id):
    with get_db() as db:
        if not db.get('chat_ids'):
            db['chat_ids'] = set([chat_id, ])
        else:
            db['chat_ids'].add(chat_id)


def remove_all_chat_ids():
    with get_db() as db:
        if 'chat_ids' in db:
            del db['chat_ids']


def get_all_chat_ids():
    with get_db() as db:
        return db.get('chat_ids', set([]))


def start(bot, update):
    store_chat_id(update.message.chat_id)

    bot.send_message(
        chat_id=update.message.chat_id,
        text="I will update each {} minutes and report with new ads".format(update_each)
    )


def clear_until(bot, update):
    set_until(None)
    bot.send_message(
        chat_id=update.message.chat_id,
        text='Until time was cleaned'
    )


def give_me(bot, update):
    o = OlxListParser(link)
    until = get_until()
    links = o.get_last_ads_link(until)
    links.reverse()

    if not links:
        bot.send_message(
            chat_id='202510933',
            text='Nothing to show',
        )
        return

    for item in links[:2]:
        bot.send_message(
            chat_id='202510933',
            text=item,
        )

    set_until(now())


def give_me_subscribe(bot, job):
    logger.info('Start JOB')
    o = OlxListParser(link)
    until = get_until()
    links = o.get_last_ads_link(until)
    links.reverse()
    logger.info('Found next links {}'.format(', '.join(links)))
    chat_ids = get_all_chat_ids()
    if not chat_ids:
        logger.info('Can\'t find any subscriber')
        return

    for chat_id in chat_ids:
        for item in links:
            bot.send_message(
                chat_id=chat_id,
                text=item,
            )

    set_until(now())


def init_bot():
    job_10_minutes = Job(give_me_subscribe, 10 * 60.0)
    updater = Updater(token=TOKEN)

    dispatcher = updater.dispatcher
    job_queue = updater.job_queue
    start_handler = CommandHandler('start', start)
    clear_until_handler = CommandHandler('clear_until', clear_until)
    give_me_handler = CommandHandler('give_me', give_me)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(clear_until_handler)
    dispatcher.add_handler(give_me_handler)
    job_queue.put(job_10_minutes, next_t=0)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    init_bot()
