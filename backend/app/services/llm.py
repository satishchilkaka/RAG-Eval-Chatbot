import asyncio

import httpx

from app.config import settings

MAX_RETRIES = 3


async def generate_answer(question: str, context: str) -> str:
    if not settings.llm_api_key:
        raise ValueError(
            "LLM_API_KEY is not set. Add your key to the .env file."
        )

    system_prompt = (
        "You are a helpful assistant that answers questions based only on the "
        "provided document context. If the answer is not in the context, say "
        "you don't have enough information. Be concise and cite relevant details."
    )
    user_prompt = (
        f"Context from uploaded documents:\n\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )

    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 1024,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        for attempt in range(MAX_RETRIES):
            response = await client.post(
                f"{settings.llm_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

            if response.status_code == 429 and attempt < MAX_RETRIES - 1:
                # Respect Retry-After if provided, else exponential backoff.
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2 ** attempt
                await asyncio.sleep(delay)
                continue

            if response.status_code == 429:
                raise ValueError(
                    f"Rate limited by the LLM provider for model "
                    f"'{settings.llm_model}' at {settings.llm_base_url}. "
                    "Wait a moment and retry, or check your provider's usage "
                    "limits/billing."
                )

            if response.status_code == 401:
                raise ValueError(
                    f"The LLM provider rejected the API key (401 "
                    f"Unauthorized) for {settings.llm_base_url}. Check "
                    "LLM_API_KEY in your .env file."
                )

            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
