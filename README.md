# HomeWeb

![HomeWeb](assets/icon.png)

**Your own website on Unraid or Docker.** Serve HTML and PHP with Apache and PHP 8.5, in a separate container for each website.

## Install on Unraid

1. Find **HomeWeb** in **Apps** and select **Install**.
2. The template fills in the settings below. Change the host port or host folders only if needed; use a free port and separate folders for each website.
3. Open **WebUI**. Replace `index.html` with your website, or add `index.php`; PHP takes priority.

An empty website folder gets a starter page with live Apache, PHP and OPcache versions. Existing files are preserved.

**These are separate fields, not text to enter as a combined mapping.** Host values belong to your Unraid server. Container ports, container paths and variable keys must match exactly, including capital letters and leading `/` characters.

| Config Type | Name (display label) | Container Port / Container Path / Key | Host Port / Host Path / Value | Other setting |
| --- | --- | --- | --- | --- |
| Port | Web port | `8080` | `8080` | Connection Type: `TCP` |
| Path | Website files | `/var/www/html` | `/mnt/user/appdata/homeweb/www` | Access Mode: `Read/Write` |
| Path | Configuration | `/config` | `/mnt/user/appdata/homeweb/config` | Access Mode: `Read/Write` |
| Variable | PUID | `PUID` | `99` | Non-root user ID |
| Variable | PGID | `PGID` | `100` | Non-root group ID |
| Variable | PHP memory limit | `PHP_MEMORY_LIMIT` | `256M` | Memory limit |
| Variable | Upload limit | `PHP_UPLOAD_LIMIT` | `32M` | Limit per file |
| Variable | Time zone | `TZ` | `Europe/Amsterdam` | Change to your time zone if needed |

For example, **PHP memory limit** is only the display name: enter `PHP_MEMORY_LIMIT` in **Key** and `256M` in **Value**. For configuration storage, **Container Path** must be `/config`, not `config`. Enter each value without backticks or quotation marks.

### Manual installation when HomeWeb is not listed in Apps

Open **Docker → Add Container** and set:

| Field | Enter |
| --- | --- |
| Name | `HomeWeb` (or another unique container name) |
| Repository | `ghcr.io/marcvandecoevering/homeweb:php8.5` |
| Network Type | `Bridge` |
| Privileged | `Off` |
| WebUI (Advanced View) | `http://[IP]:[PORT:8080]` |

Use **Add another Path, Port, Variable, Label or Device** to add each row from the settings table above as a separate entry. **Name** is a readable label; **Key** is the exact environment variable name. Keep the WebUI placeholders literally as shown; Unraid replaces them with your server address and chosen host port. Select **Apply**, then open **WebUI** from the container menu.

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
