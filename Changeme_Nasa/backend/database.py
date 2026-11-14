import os
import re
import ssl
from contextlib import asynccontextmanager

import asyncpg


@asynccontextmanager
async def read_snapshot():
    host, user, password, certificate = (
        os.getenv(f"COMBUSLAB_DB_{key}") for key in ("HOST", "USER", "PASSWORD", "CA")
    )
    if not all((host, user, password, certificate)):
        raise ValueError("Database configuration is incomplete")

    tls = ssl.create_default_context()
    pem = certificate.strip().strip('"\'').replace(r"\r", "").replace(r"\n", "\n")
    blocks = re.findall(r"-----BEGIN CERTIFICATE-----\s*(.*?)\s*-----END CERTIFICATE-----", pem, re.DOTALL)
    if not blocks:
        raise ValueError("Database CA must be a PEM certificate")
    for block in blocks:
        der = re.sub(r"\s+", "", block)
        body = "\n".join(der[index:index + 64] for index in range(0, len(der), 64))
        tls.load_verify_locations(cadata=f"-----BEGIN CERTIFICATE-----\n{body}\n-----END CERTIFICATE-----\n")

    connection = await asyncpg.connect(
        host=host.strip(), user=user.strip(), password=password, database="postgres",
        port=5432, ssl=tls, timeout=6, command_timeout=6, statement_cache_size=0,
    )
    try:
        async with connection.transaction(isolation="repeatable_read", readonly=True):
            await connection.execute("SET LOCAL statement_timeout = '5s'")
            yield connection
    finally:
        await connection.close(timeout=2)
