import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Service:
    name: str
    benefits: List[str]
    ideal_customers: str
    keywords: List[str]


@dataclass
class BusinessProfile:
    business_name: str
    brand_voice: str
    target_audience: str
    services: List[Service]


def load_business_profile(path: str | Path = "business_profile.json") -> BusinessProfile:
    file_path = Path(path)
    raw = json.loads(file_path.read_text(encoding="utf-8"))

    services = [
        Service(
            name=s["name"],
            benefits=s.get("benefits", []),
            ideal_customers=s.get("ideal_customers", ""),
            keywords=s.get("keywords", []),
        )
        for s in raw.get("services", [])
    ]

    return BusinessProfile(
        business_name=raw.get("business_name", ""),
        brand_voice=raw.get("brand_voice", ""),
        target_audience=raw.get("target_audience", ""),
        services=services,
    )

