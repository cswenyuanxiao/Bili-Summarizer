
"""
Bilibili WBI Signature Helper
"""
import hashlib
import urllib.parse
import time

# WBI Mixin Key Encoding Table
CHECK_TABLE = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 57, 54, 36, 48, 14, 24, 50, 54, 19, 10, 33, 23, 20, 31, 60, 2
]

def get_mixin_key(orig: str) -> str:
    """Shuffle characters for mixin key"""
    return ''.join([orig[i] for i in CHECK_TABLE])[:32]

def sign_wbi(params: dict, img_key: str, sub_key: str) -> dict:
    """
    Sign parameters with WBI keys
    Returns a new dictionary with signed parameters (including w_rid and wts)
    """
    mixin_key = get_mixin_key(img_key + sub_key)
    curr_time = round(time.time())
    
    # Copy params to avoid modifying original
    signed_params = params.copy()
    signed_params['wts'] = curr_time
    
    # Sort and filter keys
    signed_params = dict(sorted(signed_params.items()))
    
    # Filter out characters "!'()*" in values (not implemented here as usually standard params don't have them)
    # Python's urllib.parse.urlencode handles most encoding, but Bilibili has specific rules.
    # For standard search params (mid, pn, ps, order), standard urlencode is sufficient.
    
    query = urllib.parse.urlencode(signed_params)
    wbi_sign = hashlib.md5((query + mixin_key).encode()).hexdigest()
    
    signed_params['w_rid'] = wbi_sign
    return signed_params

def parse_wbi_keys(nav_data: dict) -> tuple[str, str]:
    """Parse img_key and sub_key from nav endpoint response data"""
    try:
        wbi_img = nav_data['data']['wbi_img']
        img_url = wbi_img['img_url']
        sub_url = wbi_img['sub_url']
        img_key = img_url.rsplit('/', 1)[1].split('.')[0]
        sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
        return img_key, sub_key
    except (KeyError, IndexError, TypeError):
        return "", ""
