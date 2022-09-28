# certific8
From a FQDN to certificates expiration dates for all subdomains

__Usage:__

python3 certific8.py DOMAIN.TLD

#Who are the issuers :

python certific8.py DOMAIN.TLD | grep Issuer | cut -d";" -f2 | cut -d":" -f2 | sort -u

__News:__

[27/09/2022] : Added colored output

[29/09/2022] : Added Issuers support and "clean" output
