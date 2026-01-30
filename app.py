def prettify_output(text: str) -> str:
    text = text.replace("**", "").strip()

    # ---------- FOOD ITEMS ----------
    food_items = []
    seen = set()

    if "FOOD ITEMS:" in text:
        _, rest = text.split("FOOD ITEMS:", 1)
        for line in rest.splitlines():
            line = line.strip()
            if not line or "TOTAL CALORIES" in line.upper():
                break
            clean = line.lstrip("•-0123456789. ").strip()
            key = clean.lower()
            if clean and key not in seen:
                seen.add(key)
                food_items.append(clean)

    food_block = ""
    if food_items:
        food_block = "FOOD ITEMS:\n" + "\n".join(
            f"{i+1}. {item}" for i, item in enumerate(food_items)
        )

    # ---------- TOTAL CALORIES ----------
    calories_match = re.search(
        r"TOTAL CALORIES:\s*([~]?\d+[,\d]*)",
        text,
        flags=re.IGNORECASE
    )

    calories_block = ""
    if calories_match:
        calories_block = f"🔥 TOTAL CALORIES: {calories_match.group(1)} calories"

    # ---------- HEALTH TIPS ----------
    tips = []
    if "HEALTH TIPS" in text:
        tips_text = text.split("HEALTH TIPS", 1)[1]
        tips_text = tips_text.replace(":", "").strip()

        raw = re.split(r"(?:🥗|•|Tip\s*\d+)", tips_text, flags=re.IGNORECASE)
        tips = [t.strip() for t in raw if len(t.strip()) > 10]

    if not tips:
        tips = [
            "Watch portion sizes to avoid excess calorie intake.",
            "Balance meals with vegetables and protein for better nutrition."
        ]

    tips_block = "HEALTH TIPS:\n" + "\n".join(f"🥗 {tip}" for tip in tips)

    return "\n\n".join(
        part for part in [food_block, calories_block, tips_block] if part
    )
