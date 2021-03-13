from requests import session
from requests.adapters import HTTPAdapter
import json
from conf import url_trade, headers, exchange_codes, url_reports
from bs4 import BeautifulSoup
import logging


formatter = logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')

logger = logging.getLogger('olb')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('olb.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)


headers=headers()

adapter = HTTPAdapter(pool_maxsize=64, max_retries=3)

session = session()

session.mount(url_trade, adapter)
session.mount(url_reports, adapter)


def get_securities_by_exchange_code():
    result = {}

    for x in exchange_codes:
        url = f"""{url_trade}/GetSecuritiesByExchangeCode?exchangeCode={x}"""

        try:
            r = session.post(url, headers=headers)
        except:
            return result

        result[x] = []

        res = []

        try:
            res = json.loads(r.content)
        except:
            pass

        result[x] = res

    logger.debug(result)

    return result

def get_rates_detail_JSON(ex_code):
    securityCode = ex_code['Code']
    securityName = ex_code['Security']['Name']
    exchangeCode = ex_code['Security']['ExchangeCode']
    decimals = ex_code['Security']['Decimals']

    boardCode = ex_code['Board']['Code']
    marketCode =ex_code['Board']['MarketCode']

    payload = json.dumps([{"securityCode":securityCode, "securityName":securityName, "exchangeCode":exchangeCode, "decimals":decimals, "boardCode":boardCode, "marketCode":marketCode}])

    url = f"""{url_trade}/GetRatesDetailJSON?request={payload}"""

    result = {}

    try:
        r = session.post(url, headers=headers)
    except:
        return result

    try:
        result = json.loads(r.content)
    except:
        pass

    logger.debug(result)

    return result

def get_open_book_detail(ex_code):
    market = ex_code['Board']['ExchangeCode']
    security = f"{ex_code['Security']['DisplayBaseSecurityCode']} ({ex_code['Security']['Code']})"
    security_code = ex_code['Security']['Code']
    decimals = ex_code['Security']['Decimals']
    deep = 20

    payload = f"""Market={market}&SecurityCode={security_code}&Decimals={decimals}&Deep={deep}"""

    url = f"""{url_trade}/GetOpenBookDetail?{payload}"""

    result = []

    try:
        r = session.post(url, headers=headers)
    except:
        return result

    soup = BeautifulSoup(r.content)

    table_rows = soup.find_all("tr")
    for row in table_rows:
        vals = row.text.split()

        if row.attrs['class'][0]=='openbook-buy':
            result.append({'type':'buy', 'price':vals[1], 'count':vals[0]})
        else:
            result.append({'type':'sell', 'price':vals[0], 'count':vals[1]})

    soup = None

    logger.debug(result)

    return result

def create_order():
    url = f"""{url_trade}/Trade/CreateOrder?...."""

def get_packet(account):
    payload = f"""SrcAccount={account['SrcAccount']}&SrcAccount_placeId={account['SrcAccount_placeId']}&AccountKey={account['AccountKey']}"""

    url = f"""{url_trade}/GetPacket?{payload}"""

    result = {}

    try:
        r = session.post(url, headers=headers)
    except:
        return result

    soup = BeautifulSoup(r.text)

    micex_head = []

    micex_head_table = soup.find_all(class_="micex_head")
    if len(micex_head_table)>0:
        micex_head = table_to_list(micex_head_table[0])
        result['micex_head'] = micex_head

    micex_data_table = soup.find_all(class_="micex data-table")
    if len(micex_data_table)>0:
        micex_data_table = table_to_list(micex_data_table[0])
        result['micex_data_table'] = micex_data_table

    account['packet'] = result

    soup = None

    logger.debug(result)

    return result

def pos_detail_report_data(account, period_from='01.01.2001', period_to='01.01.2040'):
    security_code, position = '', 0
    offset_start, offset_end = 82, 114

    payload = f"""PeriodFrom={period_from}&PeriodTo={period_to}&DisplayAccountNumber={account['SrcAccount']}&SecurityCode={security_code}&Position={position}"""

    url = f"""{url_reports}/PosDetailReportData?{payload}"""

    result = []

    try:
        r = session.post(url, headers=headers)
    except:
        return result

    instance_id_start = r.text.find("""reportview_ReportArea_ErrorLabel', 'reportview_CP', '/Telerik.ReportViewer.axd',""")
    if instance_id_start>0:
         instance_id = r.text[instance_id_start+offset_start:instance_id_start+offset_end]

         url = f"""https://lk.olb.ru/Telerik.ReportViewer.axd?instanceID={instance_id}&optype=Export&ExportFormat=CSV"""

         try:
             r = session.get(url, headers=headers)
         except:
             return result

         txt = r.content.decode('utf-8')

         result = get_order_result(txt)

    logger.debug(result)

    return result

def get_order_result(txt):
    result = []

    txt = txt.replace("""textBox32,textBox33,textBox36,textBox37,textBox27,textBox26,textBox28,textBox29,textBox30,textBox31,textBox38,textBox14,textBox1,textBox34,textBox35,textBox43,textBox44,textBox47,textBox56,textBox57,textBox58,textBox59,textBox60,textBox61,textBox62,textBox63,textBox64,textBox2,textBox3,textBox4,textBox5,textBox6,textBox7,textBox8,textBox9,textBox10,textBox11,textBox23,textBox45,textBox12,textBox16,textBox17,textBox18,textBox19,textBox20,textBox21,textBox22,textBox24,textBox25""", '').replace("""Увеличение,Открытие,Уменьшение,Переворот,Закрытие,Отчет по позициям,"Внимание: Комиссия = Ком. Банка за расчет + Ком. Банка за закл. Цена позиции – считается как средневзвешенная цена всех сделок, сформировавших позицию, поэтому данные по финансовым результатам,  отличаются от финансового результата, формирующего налоговую базу, поскольку при определении расходов на приобретение ценных бумаг используется исключительно метод ФИФО, а не метод средневзвешенной цены. Данный отчет не учитывает сделок РЕПО и иных комиссий при расчете реализованного результата. """, '')

    ex_code, ex_position, positions = '', '', []

    lines = txt.splitlines()
    for idx, val in enumerate(lines):
        if len(val)==0:
            continue

        line = lines[idx].split(',')

        line = normalize_string(line)

        if ex_code!=line[5] or ex_position!=line[7]:
            d = {'ex_code':line[5],
                 'ex_name':line[6],
                 'ex_position':line[7],
                 'date_start':line[21],
                 'date_end':line[26],
                 'result':line[24],
                 'commission':line[27],
                 'positions':positions}

            if len(positions)>0:
                result.append(d)

            positions = []
            ex_code = line[5]
            ex_position = line[7]

        p = {'position':line[31],
             'date':line[32],
             'time':line[33],
             'order':line[34],
             'order_type':line[35],
             'price':line[36],
             'count':line[37],
             'volume':line[38],
             'price_position_before':line[39],
             'volume_position_before':line[40],
             'price_sell':line[41],
             'commission':line[42]}

        positions.append(p)

        if idx==len(lines):
            d = {'ex_code':line[5],
                 'ex_name':line[6],
                 'ex_position':line[7],
                 'date_start':line[21],
                 'date_end':line[26],
                 'result':line[24],
                 'commission':line[27],
                 'positions':positions}

            result.append(d)

    return result

def table_to_list(table):
    result = []

    t_head_struct = get_t_head_struct(table)

    t_body_struct = get_t_body_struct(table)
    for vals in t_body_struct:
        if len(t_head_struct)>0:

            if len(t_head_struct)!=len(vals):
                raise 'len(t_head_struct)!=len(vals)'

            item = {}
            for idx, val in enumerate(t_head_struct):
                item[t_head_struct[idx]] = vals[idx]

            result.append(item)

        else:
            result.append(vals)

    return result

def get_t_body_struct(table):
    t_body_struct = []

    t_body = table.findAll('tbody')
    if len(t_body)>0:
        tags_type = ['th', 'td']

        rows = t_body[0].findAll('tr')
        for row in rows:
            vals = []

            row_els = row.findAll()
            for el in row_els:

                tag_type = str(el)[1:3]
                if not tag_type in tags_type:
                    continue

                vals.append(el.text)

            vals = normalize_string(vals)

            t_body_struct.append(vals)

    return t_body_struct

def get_t_head_struct(table):
    t_head_struct = []

    t_head = table.findAll('thead')
    if len(t_head)>0:
        rows = t_head[0].findAll('tr')
        vals = []

        if len(rows)==1:
            rows_root_el = rows[0].findAll('th')
            for row_root_el in rows_root_el:
                vals.append(row_root_el.text)

        elif len(rows)>1:
            rows_root_el = rows[0].findAll('th')
            rows_children_el = rows[1].findAll('th')

            offset = 0

            for row_root_el in rows_root_el:
                if row_root_el.attrs.get('colspan') is None:
                    vals.append(row_root_el.text)

                else:
                    val_root = row_root_el.text

                    col_span = int(row_root_el['colspan'])
                    for i in range(0, col_span):
                        offset_el = rows_children_el[i+offset]
                        vals.append(f'{val_root}_{offset_el.text}')

                    offset = offset+col_span

        vals = normalize_string(vals)
        for idx, val in enumerate(vals):
            if len(val)==0:
                t_head_struct.append(f'____{str(idx)}')
            else:
                t_head_struct.append(val)

    return t_head_struct

def normalize_string(vals):
    result = []

    for v in vals:
        v = v.replace("\xa0", "").replace("\r\n", "").replace("\n", "").replace("                    ", "").replace("                ", "")
        v  = v.strip()

        result.append(v)

    return result

