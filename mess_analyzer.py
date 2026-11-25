import csv
import os
from datetime import date, datetime, timedelta

MENU_FILE = "menu.csv"
FEEDBACK_FILE = "feedback.csv"
REPORT_FILE = "report.txt"

MEALS = ["Breakfast", "Lunch", "Dinner"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

DROP_BELOW = 2.5
MODIFY_BELOW = 3.5
MIN_RATINGS = 3
MAX_REPEATS = 2

FIXES = {"salty": "reduce salt", "oily": "use less oil", "cold": "serve hot",
         "stale": "use fresh ingredients", "bland": "improve seasoning",
         "raw": "cook thoroughly", "spicy": "reduce spice level"}

def parse_date(text):
    for fmt in ["%Y-%m-%d", "%d-%m-%Y"]:
        try:
            return datetime.strptime(text.strip(), fmt).date()
        except ValueError:
            pass
    return None

def load_menu():
    menu = {}
    if not os.path.exists(MENU_FILE):
        return menu
    with open(MENU_FILE, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            menu[(row["day"], row["meal"])] = row["dish"]
    return menu

def load_feedback():
    feedback = []
    if not os.path.exists(FEEDBACK_FILE):
        return feedback
    with open(FEEDBACK_FILE, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if not row["rating"] or not row["rating"].isdigit():
                continue
            row_date = parse_date(row["date"])
            rating = int(row["rating"])
            if row_date is None or rating < 1 or rating > 5:
                continue
            row["date"] = row_date
            row["rating"] = rating
            row["review"] = row["review"].lower()
            feedback.append(row)
    return feedback

def save_feedback(row):
    is_new = not os.path.exists(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["date", "student_id", "meal", "dish", "rating", "review"])
        writer.writerow(row)

def read_int(prompt, low, high):
    while True:
        try:
            value = int(input(prompt))
        except ValueError:
            print("  Please enter a whole number.")
            continue
        if low <= value <= high:
            return value
        print(f"  Please enter a number between {low} and {high}.")

def read_date(prompt):
    while True:
        text = input(prompt).strip()
        if text == "":
            return date.today()
        d = parse_date(text)
        if d is None:
            print("  Invalid date. Use YYYY-MM-DD or press Enter for today.")
        elif d > date.today():
            print("  Feedback cannot be given for a future date.")
        else:
            return d

def submit_feedback(menu):
    print("\n--- Submit Feedback ---")
    student_id = input("Student ID / Roll No: ").strip().upper()
    if student_id == "":
        print("  Student ID cannot be empty.")
        return

    d = read_date("Date (YYYY-MM-DD, Enter = today): ")
    day = DAYS[d.weekday()]

    for i in range(3):
        print(f"  {i + 1}. {MEALS[i]}: {menu.get((day, MEALS[i]), 'not in menu')}")
    meal = MEALS[read_int("Choose meal (1-3): ", 1, 3) - 1]

    if (day, meal) not in menu:
        print("  No dish is listed for that meal in menu.csv.")
        return
    dish = menu[(day, meal)]

    rating = read_int(f"Rate '{dish}' (1-5): ", 1, 5)
    review = input("Short review (optional): ").strip()

    save_feedback([d.isoformat(), student_id, meal, dish, rating, review])
    print("  Thank you! Feedback saved.")

def filter_period(feedback, days):
    if not feedback:
        return []
    newest = feedback[0]["date"]
    for row in feedback:
        if row["date"] > newest:
            newest = row["date"]
    start = newest - timedelta(days=days - 1)

    result = []
    for row in feedback:
        if start <= row["date"] <= newest:
            result.append(row)
    return result

def dish_statistics(rows):
    stats = {}
    for row in rows:
        dish = row["dish"]
        if dish not in stats:
            stats[dish] = {"ratings": [], "reviews": [], "meals": []}
        stats[dish]["ratings"].append(row["rating"])
        stats[dish]["reviews"].append(row["review"])
        if row["meal"] not in stats[dish]["meals"]:
            stats[dish]["meals"].append(row["meal"])

    for dish in stats:
        s = stats[dish]
        s["count"] = len(s["ratings"])
        s["avg"] = sum(s["ratings"]) / s["count"]
        ordered = []
        for meal in MEALS:
            if meal in s["meals"]:
                ordered.append(meal)
        s["meal"] = "/".join(ordered)
    return stats

def meal_average(rows, meal):
    ratings = []
    for row in rows:
        if row["meal"] == meal:
            ratings.append(row["rating"])
    if not ratings:
        return 0.0
    return sum(ratings) / len(ratings)

def find_fixes(reviews):
    fixes = []
    for text in reviews:
        for word in FIXES:
            if word in text and FIXES[word] not in fixes:
                fixes.append(FIXES[word])
    fixes.sort()
    return fixes

def recommend(stats, menu):
    served = list(menu.values())
    groups = {"DROP": [], "MODIFY": [], "KEEP (VARY)": [], "KEEP": [], "NOT ENOUGH DATA": []}

    for dish, s in stats.items():
        avg = s["avg"]
        if s["count"] < MIN_RATINGS:
            action = "NOT ENOUGH DATA"
            reason = f"only {s['count']} rating(s); need {MIN_RATINGS}"
        elif avg < DROP_BELOW:
            action = "DROP"
            reason = "avg below 2.5"
        elif avg < MODIFY_BELOW:
            action = "MODIFY"
            reason = "avg 2.5-3.5"
            fixes = find_fixes(s["reviews"])
            if fixes:
                reason += "; " + ", ".join(fixes)
        else:
            action = "KEEP"
            reason = "well liked"

        times = served.count(dish)
        if times > MAX_REPEATS and action in ("MODIFY", "KEEP"):
            reason += f"; served {times}x/week, vary"
            if action == "KEEP":
                action = "KEEP (VARY)"

        groups[action].append((avg, dish, action, reason))

    result = []
    for action in groups:
        groups[action].sort()
        result += groups[action]
    return result

def build_report(feedback, menu):
    if not feedback:
        return "No feedback data available."

    line = "=" * 74
    lines = []
    for label, days in [("WEEKLY (last 7 days)", 7), ("MONTHLY (last 30 days)", 30)]:
        rows = filter_period(feedback, days)
        stats = dish_statistics(rows)

        ranked = []
        for dish in stats:
            if stats[dish]["count"] >= MIN_RATINGS:
                ranked.append((stats[dish]["avg"], dish))
        ranked.sort(reverse=True)

        lines += [line, f"{label}  |  {len(rows)} responses", line]
        for meal in MEALS:
            lines.append(f"  {meal:<10} average rating: {meal_average(rows, meal):.2f}")
        if ranked:
            lines.append(f"  Highest rated : {ranked[0][1]} ({ranked[0][0]:.2f})")
            lines.append(f"  Lowest rated  : {ranked[-1][1]} ({ranked[-1][0]:.2f})")

        lines += ["", f"  {'Dish':<24}{'Meal(s)':<22}{'Avg':>5}{'N':>4}"]
        for avg, dish in ranked:
            lines.append(f"  {dish:<24}{stats[dish]['meal']:<22}{avg:>5.2f}{stats[dish]['count']:>4}")
        lines.append("")

    lines += [line, "RECOMMENDATIONS FOR NEXT WEEKLY MENU (based on monthly data)", line]
    stats = dish_statistics(filter_period(feedback, 30))
    for avg, dish, action, reason in recommend(stats, menu):
        lines.append(f"  [{action:<15}] {dish:<22} {avg:.2f}  {reason}")
    return "\n".join(lines)

def generate_report(menu):
    report = build_report(load_feedback(), menu)
    print("\n" + report)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"\nReport saved to {REPORT_FILE}")

def view_menu(menu):
    print("\n--- Weekly Menu ---")
    for day in DAYS:
        parts = []
        for meal in MEALS:
            parts.append(f"{meal[0]}: {menu.get((day, meal))}")
        print(f"  {day:<10} " + " | ".join(parts))

def main():
    menu = load_menu()
    if not menu:
        print("menu.csv not found or empty. Please add it first.")
        return

    while True:
        print("\n===== HOSTEL MESS FEEDBACK ANALYZER =====")
        print("1. Submit feedback")
        print("2. View weekly menu")
        print("3. Generate analysis report")
        print("4. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            submit_feedback(menu)
        elif choice == "2":
            view_menu(menu)
        elif choice == "3":
            generate_report(menu)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice. Enter 1-4.")

if __name__ == "__main__":
    main()
