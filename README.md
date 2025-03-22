# Plex Discord

A Python script that connect to your Plex Media Server, fetch recently added movies or TV shows, and post it to Discord.

## Environment variables

Required variables :

- `WEBHOOK_URL` : Discord webhook URL, see https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks
- `PLEX_URL` : your server's IP adresse (eg http://192.168.1.1:32400)
- `PLEX_TOKEN` : your server's token, see https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

## Installation

### Docker

Build Docker image :

```
docker build -t plex-discord .
```

Run it :

```
docker run --env-file .env -v ./last_execution.txt:/app/last_execution.txt plex-discord
```

### Python

Install dependencies :

```
pip install -r requirements.txt
```

Run script :

```
python main.py
```

## Usage

Run it in a cron job with environment variables and a bind-mount on `/app/last_execution.txt` :

```
docker compose run --rm plex-discord
```