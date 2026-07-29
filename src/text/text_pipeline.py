"""
Text pipeline for story generation.

Priority order:
  1. Groq  — if GROQ_API_KEY is set  (fast, free tier)
  2. IBM watsonx.ai — if IBM_API_KEY + IBM_PROJECT_ID are set
  3. Local mock — fallback when no credentials are present
"""

import os


def generate_text(prompt: str, max_tokens: int = 300) -> str:
    """
    Generate story text. Tries Groq first, then IBM, then mock.
    """
    groq_key = os.getenv("GROQ_API_KEY")
    ibm_key = os.getenv("IBM_API_KEY")
    ibm_project = os.getenv("IBM_PROJECT_ID")

    if groq_key:
        return _generate_with_groq(prompt, max_tokens, groq_key)

    if ibm_key and ibm_project:
        return _generate_with_watsonx(
            prompt, max_tokens, ibm_key, ibm_project,
            os.getenv("IBM_API_URL", "https://us-south.ml.cloud.ibm.com"),
        )

    # ── Fallback mock ─────────────────────────────────────────────────────────
    return (
        f"[Mock Story] Once upon a time, inspired by: \"{prompt[:60]}\"...\n\n"
        "Add a GROQ_API_KEY or IBM_API_KEY to your .env to generate real stories."
    )


# ── Groq ──────────────────────────────────────────────────────────────────────

def _generate_with_groq(prompt: str, max_tokens: int, api_key: str) -> str:
    from groq import Groq

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a creative storytelling assistant. "
                    "Write an engaging, vivid short story based on the user's prompt. "
                    "Keep it under 300 words. Do not include a title — start the story directly."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=max_tokens,
        temperature=0.85,
    )

    return completion.choices[0].message.content.strip()


# ── IBM watsonx.ai ────────────────────────────────────────────────────────────

def _generate_with_watsonx(
    prompt: str,
    max_tokens: int,
    api_key: str,
    project_id: str,
    api_url: str,
) -> str:
    from ibm_watsonx_ai import APIClient, Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params

    credentials = Credentials(api_key=api_key, url=api_url)
    client = APIClient(credentials)

    model = ModelInference(
        model_id="ibm/granite-13b-instruct-v2",
        api_client=client,
        project_id=project_id,
    )

    system_instruction = (
        "You are a creative storytelling assistant. "
        "Write an engaging, vivid short story based on the user's prompt. "
        "Keep it under 300 words."
    )
    full_prompt = f"{system_instruction}\n\nPrompt: {prompt}\n\nStory:"

    return model.generate_text(
        prompt=full_prompt,
        params={
            Params.MAX_NEW_TOKENS: max_tokens,
            Params.TEMPERATURE: 0.8,
            Params.TOP_P: 0.9,
        },
    )
