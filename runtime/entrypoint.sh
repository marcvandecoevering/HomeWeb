#!/bin/sh
set -eu
fail() { echo "HomeWeb: $*" >&2; exit 1; }
[ "$(id -u)" = 0 ] || fail 'initialization requires root; web requests run as PUID/PGID'
# Ignore old generated configuration while validating fresh environment values.
rm -f /usr/local/etc/php/conf.d/zz-homeweb.ini /usr/local/etc/php/conf.d/zzz-custom.ini
php /opt/homeweb/init.php
# Apache's privilege drop also needs a passwd entry for numeric UIDs.
# Without one, unixd can log getpwuid errors while workers retain root.
if ! getent group "$PGID" >/dev/null; then
    groupadd --gid "$PGID" "homeweb-g$PGID"
fi
if ! getent passwd "$PUID" >/dev/null; then
    useradd --no-create-home --no-log-init --key UID_MIN=1 --uid "$PUID" --gid "$PGID" \
        --shell /usr/sbin/nologin "homeweb-u$PUID"
fi
export APACHE_RUN_USER="#$PUID" APACHE_RUN_GROUP="#$PGID"
setpriv --reuid="$PUID" --regid="$PGID" --clear-groups sh -c \
  'test -r /var/www/html && test -x /var/www/html' || fail 'website directory is not readable/accessible by PUID/PGID'
if [ -e /config/php.ini ]; then
    [ -f /config/php.ini ] && [ -r /config/php.ini ] || fail '/config/php.ini is not readable'
    php /opt/homeweb/validate-ini.php
    cp /config/php.ini /usr/local/etc/php/conf.d/zzz-custom.ini
fi
diagnostics=$(mktemp)
if ! php /opt/homeweb/check.php > /tmp/homeweb-php-version 2> "$diagnostics"; then
    cat "$diagnostics" >&2; rm -f "$diagnostics"; fail 'PHP validation failed'
fi
if [ -s "$diagnostics" ]; then cat "$diagnostics" >&2; rm -f "$diagnostics"; fail 'PHP startup warning; check php.ini'; fi
rm -f "$diagnostics"
apache2ctl -t || fail 'invalid Apache configuration'
exec docker-php-entrypoint "$@"
