"""Load runtime secrets from HashiCorp Vault (KV v2) into environment variables.

Only activates when VAULT_ADDR and VAULT_TOKEN are set (e.g. in prod/staging).
Falls back silently to whatever is already in the environment (local dev / CI)
if Vault is unreachable or credentials are missing, so `manage.py` never hard-fails.
"""
import logging
import os

logger = logging.getLogger(__name__)


def load_secrets_from_vault():
    addr = os.environ.get('VAULT_ADDR')
    token = os.environ.get('VAULT_TOKEN')
    if not addr or not token:
        return

    mount_point = os.environ.get('VAULT_KV_MOUNT', 'kv')
    secret_path = os.environ.get('VAULT_SECRET_PATH', 'media-drishti/config')

    try:
        import hvac

        client = hvac.Client(url=addr, token=token)
        if not client.is_authenticated():
            logger.warning('Vault token rejected; using existing environment variables.')
            return

        response = client.secrets.kv.v2.read_secret_version(
            path=secret_path, mount_point=mount_point
        )
        secrets = response['data']['data']
        for key, value in secrets.items():
            # Don't override an explicitly-set local env var.
            os.environ.setdefault(key, str(value))
    except Exception:
        logger.warning('Could not load secrets from Vault; using existing environment variables.', exc_info=True)
