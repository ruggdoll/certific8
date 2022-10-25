import datetime
import json
import socket
import ssl

import requests
from colorama import Back, Style, init

class Certific8:
    def __init__(self, domain):
        self.domain=domain
        self.fqdn_list={}
        self.set_fqdn_list()
        for fqdn in self.fqdn_list:
            self.set_certificate_info(fqdn)
    
    def set_fqdn_list(self):
        session = requests.session()
        ua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0)"
        " Gecko/20100101"
        " Firefox/40.1"
        headers = {'User-Agent': ua}
        session.headers = headers
        url = "https://crt.sh/?q={}&output=json&exclude=expired".format(
            self.domain
            )
        req = session.get(url)
        rawlist = json.loads(req.content.decode('utf-8'))
        for item in rawlist:
            if item['common_name'] not in self.fqdn_list:
                self.fqdn_list[item['common_name']]=""

    def get_ssl_info(self,fqdn):
        context = ssl.create_default_context()
        context.check_hostname = False
        conn = context.wrap_socket(
                   socket.socket(socket.AF_INET),
                   server_hostname=fqdn,
                )
        conn.settimeout(5.0)
        conn.connect((fqdn, 443))
        return conn.getpeercert(binary_form=False)

    def set_certificate_info(self,fqdn):
        ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'
        now = datetime.datetime.now()
        try:
            my_ssl_info = self.get_ssl_info(fqdn)
#            print(my_ssl_info['subjectAltName'])
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
            self.fqdn_list[fqdn]={
                'Issuer':issuer,
                'Not_After':expire.strftime("%d/%m/%Y"),
                'Remaining':diff.days,
                'Error':''
                }

        except Exception as e:
            if str(e).find("Certificate has expired") != -1:
                self.fqdn_list[fqdn]={
                'Issuer':issuer,
                'Not_After':'',
                'Remaining':'0',
                'Error':"Certificate has expired",
                }
            else :
                self.fqdn_list[fqdn]={
                'Issuer':'',
                'Not_After':'',
                'Remaining':'',  
                'Error':str(e),
                }

    def console_print_certificate_info(self):
        init(autoreset=True)
        print(Back.RED + "Cert expired                 ")
        print(Back.YELLOW + "Expiration in 15 days or less")
        print(Back.BLUE + "Error while checking cert    ")
        print("~-" * 25)
        for fqdn in self.fqdn_list:
            if(self.fqdn_list[fqdn]['Error'] == ''):
                status_msg=str(
                    "FQDN:"+fqdn+";"\
                    "Issuer:"+self.fqdn_list[fqdn]['Issuer']+";"\
                    "Expires_on:"+self.fqdn_list[fqdn]['Not_After']+";"\
                    "DayCount:"+str(self.fqdn_list[fqdn]['Remaining'])+";"\
                )
                if(self.fqdn_list[fqdn]['Remaining']<15):
                    print(Back.YELLOW + status_msg)
                else:
                    print(status_msg)   
            else:
                if(self.fqdn_list[fqdn]['Error'] == "Certificate has expired"):
                    status_msg=str(
                        "FQDN:"+fqdn+";"\
                        "Issuer:"+self.fqdn_list[fqdn]['Issuer']+";"\
                        "Expires_on:;"\
                        "Error:"+self.fqdn_list[fqdn]['Error']+";"
                        )
                    print(Back.RED + status_msg)
                else:
                    status_msg=str(
                        "FQDN:"+fqdn+";"\
                        "Issuer:;"\
                        "Expires_on:;"\
                        "Error:"+self.fqdn_list[fqdn]['Error']+";"
                        )
                    print(Back.BLUE + status_msg)

    def CSV_print_certificate_info(self):
        print("FQDN;ISSUER;EXPIRES_ON,DAYCOUNT;ERROR")
        for fqdn in self.fqdn_list:
            if(self.fqdn_list[fqdn]['Error'] == ''):
                status_msg=str(
                    fqdn+";"\
                    +self.fqdn_list[fqdn]['Issuer']+";"\
                    +self.fqdn_list[fqdn]['Not_After']+";"\
                    +str(self.fqdn_list[fqdn]['Remaining'])+";;"
                )
            else:
                if(self.fqdn_list[fqdn]['Error'] == "Certificate has expired"):
                    status_msg=str(
                        fqdn+";"\
                        +self.fqdn_list[fqdn]['Issuer']+";;;"\
                        +self.fqdn_list[fqdn]['Error']+";"
                    )
                else:
                    status_msg=str(
                        fqdn+";;;;"\
                        "Error:"+self.fqdn_list[fqdn]['Error']+";"
                        )
            print(status_msg)