"""
Text pipeline for story generation.

Priority order:
    1. Gemini — if GEMINI_API_KEY is set (free tier)
    2. Groq — if GROQ_API_KEY is set (free tier)
    3. IBM watsonx.ai — if IBM_API_KEY + IBM_PROJECT_ID are set
    4. Local mock — fallback when no credentials are present
"""

import os


def generate_text(prompt: str, max_tokens: int = 300) -> str:
    """
    Generate story text. Tries Gemini, Groq, IBM, then mock.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    ibm_key = os.getenv("IBM_API_KEY")
    ibm_project = os.getenv("IBM_PROJECT_ID")

    if gemini_key:
        try:
            return _generate_with_gemini(prompt, max_tokens, gemini_key)
        except Exception as exc:
            print(f"[text_pipeline] Gemini error: {exc} — trying next provider")

    if groq_key:
        try:
            return _generate_with_groq(prompt, max_tokens, groq_key)
        except Exception as exc:
            print(f"[text_pipeline] Groq error: {exc} — using mock story")

    if ibm_key and ibm_project:
        try:
            return _generate_with_watsonx(
                prompt, max_tokens, ibm_key, ibm_project,
                os.getenv("IBM_API_URL", "https://us-south.ml.cloud.ibm.com"),
            )
        except Exception as exc:
            print(f"[text_pipeline] watsonx error: {exc} — using mock story")

    # ── Fallback mock ─────────────────────────────────────────────────────────
    return (
        f"[Mock Story] Once upon a time, inspired by: \"{prompt[:60]}\"...\n\n"
        "Add a GROQ_API_KEY or IBM_API_KEY to your .env to generate real stories."
    )


# ── Gemini ────────────────────────────────────────────────────────────────────

def _generate_with_gemini(prompt: str, max_tokens: int, api_key: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        contents=(
            "You are a creative storytelling assistant. "
            "Write an engaging, vivid short story based on the user's prompt. "
            "Do not include a title; start the story directly.\n\n"
            f"Prompt: {prompt}"
        ),
        config=types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=0.85,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response")
    return response.text.strip()


# ── Groq ──────────────────────────────────────────────────────────────────────

def _generate_with_groq(prompt: str, max_tokens: int, api_key: str) -> str:
    from groq import Groq

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
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
