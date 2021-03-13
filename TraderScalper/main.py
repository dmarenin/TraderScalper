import target
import message
from olb import get_securities_by_exchange_code, get_open_book_detail, get_packet, pos_detail_report_data

from conf import accounts


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
    for acc in accounts:
        report = pos_detail_report_data(acc)


if __name__ == "__main__":
    main()

