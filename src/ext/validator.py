import re

def is_valid_url(url:str) -> bool:
    if not url:
        return False

    if len(url) > 2048:  # Reasonable URL length limit
        return False
    
    # More secure regex pattern without nested quantifiers
    regex = r'^https?://(?:www\.)?[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,6}(?:/[^\s]*)?$'
    
    try:
        return re.match(regex, url, re.IGNORECASE) is not None
    
    except re.error:
        return False