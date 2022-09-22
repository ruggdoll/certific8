import socket
import ssl
import datetime
import requests
import json
from bs4 import BeautifulSoup

def fetch_domains(domain):
	session = requests.session()
	ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
	headers = {'User-Agent': ua}
	session.headers = headers
	base_url = "https://crt.sh/?q={}&output=json&exclude=expired"
	url = base_url.format(domain)
	req = session.get(url)
	content = req.content.decode('utf-8')
	soup = BeautifulSoup(content, "html.parser")
	data = list_cleanser(json.loads(soup.text))
	return data

def list_cleanser(rawlist):
	mylist=[]
	for item in rawlist:
		if item["common_name"] not in mylist:
			mylist.append(item["common_name"])
	return(mylist)

def ssl_expiry_datetime(hostname):
    ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    context.check_hostname = False

    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # 5 second timeout
    conn.settimeout(5.0)

    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    # Python datetime object
    return datetime.datetime.strptime(ssl_info['notAfter'], ssl_dateformat)

if __name__ == "__main__":

    domain="ssllabs.com"
    domains_url = fetch_domains(domain)
    for value in domains_url:
        now = datetime.datetime.now()
        try:
            expire = ssl_expiry_datetime(value)
            diff = expire - now
            print ("{} Expiration_date: {} Remaining_days: {}".format(value,expire.strftime("%d/%m/%Y"),diff.days))
        except Exception as e:
            print (value,"ERROR :",e)