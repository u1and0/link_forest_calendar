"""リンクフォレストの部屋予約ページの取得関連モジュール"""
import urllib.parse
from datetime import datetime
import subprocess
from enum import Enum
from bs4 import BeautifulSoup


def build_url(**params):
    """fetchするページのURLの作成"""
    base_url = "https://rsv.ihonex.com/cgi-bin/ihonex3/plan_cal.cgi"
    base_params = {
        "hid": "linkforest",
        "form": "jp",
        "roomcd": "05",  # 部屋番号
        " 部屋"
        "search_ninzu": "0",
        "search_adult": "2",
        # "plancd": "PS4",  # プラン
    }
    params.update(base_params)
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"


def fetch_and_parse(url, _class) -> BeautifulSoup:
    """curl | grepでほしいクラスだけ取得してBeautifulSoupで構造化する
    リンクフォレストの予約ページが<p>タグの下層の<div>タグ内にあるため、
    BeautifulSoupでパースできないため。
    """
    # HTTP GETリクエスト
    curl_cmd = ["curl", "-fsSL", url]
    curl_result = subprocess.run(curl_cmd, capture_output=True, text=True)
    # 特定クラスだけフィルタリング
    grep_cmd = ["grep", "-A5", _class]
    grep_result = subprocess.run(grep_cmd,
                                 input=curl_result.stdout,
                                 capture_output=True,
                                 text=True)
    return BeautifulSoup(grep_result.stdout, 'html.parser')


class Status(Enum):
    AVAILABLE = "○"
    UNAVAILABLE = "×"
    LAST_ROOM = "あと1室"
    LAST_TWO_ROOM = "あと2室"
    UNKNOWN = "－"


def _parse_price(price_str):
    # '13,640円' -> 13640.0 のように変換する
    if price_str:
        price_str = price_str.replace('円', '').replace(',', '')
        return float(price_str)
    return None


def _parse_date(date_str):
    # '2024年08月15日(木)' -> datetime(2024, 8, 15) のように変換する
    return datetime.strptime(date_str[:11], "%Y年%m月%d日")


def _parse_status(status_str):
    # '○', '×', 'あと1室', '－' の文字列をStatus Enumに変換する
    for status in Status:
        if status.value == status_str:
            return status
    return Status.UNKNOWN


class Room(object):

    def __init__(self, date, price, status):
        self.date: datetime = _parse_date(date)
        self.price: float = _parse_price(price)
        self.status: Status = _parse_status(status)

    def __str__(self):
        return "{}, {}, {}".format(
            self.date.strftime("%Y-%m-%d"),
            self.price,
            self.status,
        )

    def __repr__(self):
        return self.__str__()

    def is_available(self) -> bool:
        return self.status == Status.AVAILABLE or \
            self.status == Status.LAST_ROOM or \
            self.status == Status.LAST_TWO_ROOM


def parse_rooms(soup: BeautifulSoup) -> list[Room]:
    # div要素を全て取得
    divs = soup.find_all('div', class_='c-calendar-sel')

    # 結果を構造化
    rooms: list[Room] = []
    for div in divs:
        date = div.get('data-c_ymd', 'N/A')
        price = div.get('data-c_price', 'N/A')
        status = div.find('span', class_='c-calendar-sel__status').text.strip()
        room = Room(date, price, status)
        rooms.append(room)
    return rooms


def get_available_rooms(rooms: list[Room]) -> list[Room]:
    return [room for room in rooms if room.is_available()]


if __name__ == '__main__':
    url = "https://rsv.ihonex.com/cgi-bin/ihonex3/plan_cal.cgi?hid=linkforest&form=jp&roomcd=01&search_ninzu=0&search_adult=2&plancd=SA1"
    calendar_class = "c-calendar-sel"
    soup = fetch_and_parse(url, calendar_class)
    rooms = parse_rooms(soup)
    # 結果を表示
    # for entry in rooms:
    #     print(entry)

    availables = get_available_rooms(rooms)
    for item in availables:
        print(item)
