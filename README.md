# SubLink Forge

Open-source subscription usage dashboard and API starter for self-hosting.

**Status:** starter release. The UI is a static demo and the API parses usage metadata supplied by the caller. It does not yet fetch subscription URLs or connect to PasarGuard, Marzban, or other panels.

## Features
- Persian/English UI toggle
- FastAPI parser for the `Subscription-Userinfo` header
- Traffic warning at or above 80%
- Docker support
- Free to download and self-host

 Project structure
```text
sublink-forge/
├── index.html
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── apps/api/
    ├── main.py
    └── requirements.txt
```

## Run locally
Requires Python 3.10+.

```bash
cd apps/api
python -m venv .venv
```

Activate the environment (`source .venv/bin/activate` on Linux/macOS or `.venv\Scripts\Activate.ps1` on Windows PowerShell), then:

```bash
pip install -r requirements.txt
uvicorn main:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/health` or `http://127.0.0.1:8000/docs`.

## Test parser
POST JSON to `/v1/usage/parse`:

```json
{
  "subscription_userinfo": "upload=1048576; download=838860800; total=1073741824"
}
```

Example:
```bash
curl -X POST http://127.0.0.1:8000/v1/usage/parse \
  -H "Content-Type: application/json" \
  -d '{"subscription_userinfo":"upload=1048576; download=838860800; total=1073741824"}'
```

## Docker
From the repository root run `docker compose up --build`. API: `http://127.0.0.1:8000`.

## GitHub Pages
GitHub Pages can host the static `index.html`: repository **Settings → Pages → Deploy from a branch → main → /(root)**. GitHub Pages does not execute Python; users must run the API on their own machine/server or another hosting provider. The current demo UI does not call a deployed API.

## Security
- Never commit credentials, tokens, `.env` files, or private subscription URLs.
- Do not expose a self-hosted API publicly without authentication and rate limiting.
- A future URL-fetching feature must protect against SSRF, private IP access, redirects, timeouts, and oversized responses.
- Use only subscription links and systems you are authorized to access.

## Panel adapters
Panel-specific adapters are not implemented in this starter release. Implement each adapter separately after verifying the panel's supported API, authentication, response schema, and terms. The current release intentionally does not fetch arbitrary user-provided URLs.

## License
MIT. See `LICENSE`.
