"""Bounded server entry point for local and reviewed hosted deployment."""
import os

import uvicorn

from admin.auth import Settings


def main():
    settings = Settings.from_env()  # Fail before listening if hosted settings are incomplete.
    port = int(os.getenv('PORT', '8080' if settings.hosted else '4180'))
    if not 1 <= port <= 65535:
        raise ValueError('PORT must be between 1 and 65535.')
    uvicorn.run('admin.app:create_app', factory=True,
                host='0.0.0.0' if settings.hosted else '127.0.0.1', port=port,
                access_log=False, proxy_headers=False, limit_concurrency=16,
                timeout_keep_alive=5)


if __name__ == '__main__':
    main()
