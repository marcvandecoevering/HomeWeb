# HomeWeb

![HomeWeb](assets/icon.png)

**Your own website on Unraid or Docker.** Serve HTML and PHP with Apache and PHP 8.5, in a separate container for each website.

## Install on Unraid

1. Find **HomeWeb** in **Apps** and select **Install**.
2. Choose a free port and folders for your website and configuration.
3. Open **WebUI**. Replace `index.html` with your website, or add `index.php`; PHP takes priority.

An empty website folder gets a starter page with live Apache, PHP and OPcache versions. Existing files are preserved.

| Setting | Default |
| --- | --- |
| Web port | `8583` → `8080` |
| Website folder | `/mnt/user/appdata/homeweb/www` → `/var/www/html` |
| Configuration folder | `/mnt/user/appdata/homeweb/config` → `/config` |
| PHP memory / upload limit | `256M` / `32M` |
| PUID / PGID | `99` / `100` |

Not listed in Apps yet? Use **Docker → Add Container** with `ghcr.io/marcvandecoevering/homeweb:php8.5`, **bridge** networking and the mappings above. In Advanced View, set **WebUI** to `http://[IP]:[PORT:8080]`.

## Use Docker on Windows or Linux

No Unraid required. Follow the [Docker guide](docs/docker.md) to run HomeWeb locally with Docker Desktop or Docker Engine. No GitHub account is needed.

## More websites

Create another container with its own name, free host port, website folder and configuration folder.

## Good to know

- Supports `.htaccess`, URL rewriting, sessions, uploads, MySQL/MariaDB, PostgreSQL and SQLite connections.
- Add your database separately. Use a reverse proxy for a domain and HTTPS.
- Back up your website, configuration and database before updating.
- Moving from ThuisWeb? Follow the [migration guide](docs/migration.md) before switching to PHP 8.5.

[User guide](docs/guide.md) · [Support](https://github.com/marcvandecoevering/HomeWeb/issues) · [Unraid templates](https://github.com/marcvandecoevering/unraid-templates) · [MIT license](LICENSE)
