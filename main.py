"""リンクフォレストの予約ページを15分ごとにfetchして、予約可能日をLINEに通知する
Usage
python main.py PS4
python main.py PG2
"""
# import sys
from time import sleep
from datetime import datetime

from room import fetch_and_parse, parse_rooms, get_available_rooms, build_url
from line import line_post, print_calendar


def extract_year_month_tuple(
        days_list: list[datetime]) -> set[tuple[int, int]]:
    """days_listの(年,月)タプルの重複を削除して返す"""
    return {(int(day.strftime("%Y")), int(day.strftime("%m")))
            for day in days_list}


def main(plancd: str):
    url = build_url(plancd=plancd)
    calendar_class = "c-calendar-sel"
    soup = fetch_and_parse(url, calendar_class)
    rooms = parse_rooms(soup)
    # 結果を表示
    # for entry in rooms:
    #     print(entry)

    availables = get_available_rooms(rooms)
    for item in availables:
        print(item)

    available_date = [room.date for room in availables]
    # print(available_date)

    year_month_set = extract_year_month_tuple(available_date)
    for year_month_tuple in year_month_set:
        message = print_calendar(
            year_month_tuple[0],
            year_month_tuple[1],
            available_date,
        )
        print(message)
        # LINEへ送信
        response = line_post(message)
        print(response.status_code)


if __name__ == '__main__':
    main("PS4")
    # plancd = sys.argv[-1]
    # while True:
    # main("PS4")
    # main("PG2")
    #     sleep(900)
