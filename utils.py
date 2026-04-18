# utils.py
import datetime

def get_timestamp():
    """Returns current time as a string"""
    return datetime.datetime.now().isoformat()

def clean_text(text):
    """Removes extra spaces and newlines from text"""
    return " ".join(text.split()) 
