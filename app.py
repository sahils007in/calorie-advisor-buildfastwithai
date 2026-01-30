import re

def normalize_food_items(text: str) -> str:
    """
    Ensures FOOD ITEMS are numbered consistently.
    """
    if "FOOD ITEMS:" not in text:
        return text

    before, rest = text.split("FOOD ITEMS:", 1)

    lines = rest.strip().splitlines()
    items = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("TOTAL CALORIES"):
            break
        # Remove existing numbering or bullets
        clean = re.sub(r"^[\-\•\d\.\)\s]+", "", line)
        if len(clean) > 3:
            items.append(clean)

    numbered = "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

    remaining = rest.split(lines[len(items)-1], 1)[-1]

    return f"{before.strip()}\n\nFOOD ITEMS:\n{numbered}\n{remaining.strip()}"


def format_health_tips(text: str, emoji: bool = True) -> str:
    """
    Formats HEALTH TIPS into clean bullet points.
    """
    if "HEALTH TIPS" not in text:
        return text

    before, tips = text.split("HEALTH TIPS", 1)
    tips = tips.replace(":", "").strip()

    raw_tips = (
        tips.replace("•", "\n")
            .replace("-", "\n")
            .split("\n")
    )

    clean_tips = [
        tip.strip()
        for tip in raw_tips
        if len(tip.strip()) > 5
    ]

    bullet = "🥗 " if emoji else "• "

    formatted = "\n".join([f"{bullet}{tip}" for tip in clean_tips])

    return f"{before.strip()}\n\nHEALTH TIPS:\n{formatted}"


def highlight_total_calories(text: str) -> str:
    """
    Highlights TOTAL CALORIES section.
    """
    return re.sub(
        r"(TOTAL CALORIES:\s*[~]?\d+[\–\-]?\d*\s*calories?)",
        r"### 🔥 \1",
        text,
        flags=re.IGNORECASE
    )


def prettify_output(text: str) -> str:
    """
    Master formatter to apply all formatting consistently.
    """
    text = normalize_food_items(text)
    text = format_health_tips(text, emoji=True)
    text = highlight_total_calories(text)
    return text.strip()
