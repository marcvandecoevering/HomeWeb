ARG BASE_IMAGE
FROM ${BASE_IMAGE}
ARG BASE_IMAGE
ARG SOURCE_REVISION=local
LABEL org.opencontainers.image.title="ThuisWeb" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.revision="${SOURCE_REVISION}" \
      org.opencontainers.image.base.name="${BASE_IMAGE}"
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
      curl util-linux libicu-dev libonig-dev libzip-dev libpq-dev \
      libpng-dev libjpeg62-turbo-dev libfreetype6-dev libxml2-dev \
    && docker-php-ext-configure gd --with-jpeg --with-freetype \
    && docker-php-ext-install -j"$(nproc)" mysqli pdo_mysql pgsql pdo_pgsql \
       intl gd zip opcache \
    && apt-get install -y --no-install-recommends \
       libicu72 libonig5 libzip4 libpq5 libpng16-16 libjpeg62-turbo libfreetype6 libxml2 \
    && apt-get purge -y --auto-remove $PHPIZE_DEPS \
       libicu-dev libonig-dev libzip-dev libpq-dev libpng-dev \
       libjpeg62-turbo-dev libfreetype6-dev libxml2-dev \
    && a2enmod rewrite headers \
    && rm -rf /var/lib/apt/lists/* \
    && cp "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"
COPY runtime/ /opt/thuisweb/
COPY landing/index.html /opt/thuisweb/index.html
COPY security-policy.json /opt/thuisweb/security-policy.json
COPY apache/thuisweb.conf /etc/apache2/sites-available/000-default.conf
RUN printf 'Listen 8080\nListen 127.0.0.1:8081\n' > /etc/apache2/ports.conf \
    && printf 'ServerName localhost\nServerTokens Prod\nServerSignature Off\nTraceEnable Off\n' > /etc/apache2/conf-available/thuisweb.conf \
    && a2enconf thuisweb \
    && chmod 755 /opt/thuisweb/entrypoint.sh \
    && mkdir -p /config /opt/thuisweb/health \
    && printf 'ready\n' > /opt/thuisweb/health/index.html \
    && php /opt/thuisweb/check.php
ENV PUID=99 PGID=100 PHP_MEMORY_LIMIT=256M PHP_UPLOAD_LIMIT=32M TZ=Europe/Amsterdam
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
 CMD curl --fail --silent --max-time 4 http://127.0.0.1:8081/ || exit 1
ENTRYPOINT ["/opt/thuisweb/entrypoint.sh"]
CMD ["apache2-foreground"]
