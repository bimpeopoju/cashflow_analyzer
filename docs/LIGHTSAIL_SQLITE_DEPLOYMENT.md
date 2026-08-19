# MarketFlow Lightsail Deployment With SQLite

This guide deploys the Django backend to an Ubuntu Lightsail instance while
keeping SQLite as the production database.

SQLite can work for a small launch or demo, but it is a single-file database.
Only one writer can write at a time, and the database file must be backed up
carefully. When the app has real concurrent users, move to PostgreSQL.

## 1. Prepare The Repo Before Pulling On Lightsail

Run these commands on your local machine:

```bash
cd C:\Users\HP\Desktop\dev\cash-flow-analyzer\cashflow_analyzer
python backend/manage.py test
python backend/manage.py check
git status --short
```

If you want the current SQLite data carried to Lightsail, commit
`backend/db.sqlite3` with the code:

```bash
git add backend/config/settings.py backend/requirements.txt .env.example docs/LIGHTSAIL_SQLITE_DEPLOYMENT.md backend/db.sqlite3
git commit -m "Prepare backend for Lightsail SQLite deployment"
git push
```

Do not commit `.env`; production secrets must be created directly on the
Lightsail instance.

## 2. Create The Lightsail Instance

Use an Ubuntu Lightsail instance. Attach a static IP before final DNS setup.

SSH into the instance:

```bash
ssh ubuntu@YOUR_LIGHTSAIL_STATIC_IP
```

Install system packages:

```bash
sudo apt update
sudo apt install -y git python3-venv python3-pip nginx
```

## 3. Pull The Project From Git

Choose an app directory:

```bash
sudo mkdir -p /srv/marketflow
sudo chown ubuntu:ubuntu /srv/marketflow
cd /srv/marketflow
git clone YOUR_GIT_REPO_URL .
```

Confirm the SQLite database came with the repo:

```bash
ls -lh backend/db.sqlite3
```

If the file is missing, it was not committed or your branch does not contain it.

## 4. Create The Production Environment File

Create `/srv/marketflow/.env`:

```bash
nano /srv/marketflow/.env
```

Use this template, replacing the domain/IP and secret:

```env
DJANGO_SECRET_KEY=REPLACE_WITH_A_LONG_RANDOM_SECRET
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=YOUR_DOMAIN.com,YOUR_LIGHTSAIL_STATIC_IP,localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=https://YOUR_DOMAIN.com
DJANGO_CORS_ALLOWED_ORIGINS=https://YOUR_DOMAIN.com
DJANGO_DATABASE_NAME=/srv/marketflow/backend/db.sqlite3
DJANGO_SQLITE_TIMEOUT_SECONDS=30
DJANGO_STATIC_ROOT=/srv/marketflow/backend/staticfiles

DJANGO_SECURE_SSL_REDIRECT=false
DJANGO_SESSION_COOKIE_SECURE=false
DJANGO_CSRF_COOKIE_SECURE=false
DJANGO_SECURE_HSTS_SECONDS=0
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=false
DJANGO_SECURE_HSTS_PRELOAD=false

JWT_ACCESS_TOKEN_MINUTES=15
JWT_REFRESH_TOKEN_DAYS=7
```

Keep the secure HTTPS flags false until Nginx and TLS are working. Turn them on
after Certbot succeeds.

Generate a secret key on the server:

```bash
python3 - <<'PY'
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
PY
```

Paste the generated value into `DJANGO_SECRET_KEY`.

## 5. Install Backend Dependencies

```bash
cd /srv/marketflow/backend
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
```

`check --deploy` may still warn about HTTPS flags before TLS is configured.

## 6. Protect SQLite Permissions

Gunicorn must be able to read and write the database and its parent directory:

```bash
sudo chown -R ubuntu:www-data /srv/marketflow
sudo chmod 775 /srv/marketflow/backend
sudo chmod 664 /srv/marketflow/backend/db.sqlite3
```

SQLite creates temporary journal/WAL files beside the database, so the
`backend` directory must be writable by the service user.

## 7. Create The Gunicorn Service

Create the service file:

```bash
sudo nano /etc/systemd/system/marketflow.service
```

Paste:

```ini
[Unit]
Description=MarketFlow Django backend
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/srv/marketflow/backend
EnvironmentFile=/srv/marketflow/.env
ExecStart=/srv/marketflow/backend/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 60
Restart=always

[Install]
WantedBy=multi-user.target
```

Start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable marketflow
sudo systemctl start marketflow
sudo systemctl status marketflow
```

Check logs:

```bash
journalctl -u marketflow -n 100 --no-pager
```

## 8. Configure Nginx

Create:

```bash
sudo nano /etc/nginx/sites-available/marketflow
```

Paste this API-only config:

```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com YOUR_LIGHTSAIL_STATIC_IP;

    client_max_body_size 10M;

    location /static/ {
        alias /srv/marketflow/backend/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable it:

```bash
sudo ln -s /etc/nginx/sites-available/marketflow /etc/nginx/sites-enabled/marketflow
sudo nginx -t
sudo systemctl reload nginx
```

Test:

```bash
curl http://YOUR_LIGHTSAIL_STATIC_IP/api/auth/oauth/providers/
```

## 9. Add HTTPS

After DNS points to the Lightsail static IP:

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN.com
```

Then update `/srv/marketflow/.env`:

```env
DJANGO_CSRF_TRUSTED_ORIGINS=https://YOUR_DOMAIN.com
DJANGO_CORS_ALLOWED_ORIGINS=https://YOUR_DOMAIN.com
DJANGO_SECURE_SSL_REDIRECT=true
DJANGO_SESSION_COOKIE_SECURE=true
DJANGO_CSRF_COOKIE_SECURE=true
DJANGO_SECURE_HSTS_SECONDS=31536000
```

Restart:

```bash
sudo systemctl restart marketflow
python /srv/marketflow/backend/manage.py check --deploy
```

## 10. Deploy Future Updates

If you want the database carried from your local machine again, commit
`backend/db.sqlite3` locally and push before pulling on the server.

On the Lightsail instance:

```bash
cd /srv/marketflow
git pull
cd backend
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart marketflow
sudo systemctl status marketflow
```

Important: if real users create data on Lightsail, pulling a newly committed
local `backend/db.sqlite3` can overwrite server data. Before replacing the
server database, back it up:

```bash
cp /srv/marketflow/backend/db.sqlite3 /srv/marketflow/backend/db.sqlite3.backup.$(date +%Y%m%d%H%M%S)
```

## 11. Backup SQLite

Create a backup directory:

```bash
mkdir -p /srv/marketflow/backups
```

Manual backup:

```bash
sqlite3 /srv/marketflow/backend/db.sqlite3 ".backup '/srv/marketflow/backups/db.sqlite3.backup'"
```

Install sqlite tools if needed:

```bash
sudo apt install -y sqlite3
```

For production, schedule a cron backup and periodically copy backups off the
instance.
