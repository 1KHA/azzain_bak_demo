# Database dump — ready-to-restore demo state

`azzain_demo.dump` (5.5 MB, PostgreSQL custom format) is a full snapshot of the
working demo database. Restoring it gives a server the complete state in one
step, instead of running migrations + seeding + image rewriting by hand.

## What's inside

| | |
|---|---|
| products | 8,871 (60 of them demo products with locally-served images) |
| Arabic names (`name_ar`) | 3,040 — includes all 60 demo products |
| collections | 4 (Casual, Formal, Sporty, Trendy) |
| "Made for you" boards | 48 — 24 men / 24 women, **0** empty slots |
| schema version | `alembic_version = 92bbdc75b49e` (includes `collection_items.gender`) |
| demo backup column | `products.image_urls_original` (created by `prepare_demo.py`, not by any migration) |
| users | 3 demo accounts |

Because the dump carries the alembic version, `flask db upgrade` after restoring
is a no-op — the schema is already at head.

> ⚠️ **Contains personal data**: the `users` table holds 3 real phone numbers.
> If this repo is or becomes public, regenerate the dump excluding them:
> `pg_dump ... --exclude-table-data=users --exclude-table-data=otp_value`

## Restore on a server

```bash
docker cp db_dump/azzain_demo.dump azzain-postgres:/tmp/azzain.dump
docker exec azzain-postgres pg_restore -U azzain -d azzain \
  --clean --if-exists --no-owner --no-privileges /tmp/azzain.dump
```

(For a fresh database, drop `--clean --if-exists`.)

## Then repoint the image URLs — required

`products.image_urls` holds **absolute** URLs, and in this dump they point at the
development tunnel `https://sweat-flame-olive.ngrok-free.dev`. Rewrite them to
the server's own address or every board tile will 404:

```sql
UPDATE products
SET image_urls = ARRAY(
      SELECT replace(u, 'https://sweat-flame-olive.ngrok-free.dev',
                        'https://YOUR-SERVER')       -- no trailing slash
      FROM unnest(image_urls) AS u)
WHERE image_urls_original IS NOT NULL;
```

One line from the shell:

```bash
docker exec azzain-postgres psql -U azzain -d azzain -c "UPDATE products SET image_urls = ARRAY(SELECT replace(u,'https://sweat-flame-olive.ngrok-free.dev','https://YOUR-SERVER') FROM unnest(image_urls) AS u) WHERE image_urls_original IS NOT NULL;"
```

Expect `UPDATE 60`. Verify with:

```sql
SELECT split_part(image_urls[1],'/',3) AS host, count(*)
FROM products WHERE image_urls_original IS NOT NULL GROUP BY 1;
```

The equivalent of this whole step is `python prepare_demo.py --base-url <url>`,
which additionally re-checks every source link over the network — the SQL above
is the fast path when the images are already on disk.

## Still needed alongside the dump

The dump is only the database. The server also needs:

1. `static/demo/` — the 175 image files (now committed to the repo).
2. `DEMO_MODE=1` in the server's `.env` (`.env` is not in git).
3. A restart of the API service.

## Regenerating this dump

```bash
docker exec azzain-postgres pg_dump -U azzain -d azzain -Fc \
  --no-owner --no-privileges > db_dump/azzain_demo.dump
```
