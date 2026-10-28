# HomeWeb with Docker

Run HomeWeb without Unraid on Windows with Docker Desktop, or on Linux with Docker Engine and Compose. The image supports `linux/amd64` (Intel/AMD x86-64); native ARM images are not provided.

## Windows: three steps

### 1. Install Docker Desktop

Follow the [official Windows instructions](https://docs.docker.com/desktop/setup/install/windows-install/), start Docker Desktop and select **Linux containers** (normally using WSL 2). Open a new PowerShell window.

### 2. Create a folder and download Compose

Use a new, empty folder. Git and a GitHub account are not required.

```powershell
New-Item -ItemType Directory -Path "$HOME\HomeWeb"
Set-Location "$HOME\HomeWeb"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/marcvandecoevering/HomeWeb/main/compose.yaml" -OutFile compose.yaml
New-Item -ItemType Directory -Path www, config
```

### 3. Start HomeWeb

```powershell
docker compose up -d
```

Open **[http://localhost:8080](http://localhost:8080)**. The first download may take a few minutes. The starter page shows the running component versions.

## Add your website

Open `HomeWeb\www` in File Explorer. Add your HTML, CSS, JavaScript and PHP files. Replace `index.html` or add `index.php`, which takes priority. Refresh your browser to see changes. Databases run separately.

The `config` folder stores settings. An optional `config/php.ini` takes effect after `docker compose restart`. The starter page is only created in a completely empty website folder; existing files are preserved.

## Stop and update

Run these commands from the folder containing `compose.yaml`.

| Action | Command |
| --- | --- |
| Check status | `docker compose ps` |
| Read logs | `docker compose logs --tail=100 homeweb` |
| Stop | `docker compose stop` |
| Start | `docker compose up -d` |
| Remove the container | `docker compose down` |

These commands preserve `www` and `config`. Back up both folders and any database before updating:

```powershell
docker compose pull
docker compose up -d
```

Updates preserve your website and any existing starter page. Docker Desktop must remain running to serve the website.

## Another port or multiple websites

If port 8080 is in use, create `.env` beside `compose.yaml`:

```dotenv
HOMEWEB_PORT=8082
```

Run `docker compose up -d` again and open `http://localhost:8082`.

For another website, create a separate folder such as `HomeWeb-second`, with its own `compose.yaml`, `www`, `config` and a different port in `.env`. Use different folder names: Compose derives the project name from the folder.

The example binds only to your PC (`127.0.0.1`). To allow access from your home network, change the port mapping to `"${HOMEWEB_PORT:-8080}:8080"` and configure your firewall as needed. Set up a domain and HTTPS separately through a reverse proxy.

## Linux

Install Docker Engine and the Compose plugin. Download [compose.yaml](../compose.yaml) into a project folder and create `www` and `config`. Run `id -u` and `id -g`, then set your non-root IDs in `.env`:

```dotenv
PUID=1000
PGID=1000
```

Replace the example IDs with your own. Existing website files must be readable by this user; upload folders also need write permission. Run `docker compose up -d` and open `http://localhost:8080`.

## Troubleshooting

- **Docker command not found:** open a new PowerShell window after installation.
- **Cannot connect to Docker:** start Docker Desktop and wait for the engine.
- **Windows containers selected:** switch to Linux containers.
- **Port already in use:** choose another port as above.
- **Website folder inaccessible:** check file sharing and folder permissions. Prefer a local folder outside OneDrive or a network drive.

See the [user guide](guide.md) for settings, permissions and backups, or the [migration guide](migration.md) for an existing ThuisWeb installation.
