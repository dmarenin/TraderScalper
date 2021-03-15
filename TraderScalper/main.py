import target
import message
from olb import get_securities_by_exchange_code, get_open_book_detail, get_packet, pos_detail_report_data, create_order, get_orders_detail

from conf import accounts
from decimal import Decimal


def init():
    message.init()

    return get_securities_by_exchange_code(), None, None

def main():
    #securities_by_exchange_code, arg2, arg3 = init()

    #set target
    #targets = ["CHEP", "YAKG","VSMO"]
    #targets = ["TATN"]

    #for t in targets:
    #    for e in securities_by_exchange_code:
    #        for ex_code in securities_by_exchange_code[e]:
    #            if ex_code['Board']['Code']=='OPTION':
    #                continue
    #            if ex_code['Board']['Code']=='FUTURE':
    #                continue
    #            if ex_code['Security']['BaseSecurityCode']==t:
    #                #target.listen(ex_code)

    #get open book
    #                while True:
    #                    res = get_open_book_detail(ex_code)
    #                    print(res)

    #scan
    #target.scan(securities_by_exchange_code['MICEX'])

    #packet
    #for acc in accounts:
    #    packet = get_packet(acc)

    #report
    #for acc in accounts:
    #    report = pos_detail_report_data(acc)

    #new order
    #targets = ["KUZB"]
    #ex_target = None
    #for acc in accounts:
    #    for t in targets:
    #        for ex_code in securities_by_exchange_code['MICEX']:
    #            if ex_code['Security']['BaseSecurityCode']==t:
    #                ex_target = ex_code
    #                break

    #    best_price = 0
    #    count = 0
    #    open_book = get_open_book_detail(ex_target)
    #    for idx, val in enumerate(open_book):
    #        if len(val['Покупка'])!=0:
    #            best_price = open_book[idx-1]['Цена']
    #            count = open_book[idx-1]['Продажа']
    #            break

    #    s_volume = 1
    #    c_volume = ex_target['Security']['LotSize']
    #    is_buy_operation = True
    #    is_swap_order = False
    #    #c_volume: 100000
    #    price = best_price
    #    is_market_price = False
    #    total_swap = 0
    #    total = s_volume*Decimal(best_price)

    #    order = {'s_volume':s_volume,
    #             'c_volume':c_volume,
    #             'is_buy_operation':is_buy_operation,
    #             'is_swap_order':is_swap_order,
    #             #'c_volume':c_volume,
    #             'price':price,
    #             'is_market_price':is_market_price,
    #             'total_swap':total_swap,
    #             'total':total}

    #    res = create_order(acc, ex_target, order)

    #    print(res)

    #orders
    for acc in accounts:
        res = get_orders_detail(acc)


if __name__ == "__main__":
    main()

