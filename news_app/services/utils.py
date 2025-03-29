from datetime import datetime, timezone, timedelta
import logging




logger = logging.getLogger(__name__)

# 日付を日本時間に変換する関数
# 例：2025-03-29T12:00:00Z → 2025/03/29 21:00
def convert_utc_to_jst(utc_str):
    try:
        dt = datetime.strptime(utc_str, "%Y-%m-%dT%H:%M:%SZ")
        dt_japan = dt.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=9)))
        return dt_japan.strftime("%Y/%m/%d %H:%M")
    except Exception:
        return utc_str  # 変換に失敗した場合は元の文字列を返す
    


# 日付または日付＋時刻の文字列を `datetime.date` に変換する。
# 例：
#     - "2025/03/29"  (日経メディカルの形式)
#     - "2025/03/29 12:00" (時事メディカルの形式)　
def parse_date(raw_date):
    if not raw_date:
        return None

    date_formats = ["%Y/%m/%d %H:%M", "%Y/%m/%d"]  # 時刻あり → なし の順に試す

    for fmt in date_formats:
        try:
            return datetime.strptime(raw_date, fmt).date()
        except ValueError:
            continue  # 次のフォーマットで試す

    logger.error(f"日付のパースに失敗しました（入力: '{raw_date}'）")
    return None