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
    data = list_cleanser(
               json.loads(
                   req.content.decode('utf-8')
               )
            )
    return data

def list_cleanser(rawlist):
    mylist=[]
    for item in rawlist:
        if item["common_name"] not in mylist:
            mylist.append(item["common_name"])
    return(mylist)

def get_ssl_info(hostname):
    context = ssl.create_default_context()
    context.check_hostname = False
    conn = context.wrap_socket(
               socket.socket(socket.AF_INET),
               server_hostname=hostname,
            )
    # 5 second timeout
    conn.settimeout(5.0)
    conn.connect((hostname, 443))
    return conn.getpeercert()

if __name__ == "__main__":
    init(autoreset=True)
    print(Back.RED + "Cert expired                 ")
    print(Back.YELLOW + "Expiration in 15 days or less")
    print(Back.BLUE + "Error while checking cert    ")
    print("~-" * 25)

    parser = argparse.ArgumentParser()
    parser.add_argument("domain",help = "Domain name to analyse")
    args = parser.parse_args()
    ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'
    for subdomains in fetch_domains(args.domain):
        now = datetime.datetime.now()
        try:
            my_ssl_info = get_ssl_info(subdomains)
            expire = datetime.datetime.strptime(
                my_ssl_info['notAfter'],
                ssl_dateformat
                )
            issuer = dict((x,y) for x,y in my_ssl_info['issuer'][1])
#            print(issuer['organizationName'])
            diff = expire - now
            status_msg = ""\
                "Domain:{};"\
                "Issuer:{};"\
                "Expiration_date:{};"\
                "Remaining_days:{}".format(
                    subdomains,
                    issuer['organizationName'],
                    expire.strftime("%d/%m/%Y"),
                    diff.days)
            if diff.days < 15:
                print (Back.YELLOW + status_msg)
            else :
                print (status_msg)

        except Exception as e:
            if str(e).find("certificate has expired") != -1:
                error_msg = ""\
                "Domain:{};"\
                "Issuer:{};"\
                "Certificate has expired".format(
                    subdomains,
                    issuer['organizationName'])
                print (Back.RED + error_msg)
            else :
                error_msg = ""\
                "Domain:{};"\
                "Error:{}".format(
                    subdomains,
                    e)
                print (Back.BLUE + error_msg)
