"""LINEへの投稿関連モジュール"""
import os
import calendar
from datetime import datetime
import requests

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


def is_message_updated(message: str, path: str) -> bool:
    """ pathというファイルに保存されたmessageと比較して
    messageが新しければ、messageをpathというファイルに保存してTrueを返す。
    messageが古ければ、Falseを返す。
    副作用として、pathに指定したファイルへのIOが発生する。

    main.is_message_updated()より一般化した
    """
    try:
        # ファイルが存在しない場合
        if not os.path.exists(path):
            try:
                # ディレクトリが存在しない場合は作成
                os.makedirs(os.path.dirname(path), exist_ok=True)

                # 新規ファイルに書き込み
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(message)
                return True, ""
            except Exception as e:
                raise IOError(f"ファイル作成中にエラーが発生しました: {e}")
        # ファイルが存在する場合、内容を読み込む
        with open(path, 'r', encoding='utf-8') as f:
            old_message = f.read()
        # メッセージが異なる場合
        if message != old_message:
            # ファイルを更新
            with open(path, 'w', encoding='utf-8') as f:
                f.write(message)
            return True, ""
        # メッセージが同じ場合
        return False
    except PermissionError:
        raise PermissionError(f"ファイル {path} にアクセス権限がありません。")
    except IOError as e:
        raise IOError(f"ファイル操作中にIOエラーが発生しました: {e}")
    except Exception as e:
        raise Exception(f"予期せぬエラーが発生しました: {e}")


def extract_year_month_tuple(
        days_list: list[datetime]) -> set[tuple[int, int]]:
    """days_listの(年,月)タプルの重複を削除して返す"""
    return {(int(day.strftime("%Y")), int(day.strftime("%m")))
            for day in days_list}


def format_message(url: str, dates: list[datetime]) -> str:
    """lineのPOSTするメッセージをフォーマットする"""
    msg = f"""LinkForest の予約ページ から予約可能日一覧を表示します。
{url}
    """
    year_month_set = extract_year_month_tuple(dates)
    for year_month_tuple in year_month_set:
        msg += "\n" + print_calendar(
            year_month_tuple[0],
            year_month_tuple[1],
            dates,
        )
    return msg


def circle_day(year: int, month: int, day: int, days: list[datetime]):
    """days の中にdayが含まれていたら日付を(  )で囲む"""
    if datetime(year, month, day) in days:
        return f"({day:2})"
    return f" {day:2} "


def print_calendar(year: int, month: int, days: list[datetime]) -> str:
    """テキストカレンダー表記の文字列を返す"""
    header = " ".join(f"{w.rjust(2)}" for w in JAPANESE_WEEKDAYS)
    calendar_str = [f"{year}年{month}月", header]
    # daysに指定した日付をカッコ付きで表示
    non_date_str = "  - "
    for week in calendar.monthcalendar(year, month):
        circle_week = [
            circle_day(year, month, day, days) if day != 0 else non_date_str
            for day in week
        ]
        # 1行を文字列に結合
        calendar_str.append("".join(circle_week))
    # 全行を改行で結合
    return "\n".join(calendar_str)


if __name__ == "__main__":
    days = [
        datetime(2024, 8, 1),
        datetime(2024, 8, 10),
        datetime(2024, 8, 21),
    ]
    cal0 = print_calendar(2024, 8, days)
    # cal1 = print_calendar(2024, 9)
    # cal2 = print_calendar(2024, 10)
    # cal = "\n\n".join([cal0, cal1, cal2])
    print(cal0)
    status = line_post(cal0)
    print(status)

# 2024年8月
#  月  火  水  木  金  土  日
#   -   -   - ( 1)  2   3   4
#   5   6   7   8   9 (10) 11
#  12  13  14  15  16  17  18
#  19  20 (21) 22  23  24  25
#  26  27  28  29  30  31   -
# 通知を送信しました！
# <Response [200]>
