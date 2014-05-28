# utils.http

# PYTHON
from urllib import urlencode

def url_with_querystring(path, **kwargs):
    return path + '?' + urlencode(kwargs)
    
def get_tldextract():
    import tldextract
    return tldextract.TLDExtract(suffix_list_url=False)
