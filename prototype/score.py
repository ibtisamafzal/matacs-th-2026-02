"""Deterministic scoring and ranking from extracted facts.

No AI is used here. Same facts + same criteria = same ranking, every run.
Usage: python score.py [facts.json] [criteria.json]
"""
import json
import sys


def experience_fraction(installs):
    if installs is None:
        return 0.0
    if installs >= 11:
        return 1.0
    if installs >= 8:
        return 0.8
    if installs >= 5:
        return 0.6
    if installs >= 1:
        return 0.4
    return 0.0


def mandatory_failures(p):
    fails = []
    if p["licence_held"] is not True:
        fails.append("Ontario electrical licence not held by the bidder")
    if p["wsib"] is not True or p["insurance_5m"] is not True:
        fails.append("WSIB clearance or $5M insurance not confirmed")
    return fails


def flags(p, c):
    out = []
    if p["injection_suspected"]:
        out.append("hidden instruction aimed at automated reviewers (ignored)")
    if p["weeks"] is None:
        out.append("no completion timeline given, 16-week limit cannot be verified")
    elif p["weeks"] > c["max_weeks"]:
        out.append("timeline exceeds the limit")
    if p["price"] is None or p["price"] > c["budget_ceiling"]:
        out.append("price missing or over the budget ceiling")
    if p["low_confidence"]:
        out.append("low-confidence extraction: " + ", ".join(p["low_confidence"]))
    return out


def score(p, c, lowest_price, shortest_weeks):
    w = c["weights"]
    s = {}
    s["experience"] = w["experience"] * experience_fraction(p["installs"])
    s["price"] = w["price"] * lowest_price / p["price"]
    s["timeline"] = w["timeline"] * shortest_weeks / p["weeks"] if p["weeks"] else 0.0
    panel = min(p["panel_years"] / 25, 1)
    work = min(p["workmanship_years"] / 12, 1)
    s["warranty"] = w["warranty"] * (0.5 * panel + 0.5 * work)
    items = [p["named_lead"], p["crew_stated"], p["safety_plan"], p["monitoring_plan"]]
    s["team"] = w["team"] * sum(items) / 4
    return s


def run(facts, c):
    passed = [p for p in facts if not mandatory_failures(p)]
    lowest_price = min(p["price"] for p in passed)
    shortest = min(p["weeks"] for p in passed if p["weeks"])
    results = []
    for p in facts:
        fails = mandatory_failures(p)
        if fails:
            results.append({"proposal": p["proposal"], "status": "ineligible",
                            "rank": None, "score": None, "reason": "; ".join(fails)})
            continue
        parts = score(p, c, lowest_price, shortest)
        total = round(sum(parts.values()), 1)
        fl = flags(p, c)
        if fl:
            results.append({"proposal": p["proposal"], "status": "flagged", "rank": None,
                            "score": None,
                            "reason": "Held for review: " + "; ".join(fl)
                            + f" (provisional score {total})"})
        else:
            best = max(parts, key=parts.get)
            results.append({"proposal": p["proposal"], "status": "ranked", "rank": 0,
                            "score": total,
                            "reason": f"Passes mandatory checks; strongest on {best}.",
                            "_parts": {k: round(v, 2) for k, v in parts.items()}})
    ranked = sorted([r for r in results if r["status"] == "ranked"],
                    key=lambda r: (-r["score"], r["proposal"]))
    for i, r in enumerate(ranked, 1):
        r["rank"] = i
    order = {"ranked": 0, "flagged": 1, "ineligible": 2}
    results.sort(key=lambda r: (order[r["status"]], r["rank"] or 99, r["proposal"]))
    return results


if __name__ == "__main__":
    facts_path = sys.argv[1] if len(sys.argv) > 1 else "sample_facts.json"
    crit_path = sys.argv[2] if len(sys.argv) > 2 else "criteria.json"
    with open(facts_path) as f:
        facts = json.load(f)
    with open(crit_path) as f:
        crit = json.load(f)
    out = run(facts, crit)
    for r in out:
        if "_parts" in r:
            print(r["proposal"], r["score"], r["_parts"])
            del r["_parts"]
    print(json.dumps(out, indent=1))
