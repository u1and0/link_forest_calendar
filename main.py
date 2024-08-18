"""リンクフォレストの予約ページを15分ごとにfetchして、予約可能日をLINEに通知する"""
from time import sleep
from room import fetch_and_parse, parse_rooms, get_available_rooms
from line import line_post, format_message


def main():
    url = "https://rsv.ihonex.com/cgi-bin/ihonex3/plan_cal.cgi?hid=linkforest&form=jp&roomcd=05&search_ninzu=0&search_adult=2&plancd=PS4"
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

    message = format_message(url, available_date)
    response = line_post(message)
    print(response.status_code)


if __name__ == '__main__':
    main()
