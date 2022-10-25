from lib_certific8 import Certific8
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("domain",help = "Domain name to analyse")
    parser.add_argument("--CSV", help="format output to CSV",action="store_true")
    args = parser.parse_args()

    mycerthandler = Certific8(args.domain)
    if args.CSV:
        mycerthandler.CSV_print_certificate_info()
    else:
        mycerthandler.console_print_certificate_info()