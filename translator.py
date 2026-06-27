"""
ترجمه متن انگلیسی به فارسی
از MyMemory API (رایگان، بدون API key) استفاده می‌کنه
"""

import requests
import logging
import time

logger = logging.getLogger(__name__)

_cache: dict[str, str] = {}


def translate_to_persian(text: str, max_retries: int = 2) -> str:
    """
    متن انگلیسی رو به فارسی ترجمه کن
    از MyMemory API استفاده می‌کنه (رایگان تا ~۵۰۰۰ کاراکتر در روز)
    """
    if not text or not text.strip():
        return text

    # کوتاه کردن متن اگر خیلی طولانی بود
    text = text[:500]

    if text in _cache:
        return _cache[text]

    for attempt in range(max_retries):
        try:
            response = requests.get(
                "https://api.mymemory.translated.net/get",
                params={
                    "q":    text,
                    "langpair": "en|fa",
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            if data.get("responseStatus") == 200:
                translated = data["responseData"]["translatedText"]
                _cache[text] = translated
                return translated
            else:
                logger.warning(f"Translation API error: {data.get('responseDetails')}")

        except requests.exceptions.Timeout:
            logger.warning(f"Translation timeout (attempt {attempt+1})")
        except Exception as e:
            logger.error(f"Translation error: {e}")

        if attempt < max_retries - 1:
            time.sleep(1)

    # اگه ترجمه کار نکرد، متن اصلی رو برگردون
    logger.warning("Translation failed, returning original text")
    return text


if __name__ == "__main__":
    # تست مستقل
    logging.basicConfig(level=logging.INFO)
    samples = [
        "OpenAI releases new GPT-5 model with enhanced reasoning capabilities",
        "Google DeepMind achieves breakthrough in protein structure prediction",
    ]
    for s in samples:
        print(f"EN: {s}")
        print(f"FA: {translate_to_persian(s)}")
        print()
