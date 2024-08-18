import os
import requests
import calendar

JAPANESE_WEEKDAYS = ["月", "火", "水", "木", "金", "土", "日"]
LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"


def line_post(message: str):
    """message に指定した文字列をLINEへ投稿"""
    # LINE Notify のアクセストークンをここに入れる
    token = os.getenv("LINE_NOTIFY_TOKEN")
    if not token:
        raise KeyError("LINE_NOTIFY_TOKEN not found")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"message": message}
    response = requests.post(LINE_NOTIFY_URL, headers=headers, data=data)

    if response.status_code == 200:
        print("通知を送信しました！")
    else:
        print(f"通知の送信に失敗しました。ステータスコード: {response.status_code}")
    return response


def format_message(url: str, dates) -> str:
    """lineのPOSTするメッセージをフォーマットする"""
    msg = f"""LinkForest の予約ページ から予約可能日一覧を表示します。
{url}
    """
    for date in dates:
        index = date.weekday()
        w = JAPANESE_WEEKDAYS[index]
        msg += "\n{}".format(date.strftime(f'%Y年%m月%d日({w})'))
    return msg


def print_calendar(year: int, month: int) -> str:
    header = " " + " ".join(JAPANESE_WEEKDAYS)
    calendar_str = [f"{year}年{month}月", header]

    for week in calendar.monthcalendar(year, month):
        row = [f"{day:3}" if day != 0 else "-".rjust(3) for day in week]
        calendar_str.append("".join(row))
    return "\n".join(calendar_str)


if __name__ == "__main__":
    cal0 = print_calendar(2024, 8)
    cal1 = print_calendar(2024, 9)
    cal2 = print_calendar(2024, 10)
    cal = "\n\n".join([cal0, cal1, cal2])
    print(cal)
    status = line_post(cal)
    print(status)
