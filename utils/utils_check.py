import re

def link_check(link: str) -> bool:
    url_pattern = r'(https?://)?(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*\??[/\w\.-=&%]*'
    if re.match(url_pattern, link):
        return True
    else:
        return False