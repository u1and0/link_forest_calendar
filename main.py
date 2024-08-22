"""リンクフォレストの予約ページを15分ごとにfetchして、予約可能日をLINEに通知する
Usage
python main.py PS4
python main.py PG2
"""
import os
from room import fetch_and_parse, parse_rooms, get_available_rooms, build_url
from line import line_post, format_message


def is_message_updated(plancd: str, calendar: str) -> bool:
    """
    前回のメッセージと比較し、更新があればTrueを返す

    Args:
        plancd (str): プランコード
        calendar (str): 整形後のメッセージ

    Returns:
        bool: カレンダーが更新されたていたらTrue
    """
    path = f"old_message_{plancd}.txt"

    if not os.path.isfile(path):
        with open(path, "w") as f:
            f.write("")
        return True

    with open(path, "r") as f:
        old_calendar = f.read()

    if old_calendar != calendar:
        # 新しいカレンダーになると
        # ファイルに書き込んでTrueを返す
        with open(path, "w") as f:
            f.write(calendar)
        return True
    else:
        return False


def get_available_dates(url: str) -> list:
    """
    空室状況ページから空室日のリストを取得する

    Args:
        url (str): 空室状況ページのURL

    Returns:
        list: 空室日のリスト
    """
    calendar_class = "c-calendar-sel"
    soup = fetch_and_parse(url, calendar_class)
    rooms = parse_rooms(soup)
    availables = get_available_rooms(rooms)
    return [room.date for room in availables]


def main(plancd: str):
    """
    指定されたプランコードの空室状況を取得し、
    前回取得時と比較して変更があればLINEに通知する
    plancd (str): プランコード
    """
    url = build_url(plancd=plancd)
    available_date = get_available_dates(url)
    calendar = format_message(url, available_date)
    print(calendar)

    if is_message_updated(plancd, calendar):
        response = line_post(calendar)
        print(response.status_code)
    else:
        print("メッセージは送信されませんでした")


if __name__ == '__main__':
    main("PS4")
    main("PG2")
