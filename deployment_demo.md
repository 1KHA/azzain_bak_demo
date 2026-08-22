# deployment_demo — Deploying the DEMO Build to a Linux Server

Date: 2026-08-22

This guide deploys the **demo mode** (see `DEMO_MODE.md`) to a raw Linux server.
It is a lighter version of `DEPLOYMENT.md` because demo mode needs **much less**:

| Component | Full deployment | Demo deployment |
|-----------|-----------------|-----------------|
| PostgreSQL (Docker) | required | **required** |
| Redis (Docker) | required | required (app config expects it; unused at demo time) |
| Qdrant (Docker) | required + indexing | **NOT needed** (fixed recommendations) |
| LLM (LM Studio/Ollama) | required | **NOT needed** |
| nginx | recommended | **required** (serves the demo images fast) |
| Demo images (`static/demo/`, ~2.2 MB) | — | **required** (transfer with the code) |

Assumes Ubuntu 22.04/24.04, a server IP or domain (`DEMO_HOST` below, e.g.
`demo.yourdomain.com` or `203.0.113.10`).

---

## 1. Server prep (once)

```bash
sudo apt update && sudo apt install -y git curl nginx ufw
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER        # re-login afterwards

# Python 3.13
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.13 python3.13-venv python3.13-dev libpq-dev

sudo ufw allow OpenSSH && sudo ufw allow 'Nginx Full' && sudo ufw enable
```

A small VPS is enough for the demo: **2 vCPU / 4 GB RAM / 20 GB disk**.

## 2. Copy the project (code + demo assets)

```bash
# from your Mac — note static/ and demo_recommendations.json MUST be included
rsync -av --exclude venv --exclude __pycache__ --exclude logs \
  ~/Documents/AzzainCode/original_code/test_orignal_code/flask-backend-development/ \
  user@DEMO_HOST:/opt/azzain/backend/
```

Check on the server: `ls /opt/azzain/backend/static/demo | wc -l` → should be 40.

## 3. PostgreSQL + Redis in Docker

`/opt/azzain/docker-compose.yml`:

```yaml
services:
  postgres:
    image: postgres:15
    container_name: azzain-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: azzain
      POSTGRES_PASSWORD: CHANGE_ME
      POSTGRES_DB: azzain
    ports: ["127.0.0.1:5432:5432"]
    volumes: [azzain-pg-data:/var/lib/postgresql/data]

  redis:
    image: redis:7
    container_name: azzain-redis
    restart: unless-stopped
    ports: ["127.0.0.1:6379:6379"]

volumes:
  azzain-pg-data:
```

```bash
cd /opt/azzain && docker compose up -d
```

No Qdrant service — demo mode never queries it.

## 4. Transfer the demo database

The demo state (rewritten `image_urls`, `image_urls_original` backup column,
24 seeded collection outfits, your test users) lives in the DB, so **dump and
restore it** rather than re-seeding:

```bash
# on the Mac:
docker exec azzain-postgres pg_dump -U azzain -d azzain -Fc > azzain_demo.dump
scp azzain_demo.dump user@DEMO_HOST:/tmp/

# on the server:
docker cp /tmp/azzain_demo.dump azzain-postgres:/tmp/
docker exec azzain-postgres pg_restore -U azzain -d azzain --clean --if-exists /tmp/azzain_demo.dump
```

## 5. Python env + .env

```bash
cd /opt/azzain/backend
python3.13 -m venv venv && source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-minimal.txt gunicorn
```

Edit `/opt/azzain/backend/.env`:

```
SQLALCHEMY_DATABASE_URI=postgresql://azzain:CHANGE_ME@localhost:5432/azzain
REDIS_URL=redis://localhost:6379/0
DEMO_MODE=1
JWT_SECRET_KEY=<python -c "import secrets; print(secrets.token_hex(32))">
QDRANT_CLIENT_URL=http://localhost:6333   # unused in demo, kept for imports
QDRANT_API_KEY=dummy
LMSTUDIO_BASE_URL=http://localhost:1234/v1  # unused in demo
LMSTUDIO_MODEL=qwen/qwen3-coder-30b         # unused in demo
```

Note: even in demo mode the app **imports** sentence-transformers at startup,
so the first launch downloads the small MiniLM model (~90 MB) from Hugging
Face — one-time, needs internet once.

## 6. Point the image URLs at the server (critical)

The demo image URLs currently baked into the DB use the old ngrok domain.
Rewrite them to the server's public URL (the same one the app will call):

```bash
cd /opt/azzain/backend && source venv/bin/activate
python prepare_demo.py --base-url https://DEMO_HOST
```

Images are already on disk, so this only rewrites URLs + reseeds collections —
it finishes in seconds and downloads nothing.

## 7. Run the API with gunicorn (systemd)

`/etc/systemd/system/azzain-demo.service`:

```ini
[Unit]
Description=Azzain Flask API (DEMO)
After=network.target docker.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/azzain/backend
EnvironmentFile=/opt/azzain/backend/.env
ExecStart=/opt/azzain/backend/venv/bin/gunicorn \
  --workers 2 --threads 4 --timeout 60 \
  --bind 127.0.0.1:5005 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

(`--timeout 60` is plenty — no LLM calls in demo mode.)

```bash
sudo chown -R www-data:www-data /opt/azzain/backend
sudo systemctl daemon-reload
sudo systemctl enable --now azzain-demo
```

## 8. nginx: serve images directly, proxy the API

`/etc/nginx/sites-available/azzain-demo`:

```nginx
server {
    listen 80;
    server_name DEMO_HOST;            # domain, or use the IP / default_server

    # demo images straight from disk — fastest possible, bypasses Flask
    location /static/ {
        alias /opt/azzain/backend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:5005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/azzain-demo /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# with a domain, add free HTTPS (recommended — RN on iOS prefers https):
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d DEMO_HOST
```

If you used HTTPS, make sure step 6 used `https://DEMO_HOST` as the base URL.

## 9. Point the app at the server

In the frontend, `native-frontend-project-setup/src/API/index.js` line 5:

```js
const BACKEND_URL = 'https://DEMO_HOST';   // was the ngrok URL
```

Rebuild/reload the RN app. (This replaces ngrok entirely — no tunnel needed.)

## 10. Verify

```bash
curl -s https://DEMO_HOST/product/banners | head -c 120          # API up
curl -s -o /dev/null -w "%{http_code} %{content_type}\n" \
  https://DEMO_HOST/static/demo/$(ls /opt/azzain/backend/static/demo | head -1)/1.jpg
                                                                  # 200 image/jpeg via nginx
# login + demo recommendation (OTP is 1234 in this build):
curl -s -X POST https://DEMO_HOST/auth/send-otp -H 'Content-Type: application/json' -d '{"phone_number":"+966536637215"}'
sudo journalctl -u azzain-demo -f                                 # logs
```

In the app: home screen shows the 4 collections with locally-served outfit
images; demographics recommendation returns instantly (<100 ms) and identically
on every call.

## Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| Images 404 in the app | DB URLs still point at ngrok — re-run step 6 with the right `--base-url`, restart gunicorn |
| Images load but slowly the first time | normal — the phone caches them (FastImage); repeat views are instant |
| App can't connect | frontend `BACKEND_URL` not updated (step 9), or firewall blocks 80/443 |
| 502 from nginx | gunicorn not running — `systemctl status azzain-demo` |
| Recommendations take 30+ s | `DEMO_MODE=1` missing from `.env` (it would try the LLM) — add it and restart |
| Startup slow the very first time | one-time MiniLM model download (~90 MB) from Hugging Face |

## Rollback to full (non-demo) mode on the same server

Follow `DEPLOYMENT.md` steps for Qdrant + the LLM, then:
`DEMO_MODE=0` in `.env`, `python prepare_demo.py --restore`,
`python init_qdrant.py`, restart the service.
