from dataclasses import dataclass
from typing import Dict, List
import os

try:
    import requests
except ImportError:  # graceful fallback if requests is not installed
    requests = None  # type: ignore[assignment]


SUPPORTED_PLATFORMS: List[str] = [
    "instagram",
    "facebook",
    "linkedin",
    "x",
    "whatsapp",
]


@dataclass
class GeneratedPost:
    platform: str
    service_name: str
    text: str
    hashtags: List[str]
    image_idea: str


def format_post_for_output(post: GeneratedPost) -> str:
    hashtags_str = " ".join(post.hashtags)
    return (
        f"[{post.platform.upper()}] Post for service '{post.service_name}':\n"
        f"{post.text}\n\n"
        f"Hashtags: {hashtags_str}\n"
        f"Image idea: {post.image_idea}\n"
    )


def _instagram_credentials(credentials: Dict[str, str] | None = None) -> Dict[str, str]:
    """
    Resolve Instagram credentials from explicit dict or environment variables.

    Required for real posting:
      - INSTAGRAM_ACCESS_TOKEN
      - INSTAGRAM_IG_USER_ID (Instagram Business account ID)
      - INSTAGRAM_IMAGE_URL (publicly accessible image URL to use with the post)
    """
    credentials = credentials or {}
    return {
        "access_token": credentials.get("access_token") or os.getenv("INSTAGRAM_ACCESS_TOKEN", ""),
        "ig_user_id": credentials.get("ig_user_id") or os.getenv("INSTAGRAM_IG_USER_ID", ""),
        "image_url": credentials.get("image_url") or os.getenv("INSTAGRAM_IMAGE_URL", ""),
    }


def post_to_instagram(post: GeneratedPost, credentials: Dict[str, str] | None = None) -> None:
    """
    Instagram posting via Meta Instagram Graph API.

    This supports two modes:
      1) If all required credentials are available AND the 'requests' package is installed,
         it will attempt a real API call to publish an image post.
      2) Otherwise, it falls back to printing the content to the console.

    To enable real posting, set these environment variables:
      - INSTAGRAM_ACCESS_TOKEN
      - INSTAGRAM_IG_USER_ID
      - INSTAGRAM_IMAGE_URL
    """
    creds = _instagram_credentials(credentials)
    access_token = creds["access_token"]
    ig_user_id = creds["ig_user_id"]
    image_url = creds["image_url"]

    # Fallback to console output if we don't have everything needed for a real API call.
    if not (access_token and ig_user_id and image_url and requests):
        print(format_post_for_output(post))
        if not requests:
            print("[INFO] 'requests' library not installed; skipping real Instagram API call.")
        if not access_token or not ig_user_id or not image_url:
            print("[INFO] Instagram credentials not fully configured; printing post instead of publishing.\n")
        return

    caption = f"{post.text}\n\n" + " ".join(post.hashtags)

    # Step 1: Create media object
    media_endpoint = f"https://graph.facebook.com/v21.0/{ig_user_id}/media"
    media_payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    }

    try:
        media_res = requests.post(media_endpoint, data=media_payload, timeout=30)
        media_res.raise_for_status()
        media_id = media_res.json().get("id")
    except Exception as exc:  # pragma: no cover - network dependent
        print(format_post_for_output(post))
        print(f"[ERROR] Failed to create Instagram media object: {exc}")
        return

    if not media_id:
        print(format_post_for_output(post))
        print("[ERROR] Instagram API did not return a media ID; cannot publish.")
        return

    # Step 2: Publish media
    publish_endpoint = f"https://graph.facebook.com/v21.0/{ig_user_id}/media_publish"
    publish_payload = {
        "creation_id": media_id,
        "access_token": access_token,
    }

    try:
        publish_res = requests.post(publish_endpoint, data=publish_payload, timeout=30)
        publish_res.raise_for_status()
        print(format_post_for_output(post))
        print(f"[INFO] Instagram post published successfully. Response: {publish_res.json()}\n")
    except Exception as exc:  # pragma: no cover - network dependent
        print(format_post_for_output(post))
        print(f"[ERROR] Failed to publish Instagram media: {exc}")


def post_to_facebook(post: GeneratedPost, credentials: Dict[str, str] | None = None) -> None:
    """
    Placeholder for real Facebook Page posting logic.
    """
    print(format_post_for_output(post))


def post_to_linkedin(post: GeneratedPost, credentials: Dict[str, str] | None = None) -> None:
    """
    Placeholder for real LinkedIn posting logic.
    """
    print(format_post_for_output(post))


def post_to_x(post: GeneratedPost, credentials: Dict[str, str] | None = None) -> None:
    """
    Placeholder for real X (Twitter) posting logic.
    """
    print(format_post_for_output(post))


def post_to_whatsapp(post: GeneratedPost, credentials: Dict[str, str] | None = None) -> None:
    """
    WhatsApp sending via WhatsApp Business Cloud API (single recipient).

    This supports two modes:
      1) If all required credentials are available AND the 'requests' package is installed,
         it will attempt a real API call to send a text message.
      2) Otherwise, it falls back to printing the content to the console.

    To enable real sending, set these environment variables:
      - WHATSAPP_ACCESS_TOKEN        (Bearer token for Cloud API)
      - WHATSAPP_PHONE_NUMBER_ID     (phone number ID from Meta)
      - WHATSAPP_RECIPIENT_NUMBER    (recipient phone in international format, e.g. 9198xxxxxxx)
    """
    creds = credentials or {}

    access_token = creds.get("access_token") or os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    phone_number_id = creds.get("phone_number_id") or os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    recipient = creds.get("recipient") or os.getenv("WHATSAPP_RECIPIENT_NUMBER", "")

    # Fallback to console output if we don't have everything needed for a real API call.
    if not (access_token and phone_number_id and recipient and requests):
        print(format_post_for_output(post))
        if not requests:
            print("[INFO] 'requests' library not installed; skipping real WhatsApp API call.")
        if not access_token or not phone_number_id or not recipient:
            print("[INFO] WhatsApp credentials not fully configured; printing post instead of sending.\n")
        return

    message_body = f"{post.text}\n\n" + " ".join(post.hashtags)

    url = f"https://graph.facebook.com/v21.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_body,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        print(format_post_for_output(post))
        print(f"[INFO] WhatsApp message sent successfully. Response: {response.json()}\n")
    except Exception as exc:  # pragma: no cover - network dependent
        print(format_post_for_output(post))
        print(f"[ERROR] Failed to send WhatsApp message: {exc}")


def dispatch_post(post: GeneratedPost, credentials_by_platform: Dict[str, Dict[str, str]] | None = None) -> None:
    creds = credentials_by_platform.get(post.platform, {}) if credentials_by_platform else {}

    if post.platform == "instagram":
        post_to_instagram(post, creds)
    elif post.platform == "facebook":
        post_to_facebook(post, creds)
    elif post.platform == "linkedin":
        post_to_linkedin(post, creds)
    elif post.platform == "x":
        post_to_x(post, creds)
    elif post.platform == "whatsapp":
        post_to_whatsapp(post, creds)
    else:
        raise ValueError(f"Unsupported platform: {post.platform}")

