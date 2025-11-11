from __future__ import annotations

import os
from anthropic import Anthropic, APIStatusError

API_KEY = os.getenv('ANTHROPIC_API_KEY')
_client: Anthropic | None = None

def _get_client() -> Anthropic:
    global _client
    if _client is None:
        if not API_KEY:
            raise RuntimeError('ANTHROPIC_API_KEY environment variable is not set')
        _client = Anthropic(api_key=API_KEY)
    return _client

def preguntar_a_claude(prompt: str, *, model: str = 'claude-3-5-haiku-20241022', max_tokens: int = 300) -> str:
    if not prompt or not prompt.strip():
        raise ValueError('prompt must be a non-empty string')
    client = _get_client()
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
    except APIStatusError as exc:
        raise RuntimeError(f'Anthropic API error: {exc.status_code}') from exc
    return response.content[0].text if response.content else ''
