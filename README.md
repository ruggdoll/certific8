# certific8
From a FQDN to certificates expiration dates for all subdomains found in crt.sh

__Usage:__

python3 certific8.py DOMAIN.TLD
==> prints a human readable colored report

python3 certific8.py --CSV DOMAIN.TLD
==> prints a CSV formatted report

#Who are the issuers oneliner:

python certific8.py DOMAIN.TLD | grep Issuer | cut -d";" -f2 | cut -d":" -f2 | sort -u

__News:__


[24/10/2022] : Medium code refactoring, needed for future extensions

[18/10/2022] : Minor code refactoring

[29/09/2022] : Added Issuers support and "clean" output

[27/09/2022] : Added colored output
