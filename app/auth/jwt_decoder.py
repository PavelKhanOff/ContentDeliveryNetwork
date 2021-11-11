from typing import Optional

import httpx
import jwt
import orjson
from eduone_cdn.app.settings.config import (
    SECRET,
    MIDDLEWARE_URL_CHECK_SUPER_USER,
    MIDDLEWARE_URL_CHECK_USER,
)
from fastapi import Header, HTTPException


async def decode(token: Optional[str]):
    token = token.split()
    if len(token) != 2:
        return None
    if token[0].lower() != "bearer":
        return None
    token = token[1]
    if token is None:
        return None
    try:
        data = jwt.decode(
            token,
            SECRET,
            audience=["fastapi-users:auth"],
            algorithms=["HS256"],
        )
        user_id = data.get("user_id")
        if user_id is None:
            return None
    except jwt.PyJWTError:
        return None
    return user_id


async def check_is_user(user_id: str, is_superuser=False):
    url = f'{MIDDLEWARE_URL_CHECK_USER}/{user_id}'
    if is_superuser:
        url = f'{MIDDLEWARE_URL_CHECK_SUPER_USER}/{user_id}'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, timeout=8)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return exc
    except Exception as e:
        return e
    return orjson.loads(response.text).get('message')


async def get_superuser(authorization: Optional[str] = Header("")):
    user_id = await decode(authorization)
    if user_id is None:
        raise HTTPException(status_code=403, detail="message Auth Failed")
    checker = await check_is_user(user_id, is_superuser=True)
    if checker != "True":
        raise HTTPException(status_code=403, detail="message Auth Failed")


async def get_user(authorization: Optional[str] = Header("")):
    user_id = await decode(authorization)
    if user_id is None:
        raise HTTPException(status_code=403, detail="message Auth Failed")
    checker = await check_is_user(user_id)
    if checker != "True":
        raise HTTPException(status_code=403, detail="message Auth Failed")
    return user_id
