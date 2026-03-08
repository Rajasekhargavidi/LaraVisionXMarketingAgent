from typing import Dict, List

from .config import load_business_profile, BusinessProfile, Service
from .llm_client import generate_social_post
from .platforms import (
    SUPPORTED_PLATFORMS,
    GeneratedPost,
    dispatch_post,
)


def build_payload(
    profile: BusinessProfile,
    service: Service,
    platform: str,
    goal: str = "increase awareness and attract new customers",
) -> Dict:
    return {
        "business_name": profile.business_name,
        "brand_voice": profile.brand_voice,
        "target_audience": profile.target_audience,
        "platform": platform,
        "service_name": service.name,
        "benefits": service.benefits,
        "ideal_customers": service.ideal_customers,
        "keywords": service.keywords,
        "goal": goal,
    }


def generate_posts_for_all_services(
    profile: BusinessProfile,
    platforms: List[str] | None = None,
    goal: str = "increase awareness and attract new customers",
) -> List[GeneratedPost]:
    platforms = platforms or SUPPORTED_PLATFORMS
    all_posts: List[GeneratedPost] = []

    for service in profile.services:
        for platform in platforms:
            payload = build_payload(profile, service, platform, goal)
            result = generate_social_post(payload)
            text = result.get("text", "").strip()
            hashtags = result.get("hashtags") or []
            image_idea = result.get("image_idea", "").strip()

            post = GeneratedPost(
                platform=platform,
                service_name=service.name,
                text=text,
                hashtags=hashtags,
                image_idea=image_idea,
            )
            all_posts.append(post)

    return all_posts


def run_agent_once(
    platforms: List[str] | None = None,
    goal: str = "increase awareness and attract new customers",
    credentials_by_platform: Dict[str, Dict[str, str]] | None = None,
) -> None:
    profile = load_business_profile()
    posts = generate_posts_for_all_services(profile, platforms=platforms, goal=goal)

    for post in posts:
        dispatch_post(post, credentials_by_platform=credentials_by_platform)


if __name__ == "__main__":
    run_agent_once()

