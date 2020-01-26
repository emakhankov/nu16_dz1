import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import pathlib
import os
import service.VGTRKBase as VGTRKBase

def get_settings():
    parent_dir = pathlib.Path(__file__).parent.absolute()
    settings_path = os.path.join(parent_dir, 'settings.json')
    tmp_dir = os.path.join(parent_dir, 'tmp')
    with open(settings_path, "r") as read_file:
        data = json.load(read_file)
        data['OUTPUT_EXCEL'] = os.path.join(tmp_dir, 'output.xlsx')
        return data


settings = get_settings()
domain_url = settings['DOMAIN_URL']
parse_url = settings['PARSE_URL']
output_excel = settings['OUTPUT_EXCEL']


def create_dataframe(data):

    df = pd.DataFrame(data, columns=['num', 'href', 'customer', 'description', 'price', 'start', 'finish', 'state'])
    df[['start', 'finish']] = df[['start', 'finish']].apply(pd.to_datetime)
    df[['price']] = df[['price']].apply(pd.to_numeric)
    return df


def get_data_page(url):

    print('gathering from:', url)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    div_id_content = soup.find('div', id='content')
    if div_id_content is None:
        print('The structure of html is broken. Missing tag <div>, id="content"')
        raise SystemExit

    div_pager = div_id_content.find('div', class_='pager')
    next_exists = False
    for a_href in div_pager.find_all('a'):
        if 'след' in a_href.text.lower():
            next_exists = True

    if next_exists:

        table_zebra = div_id_content.find('table', class_='table zebra')
        if table_zebra is None:
            print('The structure of html is broken. Missing tag <table class="table zebra">')
            raise SystemExit

        table_body = table_zebra.find('tbody')
        if table_body is None:
            print('The structure of html is broken. Missing tag <body>')
            raise SystemExit

        for tr_table_body in table_body.find_all('tr'):
            row_dict = {}
            td_table_body = tr_table_body.find_all('td')
            row_dict['num'] = td_table_body[0].a.text
            row_dict['href'] = td_table_body[0].a.get('href')

            row_dict['description'] = td_table_body[1].a.text

            row_dict['customer'] = td_table_body[2].text

            row_dict['price'] = td_table_body[3].text.replace(',', '.').replace(' ', '')

            row_dict['start'] = td_table_body[4].text

            row_dict['finish'] = td_table_body[5].text

            row_dict['state'] = td_table_body[6].text

            result = VGTRKBase.update_row(row_dict)

            if not result:
                return False
        return True

    else:

        return False


def get_data():

    i = 0
    while True:
        i += 1
        return_value = get_data_page(f'{domain_url}{parse_url}/page/{i}')
        if not return_value:
            break
    VGTRKBase.set_hour()


def verify_up_to_date():

    if VGTRKBase.verify_hour():
        get_data()


def get_by_nomer(num):

    verify_up_to_date()
    rows = VGTRKBase.get_rows(num, '')
    return rows


def get_by_description(description):

    verify_up_to_date()
    rows = VGTRKBase.get_rows('', description)
    return rows


def get_excel():

    verify_up_to_date()
    rows = VGTRKBase.get_rows('', '')
    df = create_dataframe(rows)
    df.to_excel(output_excel, engine='xlsxwriter')
