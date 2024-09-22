from datetime import datetime

def parse_date(val, format):
    """Parse string representing date or datetime into a datetime object""" 
    try:
        return datetime.strptime(val, format)
    except Exception:
        return ValueError(f"Invalid datetime value: {val} ({format})")
