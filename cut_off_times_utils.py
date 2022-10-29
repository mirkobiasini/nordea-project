# Import external libraries
import datetime


def get_day_key(date: datetime.date) -> str:
    today = datetime.date.today()
    if date == today:
        return 'today'
    tomorrow = today + datetime.timedelta(days=1)
    if date == tomorrow:
        return 'tomorrow'
    return 'after_tomorrow'


def get_min_cut_off_time(cut_off_a: float, cut_off_b: float) -> str:
    min_cut_off_time = min(cut_off_a, cut_off_b)
    if min_cut_off_time == float('-inf'):
        return 'Never possible'
    elif min_cut_off_time == float('inf'):
        return 'Always possible'
    else:
        return f'{min_cut_off_time:02.02f}'
