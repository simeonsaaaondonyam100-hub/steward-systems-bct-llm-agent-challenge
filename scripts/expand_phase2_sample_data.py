from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT / "data" / "sample"


USERS = [
    {
        "user_id": "user_001",
        "name": "Tola",
        "description": "Price-sensitive Lagos university student who likes spicy affordable meals, filling portions, and fast delivery after lectures.",
        "rating_style": "balanced",
        "cold_start": False,
    },
    {
        "user_id": "user_002",
        "name": "Chinedu",
        "description": "Busy Lagos Island professional who values clean packaging, premium taste, quick office lunch, and reliable delivery.",
        "rating_style": "strict",
        "cold_start": False,
    },
    {
        "user_id": "user_003",
        "name": "Aisha",
        "description": "Family-oriented Abuja parent who prefers generous portions, mild spice, hygiene, and meals that can be shared at home.",
        "rating_style": "generous",
        "cold_start": False,
    },
    {
        "user_id": "user_004",
        "name": "Kunle",
        "description": "Mainland tech worker who likes shawarma, suya, cold drinks, late-night delivery, peppery food, and value for money.",
        "rating_style": "generous",
        "cold_start": False,
    },
    {
        "user_id": "user_005",
        "name": "Efe",
        "description": "Port Harcourt spice lover who enjoys pepper soup, bole, seafood, asun, lively local flavour, and honest portions.",
        "rating_style": "balanced",
        "cold_start": False,
    },
    {
        "user_id": "user_006",
        "name": "Mariam",
        "description": "Budget-conscious NYSC member who wants affordable groceries, durable products, simple meals, and dependable delivery.",
        "rating_style": "strict",
        "cold_start": False,
    },
    {
        "user_id": "user_007",
        "name": "Seyi",
        "description": "Book and movie lover who enjoys Nigerian stories, zobo or Chapman with snacks, and calm weekend plans.",
        "rating_style": "balanced",
        "cold_start": False,
    },
    {
        "user_id": "user_008",
        "name": "Ngozi",
        "description": "Busy Lekki parent who likes family meals, clean restaurants, kids-friendly options, and predictable delivery time.",
        "rating_style": "balanced",
        "cold_start": False,
    },
    {
        "user_id": "user_009",
        "name": "Ibrahim",
        "description": "Health-conscious customer who prefers grilled meals, low sugar drinks, good protein, and moderate prices.",
        "rating_style": "strict",
        "cold_start": False,
    },
    {
        "user_id": "user_010",
        "name": "Bimbo",
        "description": "Social organiser who buys small chops, drinks, cakes, and group-friendly meals for birthdays and office hangouts.",
        "rating_style": "generous",
        "cold_start": False,
    },
    {
        "user_id": "user_011",
        "name": "Damilola",
        "description": "Very strict reviewer in Yaba who complains about late delivery, cold food, careless packaging, and inflated prices.",
        "rating_style": "strict",
        "cold_start": False,
    },
    {
        "user_id": "user_012",
        "name": "Adaeze",
        "description": "Generous reviewer who enjoys trying new Nigerian restaurants, values ambience, friendly service, and local flavour.",
        "rating_style": "generous",
        "cold_start": False,
    },
    {
        "user_id": "user_013",
        "name": "Musa",
        "description": "Delivery-sensitive Abuja consultant who needs quick lunch, clear timing, neat packaging, and no unnecessary delay.",
        "rating_style": "strict",
        "cold_start": False,
    },
    {
        "user_id": "user_014",
        "name": "Fisayo",
        "description": "Ambience-focused Lagos diner who likes stylish restaurants, smooth service, Chapman, desserts, and date-night comfort.",
        "rating_style": "balanced",
        "cold_start": False,
    },
    {
        "user_id": "user_015",
        "name": "Temi",
        "description": "Cold-start Lagos visitor who wants affordable local food, not too much pepper, and quick delivery near Yaba.",
        "rating_style": "balanced",
        "cold_start": True,
    },
    {
        "user_id": "user_016",
        "name": "Nneka",
        "description": "Cold-start remote worker who wants useful everyday products, books, light meals, and low-stress recommendations.",
        "rating_style": "balanced",
        "cold_start": True,
    },
    {
        "user_id": "user_017",
        "name": "Kemi",
        "description": "University hostel resident who likes meat pie, puff-puff, cheap drinks, fast delivery, and snacks for friends.",
        "rating_style": "generous",
        "cold_start": False,
    },
    {
        "user_id": "user_018",
        "name": "Obinna",
        "description": "Everyday product buyer who values durable electronics, fair price, clear specs, and products that survive Nigerian power realities.",
        "rating_style": "strict",
        "cold_start": False,
    },
]


ITEMS = [
    ("item_001", "Spicy Chicken Shawarma", "Food", 2500, 4, 35, "medium", "Lagos Mainland", ["shawarma", "spicy", "student", "quick"], 88, 4.2),
    ("item_002", "Jollof Rice and Grilled Chicken", "Food", 3200, 4, 45, "large", "Lagos", ["jollof", "chicken", "filling", "party"], 93, 4.4),
    ("item_003", "Amala with Ewedu and Gbegiri", "Food", 2200, 2, 40, "large", "Yaba", ["amala", "swallow", "local", "budget"], 82, 4.1),
    ("item_004", "Suya Platter with Yaji", "Food", 3800, 5, 30, "medium", "Ikeja", ["suya", "pepper", "night", "protein"], 95, 4.5),
    ("item_005", "Catfish Pepper Soup", "Food", 4500, 5, 55, "medium", "Port Harcourt", ["pepper soup", "catfish", "spicy"], 79, 4.3),
    ("item_006", "Bole and Fish Combo", "Food", 3500, 4, 50, "large", "Port Harcourt", ["bole", "fish", "filling", "local"], 86, 4.4),
    ("item_007", "Fried Rice Party Pack", "Food", 14500, 1, 70, "family", "Lekki", ["fried rice", "party", "family", "sharing"], 73, 4.0),
    ("item_008", "Small Chops Box", "Food", 6000, 1, 45, "sharing", "Lagos", ["small chops", "party", "snacks", "sharing"], 89, 4.2),
    ("item_009", "Asun with Fried Plantain", "Food", 5000, 5, 50, "medium", "Surulere", ["asun", "pepper", "plantain"], 80, 4.1),
    ("item_010", "Moi Moi and Pap Breakfast", "Food", 1800, 1, 25, "medium", "Lagos Mainland", ["breakfast", "moi moi", "budget", "quick"], 70, 3.9),
    ("item_011", "Grilled Chicken Salad Bowl", "Food", 4200, 1, 35, "medium", "Victoria Island", ["healthy", "protein", "salad", "office"], 65, 4.0),
    ("item_012", "Egusi Soup and Pounded Yam", "Food", 4200, 3, 60, "large", "Abuja", ["egusi", "swallow", "family", "filling"], 84, 4.3),
    ("item_013", "Ofada Rice and Ayamase", "Food", 4800, 5, 55, "large", "Lagos Island", ["ofada", "ayamase", "pepper", "local"], 87, 4.4),
    ("item_014", "Akara and Custard Combo", "Food", 1700, 1, 25, "medium", "Lagos Mainland", ["akara", "breakfast", "budget", "quick"], 72, 3.9),
    ("item_015", "Meat Pie Duo", "Food", 1600, 1, 20, "small", "Yaba", ["meat pie", "snack", "student", "quick"], 76, 3.8),
    ("item_016", "Puff-Puff Sharing Bowl", "Food", 2000, 1, 20, "sharing", "Lagos Mainland", ["puff-puff", "snack", "sharing", "budget"], 81, 4.0),
    ("item_017", "Grilled Chicken and Plantain", "Food", 5200, 3, 40, "large", "Lekki", ["grilled chicken", "plantain", "protein"], 83, 4.2),
    ("item_018", "Beans and Plantain Bowl", "Food", 2400, 2, 35, "large", "Yaba", ["beans", "plantain", "budget", "filling"], 75, 4.0),
    ("item_019", "Seafood Okra Soup", "Food", 6200, 4, 65, "large", "Port Harcourt", ["seafood", "okra", "swallow", "premium"], 77, 4.3),
    ("item_020", "Premium Sushi Box", "Food", 18500, 1, 80, "small", "Victoria Island", ["sushi", "premium", "date"], 50, 4.0),
    ("item_021", "Office Lunch Rice Bowl", "Food", 3600, 2, 28, "medium", "Victoria Island", ["office lunch", "quick", "rice", "clean"], 78, 4.0),
    ("item_022", "Family Pepperless Chicken Stew", "Food", 9000, 1, 50, "family", "Abuja", ["family", "mild", "chicken", "sharing"], 74, 4.1),
    ("item_023", "Smoky Party Jollof Tray", "Food", 16500, 3, 75, "family", "Lagos", ["jollof", "party", "sharing"], 90, 4.5),
    ("item_024", "Ewa Agoyin and Agege Bread", "Food", 2300, 3, 38, "large", "Lagos Mainland", ["ewa agoyin", "bread", "local", "budget"], 79, 4.1),
    ("item_025", "Chicken Pepper Soup Bowl", "Food", 3900, 5, 45, "medium", "Abuja", ["pepper soup", "chicken", "spicy"], 76, 4.0),
    ("item_026", "Zobo Ginger Bottle", "Drink", 900, 3, 20, "single", "Lagos", ["zobo", "ginger", "budget", "drink"], 78, 4.1),
    ("item_027", "Classic Chapman", "Drink", 1500, 1, 25, "single", "Lagos", ["chapman", "sweet", "drink", "hangout"], 81, 4.0),
    ("item_028", "Tiger Nut Drink", "Drink", 1200, 1, 20, "single", "Abuja", ["tigernut", "low sugar", "drink"], 66, 3.8),
    ("item_029", "Cold Malt Pack", "Drink", 2500, 1, 30, "sharing", "Lagos", ["malt", "sharing", "cold drink"], 75, 3.9),
    ("item_030", "Kunu Bottle", "Drink", 800, 1, 18, "single", "Abuja", ["kunu", "budget", "local drink"], 61, 3.7),
    ("item_031", "Fresh Orange Juice", "Drink", 1800, 1, 22, "single", "Victoria Island", ["juice", "healthy", "low sugar"], 68, 4.0),
    ("item_032", "Ginger Pineapple Juice", "Drink", 1600, 2, 25, "single", "Lagos", ["ginger", "pineapple", "drink"], 72, 4.0),
    ("item_033", "Reusable Food Flask", "Product", 7500, 0, 48, "single", "Lagos", ["flask", "durable", "school", "office"], 72, 4.2),
    ("item_034", "Budget Android Earbuds", "Product", 9500, 0, 36, "single", "Lagos", ["earbuds", "budget", "electronics"], 68, 3.6),
    ("item_035", "Rechargeable Standing Fan", "Product", 32000, 0, 72, "single", "Lagos", ["fan", "rechargeable", "durable", "power"], 91, 4.4),
    ("item_036", "Student Grocery Starter Pack", "Product", 8500, 0, 40, "family", "Yaba", ["grocery", "student", "budget", "staples"], 87, 4.0),
    ("item_037", "Power Bank 20000mAh", "Product", 18500, 0, 35, "single", "Lagos", ["power bank", "durable", "electronics", "power"], 89, 4.3),
    ("item_038", "Mosquito Repellent Kit", "Product", 4200, 0, 30, "family", "Abuja", ["home", "health", "family"], 70, 3.9),
    ("item_039", "Non-Stick Frying Pan", "Product", 12500, 0, 45, "single", "Lagos", ["kitchen", "durable", "home"], 73, 4.1),
    ("item_040", "Budget Data Router", "Product", 28000, 0, 55, "single", "Lagos", ["router", "remote work", "electronics"], 82, 4.0),
    ("item_041", "Nigerian Campus Love Stories", "Book", 3000, 0, 24, "single", "Online", ["campus", "romance", "nigerian story"], 74, 4.2),
    ("item_042", "Things Fall Apart Paperback", "Book", 4500, 0, 36, "single", "Online", ["classic", "nigerian story", "literature"], 92, 4.8),
    ("item_043", "Personal Finance for Young Nigerians", "Book", 5500, 0, 36, "single", "Online", ["finance", "young nigerians", "practical"], 69, 4.1),
    ("item_044", "Lagos Food Memoir", "Book", 4200, 0, 30, "single", "Online", ["food", "lagos", "memoir"], 62, 4.0),
    ("item_045", "African Sci-Fi Short Stories", "Book", 5000, 0, 40, "single", "Online", ["sci-fi", "african", "stories"], 58, 3.9),
    ("item_046", "Nigerian Startup Playbook", "Book", 7000, 0, 36, "single", "Online", ["startup", "business", "nigeria"], 64, 4.0),
    ("item_047", "Lagos Noir Movie Night", "Movie", 2500, 0, 0, "single", "Streaming", ["thriller", "lagos", "nollywood"], 76, 4.0),
    ("item_048", "Nollywood Family Comedy", "Movie", 2200, 0, 0, "family", "Streaming", ["comedy", "family", "nollywood"], 83, 3.8),
    ("item_049", "Documentary on Lagos Food Markets", "Movie", 1800, 0, 0, "single", "Streaming", ["documentary", "food", "lagos"], 64, 4.3),
    ("item_050", "Afrobeats Concert Stream", "Movie", 3000, 0, 0, "sharing", "Streaming", ["music", "concert", "hangout"], 85, 4.1),
    ("item_051", "Northern Nigeria Travel Documentary", "Movie", 2000, 0, 0, "single", "Streaming", ["documentary", "travel", "nigeria"], 59, 4.0),
    ("item_052", "Office Birthday Cake", "Food", 18000, 1, 65, "sharing", "Lagos", ["cake", "birthday", "office", "sharing"], 77, 4.2),
    ("item_053", "Date Night Dessert Box", "Food", 9500, 1, 45, "sharing", "Lekki", ["dessert", "date", "premium"], 69, 4.1),
    ("item_054", "Kilishi Snack Pack", "Food", 3200, 4, 35, "small", "Abuja", ["kilishi", "spicy", "snack"], 71, 4.0),
    ("item_055", "Yam Porridge Bowl", "Food", 2800, 2, 42, "large", "Lagos Mainland", ["yam", "porridge", "filling", "budget"], 67, 3.9),
    ("item_056", "Coconut Rice and Turkey", "Food", 4800, 2, 48, "large", "Lekki", ["rice", "turkey", "family"], 74, 4.1),
    ("item_057", "Plantain Chips Multipack", "Product", 3500, 1, 28, "sharing", "Lagos", ["plantain chips", "snack", "sharing"], 78, 3.9),
    ("item_058", "Office Snack Basket", "Product", 11000, 1, 40, "sharing", "Lagos", ["snacks", "office", "sharing"], 80, 4.0),
    ("item_059", "Low Sugar Greek Yoghurt", "Drink", 2200, 0, 20, "single", "Lagos", ["healthy", "low sugar", "protein"], 63, 4.0),
    ("item_060", "Palm Wine Bottle", "Drink", 1800, 0, 30, "single", "Lagos", ["palm wine", "local drink", "hangout"], 60, 3.8),
]


USER_POSITIVES = {
    "user_001": {"jollof", "shawarma", "zobo", "akara", "beans", "puff-puff", "ewa agoyin", "budget", "quick", "filling", "spicy"},
    "user_002": {"office", "quick", "clean", "premium", "salad", "rice", "sushi", "flask"},
    "user_003": {"family", "large", "sharing", "mild", "egusi", "amala", "fried rice", "chicken"},
    "user_004": {"shawarma", "suya", "malt", "asun", "pepper", "late", "quick", "value"},
    "user_005": {"pepper soup", "bole", "fish", "seafood", "asun", "spicy", "local"},
    "user_006": {"budget", "grocery", "akara", "breakfast", "durable", "finance", "cheap"},
    "user_007": {"book", "movie", "nollywood", "documentary", "zobo", "story", "campus"},
    "user_008": {"family", "kids", "sharing", "cake", "clean", "mild", "flask"},
    "user_009": {"healthy", "grilled", "protein", "low sugar", "salad", "tigernut", "yoghurt"},
    "user_010": {"small chops", "cake", "chapman", "party", "office", "sharing", "birthday"},
    "user_011": {"quick", "clean", "affordable", "hot", "packaging"},
    "user_012": {"ambience", "local", "new", "chapman", "dessert", "friendly", "date"},
    "user_013": {"quick", "office", "lunch", "clean", "predictable", "no delay"},
    "user_014": {"date", "dessert", "chapman", "ambience", "premium", "lekki"},
    "user_017": {"meat pie", "puff-puff", "zobo", "snack", "student", "budget", "quick"},
    "user_018": {"durable", "power", "electronics", "router", "fan", "power bank", "clear specs"},
}


STYLE_BIAS = {"strict": -0.6, "balanced": 0.0, "generous": 0.45}


def build_item(row: tuple) -> dict:
    item_id, name, category, price, spice, delivery, portion, location, tags, popularity, average = row
    metadata = {
        "spice_level": spice,
        "spicy": spice >= 4,
        "delivery_time_minutes": delivery,
        "portion_size": portion,
        "location": location,
        "category": category,
        "tags": tags,
        "popularity_score": popularity,
        "popularity": popularity,
        "average_rating": average,
        "quality_score": average,
    }
    return {"item_id": item_id, "name": name, "category": category, "price": price, "metadata": metadata}


def score_review(user: dict, item: dict) -> int:
    positive_terms = USER_POSITIVES.get(user["user_id"], set())
    text = f"{item['name']} {' '.join(item['metadata']['tags'])}".lower()
    overlap = sum(1 for term in positive_terms if term in text)
    rating = 3.2 + STYLE_BIAS[user["rating_style"]] + min(overlap, 4) * 0.35

    description = user["description"].lower()
    price = item["price"]
    spice = item["metadata"]["spice_level"]
    delivery = item["metadata"]["delivery_time_minutes"]
    portion = item["metadata"]["portion_size"]

    if any(term in description for term in ["budget", "price-sensitive", "affordable", "student", "nysc"]) and price <= 3500:
        rating += 0.45
    if any(term in description for term in ["budget", "price-sensitive", "affordable", "student", "nysc"]) and price >= 9000:
        rating -= 0.85
    if any(term in description for term in ["quick", "delivery-sensitive", "fast", "late", "delay"]) and delivery and delivery <= 35:
        rating += 0.4
    if any(term in description for term in ["quick", "delivery-sensitive", "fast", "late", "delay"]) and delivery >= 60:
        rating -= 0.75
    if any(term in description for term in ["spice lover", "peppery", "spicy"]) and spice >= 4:
        rating += 0.45
    if "not too much pepper" in description and spice >= 4:
        rating -= 0.6
    if any(term in description for term in ["family", "sharing", "portions"]) and portion in {"large", "family", "sharing"}:
        rating += 0.45
    if any(term in description for term in ["health", "low sugar", "protein"]) and any(tag in item["metadata"]["tags"] for tag in ["healthy", "protein", "low sugar"]):
        rating += 0.65
    if any(term in description for term in ["book", "movie"]) and item["category"] in {"Book", "Movie"}:
        rating += 0.75
    if any(term in description for term in ["durable", "electronics", "product"]) and item["category"] == "Product":
        rating += 0.5

    return max(1, min(5, int(round(rating))))


def review_text(user: dict, item: dict, rating: int) -> str:
    tags = item["metadata"]["tags"]
    delivery = item["metadata"]["delivery_time_minutes"]
    portion = item["metadata"]["portion_size"]
    price = item["price"]
    name = item["name"]
    if rating >= 5:
        return f"{name} really matched my taste. The {tags[0]} angle worked, portion was {portion}, and the price felt fair for the experience."
    if rating == 4:
        delivery_note = "delivery was smooth" if not delivery or delivery <= 40 else "delivery could still be faster"
        return f"{name} was a good pick. I liked the {tags[0]} feel and {delivery_note}, though there is still small room to improve."
    if rating == 3:
        return f"{name} was okay, not bad but not outstanding. The price around NGN {price:,} needs to match the portion and freshness better."
    if rating == 2:
        return f"{name} did not fully work for me. Delivery, portion, or value felt off, so I expected more for the money."
    return f"{name} was disappointing. The experience did not justify the price and I would choose another option next time."


def main() -> None:
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    items = [build_item(row) for row in ITEMS]
    reviews = []
    review_id = 1
    active_users = [user for user in USERS if not user["cold_start"]]
    for user_index, user in enumerate(active_users):
        for offset in range(10):
            item = items[(user_index * 7 + offset * 5) % len(items)]
            rating = score_review(user, item)
            reviews.append(
                {
                    "review_id": f"review_{review_id:03d}",
                    "user_id": user["user_id"],
                    "item_id": item["item_id"],
                    "rating": rating,
                    "review": review_text(user, item, rating),
                }
            )
            review_id += 1

    SAMPLE_DIR.joinpath("users.json").write_text(json.dumps(USERS, indent=2), encoding="utf-8")
    SAMPLE_DIR.joinpath("items.json").write_text(json.dumps(items, indent=2), encoding="utf-8")
    SAMPLE_DIR.joinpath("reviews.json").write_text(json.dumps(reviews, indent=2), encoding="utf-8")
    print(f"Wrote Phase 2 sample data: {len(USERS)} users, {len(items)} items, {len(reviews)} reviews.")


if __name__ == "__main__":
    main()
