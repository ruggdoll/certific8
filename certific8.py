import socket
import ssl
import datetime
import requests
import json
import argparse
from colorama import init,Back,Style

def fetch_fqdn(domain):
    session = requests.session()
    ua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"
    " Gecko/20100101"
    " Firefox/40.1"
    headers = {'User-Agent': ua}
    session.headers = headers
    url = "https://crt.sh/?q={}&output=json&exclude=expired".format(domain)
    req = session.get(url)
    rawlist = json.loads(req.content.decode('utf-8'))
    mylist=[]
    for item in rawlist:
        if item["common_name"] not in mylist:
            mylist.append(item["common_name"])
    return mylist

def check_certificate(fqdn):
    ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'
    now = datetime.datetime.now()
    try:
        my_ssl_info = get_ssl_info(fqdn)
        expire = datetime.datetime.strptime(
            my_ssl_info['notAfter'],
            ssl_dateformat
            )
        # Not my proudest piece of code
        stop_loop = 0
        for issuer_items in my_ssl_info['issuer']:
            if stop_loop == 1:
                break
            else :
                for value in issuer_items:
                    if value[0] == 'organizationName':
                        issuer = value[1]
                        stop_loop = 1
                        break
        diff = expire - now
        status_msg = ""\
            "FQDN:{};"\
            "Issuer:{};"\
            "Expiration_date:{};"\
            "Remaining_days:{}".format(
                fqdn,
                issuer,
                expire.strftime("%d/%m/%Y"),
                diff.days)
        if diff.days < 15:
            print (Back.YELLOW + status_msg)
        else :
            print (status_msg)

    except Exception as e:
        if str(e).find("certificate has expired") != -1:
            error_msg = ""\
            "FQDN:{};"\
            "Issuer:{};"\
            "Certificate has expired".format(
                fqdn,
                issuer)
            print (Back.RED + error_msg)
        else :
            error_msg = ""\
            "FQDN:{};"\
            "Error:{}".format(fqdn,e)
            print (Back.BLUE + error_msg)

def get_ssl_info(hostname):
    context = ssl.create_default_context()
    context.check_hostname = False
    conn = context.wrap_socket(
               socket.socket(socket.AF_INET),
               server_hostname=hostname,
            )
    conn.settimeout(5.0)
    conn.connect((hostname, 443))
    return conn.getpeercert()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domain",help = "Domain name to analyse")
    args = parser.parse_args()

    init(autoreset=True)
    print(Back.RED + "Cert expired                 ")
    print(Back.YELLOW + "Expiration in 15 days or less")
    print(Back.BLUE + "Error while checking cert    ")
    print("~-" * 25)
    for fqdn in fetch_fqdn(args.domain):
        check_certificate(fqdn)