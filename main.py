import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
import re
import time
import json
from alive_progress import alive_bar


def get_headers():

    return Headers(browser='chrome', os='win').generate()


def get_parametres(num):

    return {
        'text': 'python',
        'area': [1, 2],
        'page': num,
        'hhtmFrom': 'vacancy_search_list',
        'items_on_page': '20'
    }


def get_requests(url, params=None, class_=None, **kwargs):

    while True:
        html = requests.get(url, headers=get_headers(), params=params)
        soup = BeautifulSoup(html.text, features="lxml")
        div = soup.find('div', class_=class_, attrs=kwargs)
        if div:
            return div, soup


def append_list(div, my_dict, item):

    dict_fields = {'company': item.find(attrs={"data-qa": "vacancy-serp__vacancy-employer"}).text,
                   'city': item.find(attrs={"data-qa": "vacancy-serp__vacancy-address"}).text,
                   'salary': div.find(attrs={"data-qa": "vacancy-salary"}).text, 'tittle': item.find('a').text}
    my_dict['fields'] = dict_fields
    my_json.append(my_dict)
    save_json()


def save_json():

    with open('web_parser.json', 'w', encoding='UTF-8') as f:
        json.dump(my_json, f, ensure_ascii=False, indent=2)


def create_bar_and_find_tegs(serp_items):

    with alive_bar(len(serp_items), force_tty=True, dual_line=True) as bar:
        for item in serp_items:
            my_dict = {'link': item.find('a').get('href')}
            bar.text = f'Download {item.find("a").text}, please wait ...'
            div, soup = get_requests(my_dict['link'], class_="vacancy-title")
            description = soup.find(attrs={"class": [
                "vacancy-branded-user-content",
                "vacancy-description"
            ]}).text
            pattern1 = re.search(r'[Dd]jango', description)
            pattern2 = re.search(r'[Ff]lask', description)
            if pattern1 or pattern2:
                append_list(div, my_dict, item)
            bar()


def main():

    url = 'https://spb.hh.ru/search/vacancy'
    end_page = True
    count_page = 0
    while end_page:
        div, soup = get_requests(url, get_parametres(count_page), id="a11y-main-content")
        serp_items = div.find_all(class_="serp-item")
        end_page = soup.find(attrs={"data-qa": "pager-next"})
        if end_page:
            print('Страница: ', count_page + 1)
        else:
            print('Последний лист')
            print('Страница: ', count_page + 1)
            end_page = False

        create_bar_and_find_tegs(serp_items)

        print('-' * 80)
        count_page += 1


if __name__ == '__main__':
    my_json = []
    a = time.perf_counter()
    main()
    b = time.perf_counter()
    print('Время работы:', b - a)
