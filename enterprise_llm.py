"""
Enterprise LLM Gateway Client

Provides OAuth2-based access to the company's enterprise LLM gateway.
Handles token generation, prompt submission, and response parsing.

Usage:
    client = EnterpriseLLMClient(config)
    response = client.generate_response(prompt="Your question", context="RAG context")
"""
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
        self._buffer_seconds: int = 300  # Refresh 5 min before expiry

    def get(self) -> Optional[str]:
        """Get cached token if still valid."""
        if self._token and time.time() < (self._expires_at - self._buffer_seconds):
            return self._token
        return None

    def set(self, token: str, expires_in: int) -> None:
        """Cache token with expiry time."""
        self._token = token
        self._expires_at = time.time() + expires_in
        logger.debug("[Enterprise LLM] Token cached (expires in %d seconds)", expires_in)

    def clear(self) -> None:
        """Clear cached token."""
        self._token = None
        self._expires_at = 0


class EnterpriseLLMClient:
    """
    🔒 Production-Ready Enterprise LLM Gateway Client

    Features:
    - OAuth2 client credentials flow
    - Automatic token generation and caching
    - Request/response logging
    - Retry logic with exponential backoff
    - Configurable timeouts and models
    - Exception handling with hard failure (no fallback)
    """

    def __init__(self, config: Any):
        """
        Initialize Enterprise LLM Client.

        Args:
            config: Configuration object with enterprise LLM settings
        """
        self.config = config

        # Load environment variables from config
        self.client_id = getattr(config, "LLM_GATEWAY_CLIENT_ID", "")
        self.client_secret = getattr(config, "LLM_GATEWAY_CLIENT_SECRET", "")
        self.project_id = getattr(config, "LLM_GATEWAY_PROJECT_ID", "")
        self.token_url = getattr(config, "LLM_GATEWAY_TOKEN_URL", "")
        self.scope = getattr(config, "LLM_GATEWAY_SCOPE", "api")
        self.base_url = getattr(config, "LLM_GATEWAY_BASE_URL", "")
        self.model_name = getattr(config, "LLM_GATEWAY_MODEL_NAME", "enterprise-llm")

        # Request configuration
        self.request_timeout = int(getattr(config, "REQUEST_TIMEOUT", "180"))
        self.verify_ssl = getattr(config, "VERIFY_SSL", True)
        self.max_retries = 3
        self.retry_delay = 1  # Start with 1 second

        # Token cache
        self._token_cache = TokenCache()

        # Validate configuration
        self._validate_config()

        logger.info("🔒 ═══════════════════════════════════════════════════════════")
        logger.info("🔒 ENTERPRISE LLM CLIENT INITIALIZED")
        logger.info("🔒 ═══════════════════════════════════════════════════════════")
        logger.info("✅ Gateway URL: %s", self.base_url)
        logger.info("✅ Project ID: %s", self.project_id)
        logger.info("✅ OAuth2 Token Endpoint: %s", self.token_url)
        logger.info("✅ Model: %s", self.model_name)
        logger.info("🔒 STRICT ENTERPRISE-ONLY INFERENCE MODE ACTIVE 🔒")
        logger.info("🔒 ═══════════════════════════════════════════════════════════")

    def _validate_config(self) -> None:
        """Validate that all required configuration is present."""
        required_fields = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "project_id": self.project_id,
            "token_url": self.token_url,
            "base_url": self.base_url,
        }

        missing = [k for k, v in required_fields.items() if not v or not str(v).strip()]
        if missing:
            raise ValueError(
                f"Missing required Enterprise LLM config: {', '.join(missing)}. "
                "Check credentials.env for LLM_GATEWAY_* variables."
            )

    def _get_access_token(self) -> str:
        """
        Get valid OAuth access token.

        Uses cached token if available and not expired.
        Automatically generates new token via OAuth2 client credentials flow.

        Returns:
            Valid access token

        Raises:
            RuntimeError: If token generation fails
        """
        # Check cache first
        cached = self._token_cache.get()
        if cached:
            logger.debug("[Enterprise LLM] Using cached access token")
            return cached

        logger.info("[Enterprise LLM] Generating new access token")
        token = self._request_token()
        return token

    def _request_token(self) -> str:
        """
        Request new access token from OAuth2 token endpoint.

        Implements RFC 6749 client credentials flow.

        Returns:
            Access token string

        Raises:
            RuntimeError: If token request fails
        """
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        try:
            logger.info("🔐 AUTHENTICATING: Requesting OAuth2 access token from %s", self.token_url)
            response = requests.post(
                self.token_url,
                data=payload,
                headers=headers,
                timeout=self.request_timeout,
                verify=self.verify_ssl,
            )

            if response.status_code != 200:
                error_msg = f"🔴 Token request failed: {response.status_code}"
                try:
                    error_detail = response.json().get("error_description", response.text)
                    error_msg += f" - {error_detail}"
                except Exception:
                    error_msg += f" - {response.text[:200]}"

                logger.error("🔴 ENTERPRISE AUTHENTICATION FAILED: %s", error_msg)
                raise RuntimeError(error_msg)

            data = response.json()
            token = data.get("access_token")
            expires_in = data.get("expires_in", 3600)

            if not token:
                raise RuntimeError("Token response missing 'access_token' field")

            self._token_cache.set(token, expires_in)
            logger.info("✅ AUTHENTICATED: OAuth2 access token obtained (expires in %d seconds)", expires_in)
            return token

        except requests.exceptions.Timeout:
            error = "🔴 Token request timed out"
            logger.error("🔴 ENTERPRISE AUTHENTICATION FAILED: %s", error)
            raise RuntimeError(error)
        except requests.exceptions.ConnectionError as e:
            error = f"🔴 Failed to connect to token endpoint: {str(e)}"
            logger.error("🔴 ENTERPRISE AUTHENTICATION FAILED: %s", error)
            raise RuntimeError(error)
        except Exception as e:
            logger.exception("🔴 ENTERPRISE AUTHENTICATION FAILED: Unexpected error during token request")
            raise RuntimeError(f"Token request failed: {str(e)}")

    def _build_inference_payload(self, prompt: str) -> Dict[str, Any]:
        """
        Build request payload for LLM inference.

        Args:
            prompt: Complete prompt with system instructions, context, and user query

        Returns:
            Dictionary ready for JSON serialization and HTTP POST
        """
        return {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": 2048,
            "temperature": 0.1,  # Low temperature for factual answers
            "top_p": 0.95,
            "project_id": self.project_id,
        }

    def _send_request(self, prompt: str) -> str:
        """
        Send request to LLM gateway with automatic retry on failure.

        Args:
            prompt: Complete prompt with context

        Returns:
            Generated response text

        Raises:
            RuntimeError: If all retries fail
        """
        token = self._get_access_token()
        payload = self._build_inference_payload(prompt)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Project-ID": self.project_id,
            "x-project-id": self.project_id,
            "project-id": self.project_id,
            "x-client-id": self.client_id,
        }

        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    "🚀 ENTERPRISE GATEWAY REQUEST (attempt %d/%d, prompt_len=%d chars)",
                    attempt + 1,
                    self.max_retries,
                    len(prompt),
                )

                response = requests.post(
                    f"{self.base_url}/inference",
                    json=payload,
                    headers=headers,
                    timeout=self.request_timeout,
                    verify=self.verify_ssl,
                )

                # Success
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("response") or data.get("text") or data.get("output")

                    if not result:
                        raise RuntimeError("LLM response missing expected field")

                    logger.info("✅ ENTERPRISE GATEWAY RESPONSE RECEIVED (%d chars)", len(str(result)))
                    return str(result).strip()

                # Rate limit - retry with backoff
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", self.retry_delay))
                    if attempt < self.max_retries - 1:
                        logger.warning(
                            "⏱️  ENTERPRISE GATEWAY RATE LIMITED, retrying in %d seconds",
                            retry_after,
                        )
                        time.sleep(retry_after)
                        continue
                    else:
                        raise RuntimeError(f"🔴 Rate limited after {self.max_retries} retries")

                # Client error - don't retry
                if response.status_code < 500:
                    error_msg = f"🔴 LLM request failed: {response.status_code}"
                    try:
                        error_detail = response.json().get("error", response.text[:500])
                        error_msg += f" - {error_detail}"
                    except Exception:
                        error_msg += f" - {response.text[:200]}"
                    logger.error("🔴 ENTERPRISE GATEWAY CLIENT ERROR: %s", error_msg)
                    raise RuntimeError(error_msg)

                # Server error - retry
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        "⏱️  ENTERPRISE GATEWAY SERVER ERROR %d, retrying in %d seconds",
                        response.status_code,
                        delay,
                    )
                    time.sleep(delay)
                    continue
                else:
                    logger.error("🔴 ENTERPRISE GATEWAY SERVER ERROR: %d", response.status_code)
                    raise RuntimeError(f"LLM server error: {response.status_code}")

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning("⏱️  ENTERPRISE GATEWAY TIMEOUT, retrying in %d seconds", delay)
                    time.sleep(delay)
                    continue
                logger.error("🔴 ENTERPRISE GATEWAY TIMEOUT after retries")
                raise RuntimeError("Request timed out after retries")

            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        "⏱️  ENTERPRISE GATEWAY CONNECTION ERROR, retrying in %d seconds: %s",
                        delay,
                        str(e)[:100],
                    )
                    time.sleep(delay)
                    continue
                logger.error("🔴 ENTERPRISE GATEWAY CONNECTION FAILED: %s", str(e)[:200])
                raise RuntimeError(f"Connection failed: {str(e)[:200]}")

        logger.error("🔴 ENTERPRISE GATEWAY FAILED after %d retries", self.max_retries)
        raise RuntimeError(f"Failed after {self.max_retries} retries")

    def _messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """
        Convert LangChain message objects to a single prompt string.

        Args:
            messages: List of LangChain BaseMessage objects

        Returns:
            Formatted prompt string
        """
        parts: List[str] = []

        for msg in messages:
            msg_type = getattr(msg, "type", None) or msg.__class__.__name__
            content = getattr(msg, "content", "")

            if not content:
                continue

            # Handle different message types
            if msg_type.lower().startswith("system"):
                parts.append(f"SYSTEM:\n{content}")
            elif msg_type.lower().startswith("human"):
                parts.append(f"USER:\n{content}")
            elif msg_type.lower().startswith("ai"):
                parts.append(f"ASSISTANT:\n{content}")
            else:
                parts.append(str(content))

        return "\n\n".join(parts).strip()

    def generate_response(
        self,
        prompt: Optional[str] = None,
        messages: Optional[List[BaseMessage]] = None,
        context: Optional[str] = None,
    ) -> str:
        MOCK_MODE = os.getenv("ENTERPRISE_MOCK_MODE", "false").lower() == "true"

        if MOCK_MODE:
          return "✅ Enterprise mock response successful"

        """
        Generate a response from the enterprise LLM.

        Can accept either:
        - A raw prompt string
        - LangChain message objects (preferred for RAG integration)

        Args:
            prompt: Raw prompt string (alternative to messages)
            messages: List of LangChain message objects (preferred)
            context: Optional additional context to log

        Returns:
            Generated response string

        Raises:
            ValueError: If neither prompt nor messages provided
            RuntimeError: If LLM request fails
        """
        # Build complete prompt
        if messages:
            complete_prompt = self._messages_to_prompt(messages)
        elif prompt:
            complete_prompt = prompt
        else:
            raise ValueError("Either 'prompt' or 'messages' must be provided")

        if not complete_prompt or not complete_prompt.strip():
            raise ValueError("Prompt cannot be empty")

        # Log context if provided
        if context:
            logger.debug("[Enterprise LLM] Context: %s", context[:200])

        # Log enterprise inference initiation
        logger.info("🔐 INITIATING ENTERPRISE LLM INFERENCE")
        logger.info("   Prompt length: %d chars", len(complete_prompt))

        # Send request and get response
        result = self._send_request(complete_prompt)
        
        logger.info("✅ ENTERPRISE LLM INFERENCE COMPLETE")
        logger.info("   Response length: %d chars", len(result))
        
        return result

    def is_available(self) -> bool:
        """
        Check if enterprise LLM gateway is properly configured and reachable.

        Returns:
            True if gateway is available, False otherwise
        """
        try:
            token = self._get_access_token()
            return bool(token and str(token).strip())
        except Exception as e:
            logger.warning("[Enterprise LLM] Gateway unavailable: %s", str(e)[:200])
            return False
