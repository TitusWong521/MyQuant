import hmac
import hashlib
import json, requests

def getSign(data,secret):
    result = hmac.new(secret.encode("utf-8"), data.encode("utf-8"), hashlib.md5).hexdigest()
    return result

def doApiRequest(url, cmds):
    s_cmds = json.dumps(cmds)
    r = requests.post(url, data={'cmds': s_cmds})
    # print(r.text)
    return r.text

def doApiRequestWithApikey(url, cmds, api_key, api_secret):
    s_cmds = json.dumps(cmds)
    sign = getSign(s_cmds,api_secret)
    r = requests.post(url, data={'cmds': s_cmds, 'apikey': api_key,'sign':sign})
    # print(r.text)
    return r.text