from datetime import datetime

def filter_shows_past(item):
    # Returns true if start time is less that current time hence the show has past
    return item['start_time'] < datetime.today().strftime("%m/%d/%Y, %H:%M:%S")

def filter_shows_upcoming(item):
    # Returns true if start time is less that current time hence the show has past
    return item['start_time'] >= datetime.today().strftime("%m/%d/%Y, %H:%M:%S")
