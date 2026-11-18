#Owner::ANIKET::ANHOTRA = MR.Panda
"""Idempotently create the private S3 development bucket after server readiness."""

from __future__ import annotations

import time

from botocore.exceptions import BotoCoreError, ClientError

from backend.app.services.storage_service import (
    get_storage_client,
    load_storage_config,
)


def ensure_private_bucket(max_attempts: int = 20) -> None:
    """Create a development bucket only after the S3-compatible server responds.

    This command does not grant public access or modify existing objects.
    """
    configuration = load_storage_config()
    client = get_storage_client()
    for attempt in range(max_attempts):
        try:
            try:
                client.head_bucket(Bucket=configuration.bucket)
            except ClientError as error:
                status = error.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
                if status != 404:
                    raise
                client.create_bucket(Bucket=configuration.bucket)
            print("PASS private evidence bucket is available")
            return
        except (ClientError, BotoCoreError) as error:
            if attempt == max_attempts - 1:
                raise RuntimeError("Private evidence bucket could not be initialised") from error
            time.sleep(2)
    raise RuntimeError("Private evidence bucket unavailable")


if __name__ == "__main__":
    ensure_private_bucket()
