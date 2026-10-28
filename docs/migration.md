# Move from ThuisWeb to HomeWeb

HomeWeb uses PHP 8.5 and English text. Its image is `ghcr.io/marcvandecoevering/homeweb:php8.5`. The old `ghcr.io/marcvandecoevering/thuisweb:php8.3` tag is not repointed to PHP 8.5. The main release workflow now maintains HomeWeb; the old image does not receive new releases from that workflow.

## Check your website first

Back up website files, configuration (including hidden files), container settings and any database. Record the previous image digest. Test a copy with HomeWeb, separate folders, a free port and a separate test database. Check your application's PHP 8.5 requirements and the official [8.4](https://www.php.net/manual/en/migration84.php) and [8.5](https://www.php.net/manual/en/migration85.php) migration guides.

Remove explicit OPcache loading from custom php.ini files: PHP 8.5 includes OPcache and an old `zend_extension=opcache.so` setting causes a startup warning. Session upload progress is disabled; ordinary uploads remain available.

## Unraid

After testing, stop your old container. Edit its **Repository** to `ghcr.io/marcvandecoevering/homeweb:php8.5`. Keep the existing website/configuration mount paths, port and environment values. You may rename the container to HomeWeb, but do not rename or empty its data folders. In Advanced View set **WebUI** to `http://[IP]:[PORT:8080]` and **Icon URL** to `https://raw.githubusercontent.com/marcvandecoevering/HomeWeb/main/assets/icon.png`.

Apply, then inspect WebUI, logs and your website's important functions. Existing files are preserved. Old initialization markers and untouched starter-page status endpoints are supported.

## Docker Compose

Keep the existing service name and project directory to avoid accidentally creating a second container. Change only its `image` to `ghcr.io/marcvandecoevering/homeweb:php8.5`, retaining mounts, ports and settings, then run:

```shell
docker compose pull
docker compose up -d
```

If adopting the new example later, note that the port variable is now `HOMEWEB_PORT`; the old example used `THUISWEB_PORT`. Do not leave the old service running on the same port.

## Replace the default starter page

Updates never overwrite website files, including the old Dutch starter page. If you still use that page and want the English HomeWeb page, back up `index.html` first. In the container console, run these commands **only when intentionally replacing the default page**:

```shell
cp /opt/homeweb/index.html /var/www/html/index.html
sha256sum /var/www/html/index.html | cut -d ' ' -f 1 > /config/.homeweb-landing.sha256
chmod 644 /config/.homeweb-landing.sha256
```

An existing `index.php` takes priority and disables the version endpoint. Do not remove your own site to make the status panel appear.
