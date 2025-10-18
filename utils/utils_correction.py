def link_correction(link: str) -> str:
    if not 'https://' in link:
        if 'http://' in link:
            link = link.replace('http://', 'https://', 1)
        else:
            link = 'https://' + link
    return link