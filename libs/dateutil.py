from datetime import datetime

def parse_date(val, format):
    try:
        return datetime.strptime(val, format)
    except Exception:
        return ValueError(f"Invalid datetime value: {val} ({format})")
