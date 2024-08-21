"""リンクフォレストの予約ページを15分ごとにfetchして、予約可能日をLINEに通知する
Usage
python main.py PS4
python main.py PG2
"""
import os
from room import fetch_and_parse, parse_rooms, get_available_rooms, build_url
from line import line_post, format_message


def main(plancd: str):
    url = build_url(plancd=plancd)
    calendar_class = "c-calendar-sel"
    soup = fetch_and_parse(url, calendar_class)
    rooms = parse_rooms(soup)
    # 結果を表示
    # for entry in rooms:
    #     print(entry)

    availables = get_available_rooms(rooms)
    # for item in availables:
    #     print(item)

    available_date = [room.date for room in availables]
    # print(available_date)

    message = format_message(url, available_date)
    print(message)

    # 過去のメッセージと比較
    path = f"old_message_{plancd}.txt"
    # ファイルパスがなければ作成する
    if not os.path.isfile(path):
        with open(path, "a"):
            pass
        os.chmod(path, 0o666)

    # 前回のカレンダーと異なっていたら
    # old_message.txtを書き換える
    with open(path, "w+") as f:
        old_message = f.read()
        # LINEに送信する
        if old_message != message:
            f.write(message)
            # LINEへ送信
            response = line_post(message)
            print(response.status_code)


if __name__ == '__main__':
    main("PS4")
    main("PG2")
