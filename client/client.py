import httplib

conn = httplib.HTTPConnection('127.0.0.1', 5000)
conn.connect()
request = conn.putrequest('GET', '/')
headers = {}
headers['Content-Type'] = 'application/json'
headers['User-Agent'] = 'Python-2.7.11;httplib'
headers['Accept'] = '*/*'
for k in headers:
    conn.putheader(k, headers[k])
conn.endheaders()

resp = conn.getresponse()
print resp.status
print resp.reason
print resp.read()

conn.close()
