import asyncio
import requests
import jwt
from jwt.algorithms import RSAAlgorithm
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from typing import Dict, Any, Callable
import utility.config as config
from utility.logging import get_logger

auth_logger = get_logger("auth", "auth.log")

# GLOBAL CACHE 
_cached_keys: Dict[str, object] = {}


security = HTTPBearer(auto_error=True)


def fetch_jwks() -> Dict[str, object]:
    response = requests.get(config.JWKS_URL, timeout=5)
    response.raise_for_status()
    auth_logger.debug(f"Fetched JWKS from {config.JWKS_URL}")
    jwks_data = response.json()

    keys = {}
    for jwk in jwks_data.get("keys", []):
        kid = jwk.get("kid")
        if not kid:
            continue
        public_key = RSAAlgorithm.from_jwk(jwk)
        keys[kid] = public_key
    return keys


async def refresh_jwks_periodically():
    global _cached_keys
    while True:
        try:
            auth_logger.info("Refreshing JWKS from backend...")
            _cached_keys = fetch_jwks()
            auth_logger.info(f"JWKS refreshed — {len(_cached_keys)} keys loaded")
        except Exception as e:
            auth_logger.error(f"Failed to refresh JWKS: {e}")
        await asyncio.sleep(config.JWKS_REFRESH_INTERVAL)


def load_jwks():
    global _cached_keys
    if not _cached_keys:
        try:
            auth_logger.debug("JWKS cache empty, fetching once...")
            _cached_keys = fetch_jwks()
        except Exception as e:
            auth_logger.error(f"Could not load JWKS initially: {e}")
    return _cached_keys


def verify_token(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        

        keys = load_jwks()
        key = keys.get(kid) if kid else None

        auth_logger.debug(f"Verifying token with kid={kid}")
        auth_logger.debug(f"Available keys: {list(keys.keys())}")
        auth_logger.debug(f"Using key: {key}")
        
        if not key:
            auth_logger.warning("No matching public key found for token")
            raise HTTPException(status_code=401, detail="No matching public key found for token")
        return jwt.decode(token, key, algorithms=["RS256"])

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# GLOBAL AUTH DEPENDENCY
def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to enforce authentication on all endpoints."""
    return verify_token(credentials)


# LIFESPAN 
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event to start the JWKS refresher task."""
    refresher_task = asyncio.create_task(refresh_jwks_periodically())
    auth_logger.info("Starting JWKS refresher task...")

    yield

    refresher_task.cancel()
    try:
        await refresher_task
    except asyncio.CancelledError:
        pass
