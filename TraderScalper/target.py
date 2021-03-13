from time import sleep
from olb import get_securities_by_exchange_code, get_rates_detail_JSON
import _thread
import message
import logging


formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')

logger = logging.getLogger('target')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('target.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)

t_loop = 0.250
black_list = []


def listen(ex_code):
    _thread.start_new_thread(_listen, (ex_code,))

def _listen(ex_code):
    last_price = 0

    while True:
        res = get_rates_detail_JSON(ex_code)
        if len(res)>0:
            if len(res['resQuote'])>0:
                if last_price==res['resQuote'][0]['LastPrice']:
                    continue

                last_price = res['resQuote'][0]['LastPrice']

                detail = {'key' : res['resQuote'][0]['Key'],
                          'last_price' : res['resQuote'][0]['LastPrice'],
                          'best_bid' : res['resQuote'][0]['BestBid'],
                          'best_offer' : res['resQuote'][0]['BestOffer'],
                          'price_max' : res['resQuote'][0]['PriceMax'],
                          'price_min' : res['resQuote'][0]['PriceMin'],
                          'trend' : res['resQuote'][0]['Trend']}

                str = f""" key - {detail['key']} 
                      last_price - {detail['last_price']} 
                      best_bid - {detail['best_bid']} 
                      best_offer - {detail['best_offer']} 
                      price_max - {detail['price_max']} 
                      price_min - {detail['price_min']} 
                      trend - {detail['trend']}"""

                logging.debug(str)

                #message.send(str)

        sleep(t_loop)

def do_loop_scan(board):
    today_value_cost = 100000
    percent_difference_cost = 5

    for ex_code in board:
        res = get_rates_detail_JSON(ex_code)
        if len(res)==0:
            continue

        if len(res['resQuote'])==0:
            continue

        ex_code['last_percent_difference'] = round(ex_code['percent_difference'], 4)
        ex_code['percent_difference'] = round(res['resQuote'][0]['PercentDifference'], 4)

        if ex_code['last_percent_difference']==ex_code['percent_difference'] :
            continue

        if res['resQuote'][0]['TodayValue']<today_value_cost:
            continue

        if ex_code['percent_difference']<percent_difference_cost:
            continue

        if ex_code['percent_difference']>res['resQuote'][0]['PercentDifference']:
            continue

        if res['resQuote'][0]['BestBid']==0:
            continue

        detail = {'key' : ex_code['Security']['BaseSecurityCode'],
                  'last_price' : res['resQuote'][0]['LastPrice'],
                  'best_bid' : res['resQuote'][0]['BestBid'],
                  'best_offer' : res['resQuote'][0]['BestOffer'],
                  'price_max' : res['resQuote'][0]['PriceMax'],
                  'price_min' : res['resQuote'][0]['PriceMin'],
                  'trend' : res['resQuote'][0]['Trend'],
                  'percent_difference' : ex_code['percent_difference'],
                  'last_percent_difference' : ex_code['last_percent_difference']}

        str = f"""
        {detail['key']} 
              last_price - {detail['last_price']} 
              
              best_bid - {detail['best_bid']} 
              best_offer - {detail['best_offer']} 
              diff_offer - {round(detail['best_offer'] - detail['best_bid'], 3)}
              
              price_max - {detail['price_max']} 
              price_min - {detail['price_min']} 
              diff_price - {detail['trend']}

              percent_diff - {detail['percent_difference']}
              last_percent_diff - {detail['last_percent_difference']}
              diff_diff - {round(detail['percent_difference'] - detail['last_percent_difference'], 3)}"""

        logging.debug(str)

        message.send(str)

def scan(board):
    boards = []

    for ex_code in board:
        if ex_code['Board']['Code']!='TQBR':
            continue

        if ex_code['Security']['FaceValueCurrency']!='RUB':
            continue

        ex_code['percent_difference'] = 0
        ex_code['last_percent_difference'] = 0

        boards.append(ex_code)

    while True:
        do_loop_scan(boards)
        sleep(0.1)

