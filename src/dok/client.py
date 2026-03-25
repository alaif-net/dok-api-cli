from __future__ import annotations

from typing import Any, Optional

import httpx

from dok.config import Config
from dok.exceptions import ApiError, AuthError, NotFoundError


class DokClient:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = httpx.Client(
            base_url=config.base_url,
            auth=(config.access_token, config.access_token_secret),
            timeout=30.0,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "DokClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code == 401:
            raise AuthError("認証エラー: アクセストークンを確認してください。")
        if response.status_code == 403:
            raise AuthError(f"権限エラー: {response.text}")
        if response.status_code == 404:
            raise NotFoundError("リソースが見つかりません。")
        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise ApiError(response.status_code, f"APIエラー ({response.status_code}): {detail}")

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        response = self._client.get(path, params=params)
        self._raise_for_status(response)
        if response.status_code == 204:
            return None
        return response.json()

    def post(self, path: str, json: Optional[dict[str, Any]] = None, params: Optional[dict[str, Any]] = None) -> Any:
        response = self._client.post(path, json=json, params=params)
        self._raise_for_status(response)
        if response.status_code == 204:
            return None
        return response.json()

    def put(self, path: str, json: Optional[dict[str, Any]] = None) -> Any:
        response = self._client.put(path, json=json)
        self._raise_for_status(response)
        return response.json()

    def delete(self, path: str) -> None:
        response = self._client.delete(path)
        self._raise_for_status(response)

    def get_stream_info(self, task_id: str, container_index: int) -> dict[str, str]:
        return self.post(f"/tasks/{task_id}/containers/{container_index}/stream/")
