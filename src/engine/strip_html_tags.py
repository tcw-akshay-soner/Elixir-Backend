import re


def strip_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)
