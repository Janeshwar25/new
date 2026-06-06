def _build_inference_payload(self, prompt: str) -> Dict[str, Any]:
    """
    Build request payload for enterprise LLM inference.
    """

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


def _send_request(self, prompt: str) -> str:
    """
    Send request to LLM gateway with automatic retry on failure.
    """

    token = self._get_access_token()

    payload = self._build_inference_payload(prompt)

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

    # Retry logic with exponential backoff
    for attempt in range(self.max_retries):

        try:

            logger.info(
                "🚀 ENTERPRISE GATEWAY REQUEST "
                "(attempt %d/%d, prompt_len=%d chars)",
                attempt + 1,
                self.max_retries,
                len(prompt),
            )

            safe_headers = {}

            for k, v in headers.items():

                if "auth" in k.lower() or "token" in k.lower():
                    safe_headers[k] = "***MASKED***"

                else:
                    safe_headers[k] = v

            print("\n===== ENTERPRISE REQUEST =====")
            print("URL:", self.base_url)
            print("HEADERS:", safe_headers)
            print("PAYLOAD:", payload)
            print("==============================\n")

            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.request_timeout,
                verify=self.verify_ssl,
            )

            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text[:1000])

            # =========================================================
            # SUCCESS
            # =========================================================
            if response.status_code == 200:

                data = response.json()

                result = (
                    data.get("response")
                    or data.get("text")
                    or data.get("output")
                    or data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content")
                )

                if not result:
                    raise RuntimeError(
                        "Enterprise response missing content"
                    )

                logger.info(
                    "✅ ENTERPRISE GATEWAY RESPONSE RECEIVED"
                )

                return str(result).strip()

            # =========================================================
            # RATE LIMIT
            # =========================================================
            if response.status_code == 429:

                retry_after = int(
                    response.headers.get(
                        "Retry-After",
                        self.retry_delay
                    )
                )

                if attempt < self.max_retries - 1:

                    logger.warning(
                        "⏱️ ENTERPRISE GATEWAY RATE LIMITED, "
                        "retrying in %d seconds",
                        retry_after,
                    )

                    time.sleep(retry_after)
                    continue

                raise RuntimeError(
                    f"🔴 Rate limited after "
                    f"{self.max_retries} retries"
                )

            # =========================================================
            # CLIENT ERROR
            # =========================================================
            if response.status_code < 500:

                error_msg = (
                    f"🔴 LLM request failed: "
                    f"{response.status_code} - "
                    f"{response.text[:1000]}"
                )

                logger.error(
                    "🔴 ENTERPRISE GATEWAY CLIENT ERROR: %s",
                    error_msg,
                )

                raise RuntimeError(error_msg)

            # =========================================================
            # SERVER ERROR
            # =========================================================
            if attempt < self.max_retries - 1:

                delay = self.retry_delay * (2 ** attempt)

                logger.warning(
                    "⏱️ ENTERPRISE GATEWAY SERVER ERROR %d, "
                    "retrying in %d seconds",
                    response.status_code,
                    delay,
                )

                time.sleep(delay)

                continue

            raise RuntimeError(
                f"🔴 LLM server error: "
                f"{response.status_code}"
            )

        except requests.exceptions.Timeout:

            if attempt < self.max_retries - 1:

                delay = self.retry_delay * (2 ** attempt)

                logger.warning(
                    "⏱️ ENTERPRISE GATEWAY TIMEOUT, "
                    "retrying in %d seconds",
                    delay,
                )

                time.sleep(delay)

                continue

            raise RuntimeError(
                "🔴 Request timed out after retries"
            )

        except requests.exceptions.ConnectionError as e:

            if attempt < self.max_retries - 1:

                delay = self.retry_delay * (2 ** attempt)

                logger.warning(
                    "⏱️ ENTERPRISE GATEWAY CONNECTION ERROR, "
                    "retrying in %d seconds: %s",
                    delay,
                    str(e)[:100],
                )

                time.sleep(delay)

                continue

            raise RuntimeError(
                f"🔴 Connection failed: {str(e)[:200]}"
            )

    raise RuntimeError(
        f"🔴 Failed after {self.max_retries} retries"
    )


def generate_response(
    self,
    prompt: Optional[str] = None,
    messages: Optional[List[BaseMessage]] = None,
    context: Optional[str] = None,
) -> str:

    MOCK_MODE = os.getenv(
        "ENTERPRISE_MOCK_MODE",
        "false"
    ).lower() == "true"

    if MOCK_MODE:
        return "✅ Enterprise mock response successful"

    """
    Generate a response from the enterprise LLM.
    """

    # =========================================================
    # BUILD PROMPT
    # =========================================================
    if messages:
        complete_prompt = self._messages_to_prompt(messages)

    elif prompt:
        complete_prompt = prompt

    else:
        raise ValueError(
            "Either 'prompt' or 'messages' must be provided"
        )

    if not complete_prompt or not complete_prompt.strip():
        raise ValueError("Prompt cannot be empty")

    if context:
        logger.debug(
            "[Enterprise LLM] Context: %s",
            context[:200]
        )

    logger.info("🔐 INITIATING ENTERPRISE LLM INFERENCE")

    logger.info(
        "Prompt length: %d chars",
        len(complete_prompt)
    )

    result = self._send_request(complete_prompt)

    logger.info(
        "✅ ENTERPRISE LLM INFERENCE COMPLETE"
    )

    logger.info(
        "Response length: %d chars",
        len(result)
    )

    return result
