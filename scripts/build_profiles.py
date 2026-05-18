from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.models.schemas import PastReview, UserPersona  # noqa: E402
from app.services.data_loader import DataLoader  # noqa: E402
from app.services.user_profile_builder import UserProfileBuilder  # noqa: E402


def main() -> None:
    loader = DataLoader(ROOT / "data" / "sample")
    builder = UserProfileBuilder()
    output_dir = ROOT / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    profiles = []
    for user in loader.load_users():
        history = [PastReview(**row) for row in loader.get_user_history(user["user_id"])]
        persona = UserPersona(user_id=user["user_id"], description=user["description"], past_reviews=history)
        profile = builder.build(persona)
        profiles.append(
            {
                "user_id": profile.user_id,
                "summary": profile.summary,
                "average_rating": round(profile.average_rating, 2),
                "rating_strictness": round(profile.rating_strictness, 2),
                "category_affinity": profile.category_affinity,
                "preferred_terms": profile.preferred_terms,
                "common_complaints": profile.common_complaints,
                "price_sensitivity_level": profile.price_sensitivity_level,
                "spice_preference": profile.spice_preference,
                "portion_preference": profile.portion_preference,
            }
        )

    path = output_dir / "user_profiles.json"
    path.write_text(json.dumps(profiles, indent=2), encoding="utf-8")
    print(f"Wrote {len(profiles)} user profiles to {path}")


if __name__ == "__main__":
    main()
