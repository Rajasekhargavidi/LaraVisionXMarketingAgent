import os
from typing import Dict, Any

try:
    from dotenv import load_dotenv
except ImportError:  # graceful fallback if python-dotenv is not installed
    def load_dotenv(*args: Any, **kwargs: Any) -> None:  # type: ignore[no-redef]
        return None


load_dotenv()


def _generate_stub_post(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback generator used when no OPENAI_API_KEY is configured.
    Produces simple but usable copy without calling any external API.
    """
    service_name = payload.get("service_name", "your service")
    platform = payload.get("platform", "social media")
    benefits = payload.get("benefits", [])
    benefit_snippet = ", ".join(benefits[:3]) if benefits else ""

    base_text = (
        f"Discover how {service_name} from {payload.get('business_name', 'our team')} "
        f"can help you {benefit_snippet.lower()}."
    ).strip()

    text = (
        f"{base_text} We work with {payload.get('target_audience', 'modern businesses and learners')} "
        f"to drive real results. Learn more with LaraVisionX."
    )

    raw_keywords = payload.get("keywords", []) or []
    base_tags = [f"#{service_name.replace(' ', '')}".lower(), "#laravisionx"]
    extra_tags = [f"#{k.replace(' ', '')}".lower() for k in raw_keywords][:6]
    hashtags = base_tags + extra_tags

    image_idea = (
        f"Clean, modern visual representing {service_name} for {platform}, "
        f"with subtle tech and education-inspired elements in LaraVisionX brand style."
    )

    return {
        "text": text,
        "hashtags": hashtags,
        "image_idea": image_idea,
    }


def _create_client():
    # Allow completely disabling OpenAI calls via env flag.
    if os.getenv("DISABLE_OPENAI", "false").lower() == "true":
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from openai import OpenAI  # imported lazily so openai is optional
    except ImportError:
        return None
    return OpenAI(api_key=api_key)


def generate_social_post(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the LLM to generate a social media post.

    Expected payload keys:
      - business_name
      - brand_voice
      - target_audience
      - platform
      - service_name
      - benefits
      - ideal_customers
      - keywords
      - goal
    """
    client = _create_client()
    if client is None:
        # No API key or OpenAI package; fall back to a local template-based generator.
        return _generate_stub_post(payload)

    system_prompt = (
        f"You are a social media marketing expert for the business "
        f"{payload['business_name']}. "
        f"Brand voice: {payload['brand_voice']}. "
        f"Target audience: {payload['target_audience']}. "
        "Generate engaging, clear posts that fit each platform's style. "
        "Return a concise JSON object with fields 'text', 'hashtags', and 'image_idea'."
    )

    user_prompt = (
        f"Platform: {payload['platform']}\n"
        f"Service: {payload['service_name']}\n"
        f"Benefits: {', '.join(payload.get('benefits', []))}\n"
        f"Ideal customers: {payload.get('ideal_customers', '')}\n"
        f"Keywords: {', '.join(payload.get('keywords', []))}\n"
        f"Goal: {payload.get('goal', 'increase awareness and drive inquiries')}\n\n"
        "Constraints:\n"
        "- Adapt tone and formatting to the platform.\n"
        "- Keep the main text concise and natural.\n"
        "- Include 5-10 relevant hashtags.\n"
        "- Suggest a simple image idea that could be turned into a static image.\n"
        "Return ONLY valid JSON in the following structure:\n"
        "{\n"
        "  \"text\": \"...\",\n"
        "  \"hashtags\": [\"#tag1\", \"#tag2\"],\n"
        "  \"image_idea\": \"...\"\n"
        "}\n"
    )

    try:
        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.8,
        )

        content = completion.choices[0].message.content
        if not content:
            raise RuntimeError("LLM returned empty content.")

        import json

        return json.loads(content)
    except Exception:
        # On any API error (including quota issues), fall back to stub generation.
        return _generate_stub_post(payload)

