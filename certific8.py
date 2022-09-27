import socket
import ssl
import datetime
import requests
import json
import argparse
from colorama import init,Back,Style

def fetch_domains(domain):
    session = requests.session()
    ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'
    headers = {'User-Agent': ua}
    session.headers = headers
    url = "https://crt.sh/?q="+domain+"&output=json&exclude=expired"
    req = session.get(url)
    data = list_cleanser(json.loads(req.content.decode('utf-8')))
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
    init(autoreset=True)
    print(Back.RED + "Cert expired                 ")
    print(Back.YELLOW + "Expiration in 15 days or less")
    print(Back.BLUE + "Error while checking cert    ")
    print("~-" * 25)

    parser = argparse.ArgumentParser()
    parser.add_argument("domain",help = "Domain name to analyse")
    args = parser.parse_args()

    for subdomains in fetch_domains(args.domain):
        now = datetime.datetime.now()
        try:
            expire = ssl_expiry_datetime(subdomains)
            diff = expire - now
            status_msg = "Domain:{} Expiration_date:{} Remaining_days:{}".format(subdomains,expire.strftime("%d/%m/%Y"),diff.days)
            if diff.days < 15:
                print (Back.YELLOW + status_msg)
            else :
                print (status_msg)

        except Exception as e:
            error_msg = "Domain:{} Error:{}".format(subdomains,e)
            if error_msg.find("certificate has expired") != -1:
                print (Back.RED + error_msg)
            else :
                print (Back.BLUE + error_msg)
