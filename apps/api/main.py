
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="SubLink Forge API",
    description="Secure subscription metadata and analytics API",
    version="0.1.0",
)

# Development only. Replace with your deployed frontend origin
# before production. Do not use wildcard origins with credentials.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class UsageMetadata(BaseModel):
    upload_bytes: Optional[int] = None
    download_bytes: Optional[int] = None
    total_bytes: Optional[int] = None
    expire_at: Optional[datetime] = None
    traffic_percent: Optional[float] = None
    time_percent: Optional[float] = None
    warning: bool = False
    status: str = "unknown"


class HeaderInput(BaseModel):
    subscription_userinfo: str = Field(
        min_length=1,
        max_length=2048,
        description="Value of the Subscription-Userinfo header",
    )


def parse_userinfo(value: str) -> UsageMetadata:
    fields = {}

    for item in value.split(";"):
        if "=" not in item:
            continue

        key, raw = item.strip().split("=", 1)
        key = key.strip().lower()
        raw = raw.strip()

        if key in {"upload", "download", "total", "expire"}:
            if not raw.isdigit():
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid numeric value for {key}",
                )
            fields[key] = int(raw)

    upload = fields.get("upload")
    download = fields.get("download")
    total = fields.get("total")
    expire = fields.get("expire")

    expiry = None
    if expire is not None:
        try:
            expiry = datetime.fromtimestamp(expire, tz=timezone.utc)
        except (ValueError, OverflowError, OSError):
            raise HTTPException(
                status_code=422,
                detail="Invalid expiry timestamp",
            )

    used = (
        upload + download
        if upload is not None and download is not None
        else None
    )

    traffic_percent = None
    if used is not None and total is not None and total > 0:
        traffic_percent = min(100.0, used * 100.0 / total)

    time_percent = None
    # Time percentage requires a known subscription start date.
    # Expiry alone is not enough to calculate it accurately.

    warning = (
        (traffic_percent is not None and traffic_percent >= 80)
        or (time_percent is not None and time_percent >= 80)
    )

    return UsageMetadata(
        upload_bytes=upload,
        download_bytes=download,
        total_bytes=total,
        expire_at=expiry,
        traffic_percent=traffic_percent,
        time_percent=time_percent,
        warning=warning,
        status="available" if fields else "unknown",
    )


@app.get("/")
def root():
    return {
        "name": "SubLink Forge API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/v1/usage/parse", response_model=UsageMetadata)
def parse_usage(payload: HeaderInput):
    """Parse supplied metadata only; does not fetch external URLs."""
    return parse_userinfo(payload.subscription_userinfo)


@app.get("/v1/usage/header-example", response_model=UsageMetadata)
def parse_example(
    subscription_userinfo: str = Header(
        ...,
        alias="Subscription-Userinfo",
        max_length=2048,
    ),
):
    return parse_userinfo(subscription_userinfo)
