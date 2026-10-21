#!/bin/sh
set -eu
fail() { echo "ThuisWeb: $*" >&2; exit 1; }
[ "$(id -u)" = 0 ] || fail 'initialisatie vereist root; webverzoeken draaien onder PUID/PGID'
# Ignore old generated configuration while validating fresh environment values.
rm -f /usr/local/etc/php/conf.d/zz-thuisweb.ini /usr/local/etc/php/conf.d/zzz-custom.ini
php /opt/thuisweb/init.php
# Apache's privilege drop also needs a passwd entry for numeric UIDs.
# Without one, unixd can log getpwuid errors while workers retain root.
if ! getent group "$PGID" >/dev/null; then
    groupadd --gid "$PGID" "thuisweb-g$PGID"
fi
if ! getent passwd "$PUID" >/dev/null; then
    useradd --no-create-home --no-log-init --uid "$PUID" --gid "$PGID" \
        --shell /usr/sbin/nologin "thuisweb-u$PUID"
fi
export APACHE_RUN_USER="#$PUID" APACHE_RUN_GROUP="#$PGID"
setpriv --reuid="$PUID" --regid="$PGID" --clear-groups sh -c \
  'test -r /var/www/html && test -x /var/www/html' || fail 'websitemap is niet leesbaar/toegankelijk voor PUID/PGID'
if [ -e /config/php.ini ]; then
    [ -f /config/php.ini ] && [ -r /config/php.ini ] || fail '/config/php.ini is niet leesbaar'
    php /opt/thuisweb/validate-ini.php
    cp /config/php.ini /usr/local/etc/php/conf.d/zzz-custom.ini
fi
diagnostics=$(mktemp)
if ! php /opt/thuisweb/check.php > /tmp/thuisweb-php-version 2> "$diagnostics"; then
    cat "$diagnostics" >&2; rm -f "$diagnostics"; fail 'PHP-controle mislukt'
fi
if [ -s "$diagnostics" ]; then cat "$diagnostics" >&2; rm -f "$diagnostics"; fail 'PHP-startwaarschuwing; controleer php.ini'; fi
rm -f "$diagnostics"
apache2ctl -t || fail 'Apache-configuratie ongeldig'
exec docker-php-entrypoint "$@"
