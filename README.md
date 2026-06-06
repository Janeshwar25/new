import os
import logging
import time
from typing import Any, Dict, List, Optional

import requests
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


class TokenCache:
    """Thread-safe token caching with automatic expiry refresh."""

    def __init__(self):
        self._token: Optional[str] = None
        self._expires_at: float = 0
        self._buffer_seconds: int = 300

    def get(self) -> Optional[str]:
        if self._token and time.time() < (
            self._expires_at - self._buffer_seconds
        ):
            return self._token
        return None

    def set(self, token: str, expires_in: int) -> None:
        self._token = token
        self._expires_at = time.time() + expires_in

    def clear(self) -> None:
        self._token = None
        self._expires_at = 0


class EnterpriseLLMClient:

    def __init__(self, config: Any):

        self.config = config

        self.client_id = getattr(
            config,
            "LLM_GATEWAY_CLIENT_ID",
            ""
        )

        self.client_secret = getattr(
            config,
            "LLM_GATEWAY_CLIENT_SECRET",
            ""
        )

        self.project_id = getattr(
            config,
            "LLM_GATEWAY_PROJECT_ID",
            ""
        )

        self.token_url = getattr(
            config,
            "LLM_GATEWAY_TOKEN_URL",
            ""
        )

        self.scope = getattr(
            config,
            "LLM_GATEWAY_SCOPE",
            "api"
        )

        self.base_url = getattr(
            config,
            "LLM_GATEWAY_BASE_URL",
            ""
        )

        self.model_name = getattr(
            config,
            "LLM_GATEWAY_MODEL_NAME",
            "enterprise-llm"
        )

        self.request_timeout = int(
            getattr(config, "REQUEST_TIMEOUT", "180")
        )

        self.verify_ssl = getattr(
            config,
            "VERIFY_SSL",
            False
        )

        self.max_retries = 3
        self.retry_delay = 1

        self._token_cache = TokenCache()

        logger.info("🔒 ENTERPRISE LLM CLIENT INITIALIZED")
        logger.info("Gateway URL: %s", self.base_url)

    def _get_access_token(self) -> str:

        cached = self._token_cache.get()

        if cached:
            return cached

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }

        headers = {
            "Content-Type":
            "application/x-www-form-urlencoded"
        }

        response = requests.post(
            self.token_url,
            data=payload,
            headers=headers,
            timeout=self.request_timeout,
            verify=self.verify_ssl,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Token request failed: "
                f"{response.status_code} - "
                f"{response.text}"
            )

        data = response.json()

        token = data.get("access_token")

        if not token:
            raise RuntimeError(
                "No access token returned"
            )

        expires_in = data.get("expires_in", 3600)

        self._token_cache.set(
            token,
            expires_in
        )

        return token

    def _build_inference_payload(
        self,
        prompt: str
    ) -> Dict[str, Any]:

        return {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 2048,
        }

    def _messages_to_prompt(
        self,
        messages: List[BaseMessage]
    ) -> str:

        parts: List[str] = []

        for msg in messages:

            msg_type = (
                getattr(msg, "type", None)
                or msg.__class__.__name__
            )

            content = getattr(msg, "content", "")

            if not content:
                continue

            if msg_type.lower().startswith("system"):
                parts.append(
                    f"SYSTEM:\n{content}"
                )

            elif msg_type.lower().startswith("human"):
                parts.append(
                    f"USER:\n{content}"
                )

            elif msg_type.lower().startswith("ai"):
                parts.append(
                    f"ASSISTANT:\n{content}"
                )

            else:
                parts.append(str(content))

        return "\n\n".join(parts).strip()

    def _send_request(self, prompt: str) -> str:

        token = self._get_access_token()

        payload = self._build_inference_payload(
            prompt
        )

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",

            "X-Project-ID": self.project_id,
            "x-project-id": self.project_id,
            "project-id": self.project_id,

            "X-Client-ID": self.client_id,
            "x-client-id": self.client_id,
            "client-id": self.client_id,
        }

        safe_headers = {}

        for k, v in headers.items():

            if (
                "auth" in k.lower()
                or "token" in k.lower()
            ):
                safe_headers[k] = "***MASKED***"

            else:
                safe_headers[k] = v

        print("\n===== ENTERPRISE REQUEST =====")
        print("URL:", self.base_url)
        print("HEADERS:", safe_headers)
        print("PAYLOAD:", payload)
        print("==============================\n")

        for attempt in range(self.max_retries):

            try:

                response = requests.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=self.request_timeout,
                    verify=self.verify_ssl,
                )

                print("STATUS:", response.status_code)
                print(
                    "RESPONSE:",
                    response.text[:1000]
                )

                if response.status_code == 200:

                    data = response.json()

                    result = (
                        data.get("response")
                        or data.get("text")
                        or data.get("output")
                        or data.get(
                            "choices",
                            [{}]
                        )[0].get(
                            "message",
                            {}
                        ).get(
                            "content"
                        )
                    )

                    if not result:
                        raise RuntimeError(
                            "No response content"
                        )

                    return str(result).strip()

                if response.status_code == 429:

                    delay = (
                        self.retry_delay
                        * (2 ** attempt)
                    )

                    time.sleep(delay)

                    continue

                raise RuntimeError(
                    f"LLM request failed: "
                    f"{response.status_code} - "
                    f"{response.text[:1000]}"
                )

            except requests.exceptions.Timeout:

                if attempt < self.max_retries - 1:

                    delay = (
                        self.retry_delay
                        * (2 ** attempt)
                    )

                    time.sleep(delay)

                    continue

                raise RuntimeError(
                    "Request timeout"
                )

            except requests.exceptions.ConnectionError as e:

                if attempt < self.max_retries - 1:

                    delay = (
                        self.retry_delay
                        * (2 ** attempt)
                    )

                    time.sleep(delay)

                    continue

                raise RuntimeError(
                    f"Connection failed: {str(e)}"
                )

        raise RuntimeError(
            "Enterprise gateway failed"
        )

    def generate_response(
        self,
        prompt: Optional[str] = None,
        messages: Optional[
            List[BaseMessage]
        ] = None,
        context: Optional[str] = None,
    ) -> str:

        MOCK_MODE = os.getenv(
            "ENTERPRISE_MOCK_MODE",
            "false"
        ).lower() == "true"

        if MOCK_MODE:
            return (
                "✅ Enterprise mock "
                "response successful"
            )

        if messages:

            complete_prompt = (
                self._messages_to_prompt(
                    messages
                )
            )

        elif prompt:

            complete_prompt = prompt

        else:

            raise ValueError(
                "Either prompt or "
                "messages required"
            )

        if (
            not complete_prompt
            or not complete_prompt.strip()
        ):
            raise ValueError(
                "Prompt cannot be empty"
            )

        logger.info(
            "🔐 INITIATING ENTERPRISE "
            "LLM INFERENCE"
        )

        result = self._send_request(
            complete_prompt
        )

        logger.info(
            "✅ ENTERPRISE INFERENCE COMPLETE"
        )

        return result

    def is_available(self) -> bool:

        try:

            token = self._get_access_token()

            return bool(token)

        except Exception as e:

            logger.warning(
                "Gateway unavailable: %s",
                str(e)
            )

            return False
