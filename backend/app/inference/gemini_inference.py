import logging
import time

from google.genai import types

from app.core.config import settings
from app.core.exceptions import UpstreamError
from app.integrations.gemini import get_gemini_client

log = logging.getLogger(__name__)


def generate(system: str, turns: list[tuple[str, str]], temperature: float = 0.2) -> str:
    """turns: [(role, text)] with role in {"user", "model"}. Retries a bounded number of times."""
    contents = [types.Content(role=r, parts=[types.Part(text=t)]) for r, t in turns]
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        http_options=types.HttpOptions(timeout=settings.gemini_timeout_s * 1000),
    )
    last_err: Exception | None = None
    for attempt in range(settings.gemini_max_retries + 1):
        try:
            resp = get_gemini_client().models.generate_content(
                model=settings.gemini_model, contents=contents, config=config
            )
            if resp.text:
                return resp.text.strip()
            raise UpstreamError("Gemini không trả về nội dung (có thể bị chặn bởi bộ lọc an toàn)")
        except UpstreamError:
            raise
        except Exception as e:  # network, quota, 5xx ...
            last_err = e
            log.warning("Gemini call failed (attempt %s): %s", attempt + 1, e)
            time.sleep(1.5 * (attempt + 1))
    raise UpstreamError(f"Gemini API lỗi: {last_err}")
