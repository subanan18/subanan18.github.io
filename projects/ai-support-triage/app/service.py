from .models import Category, Priority, Ticket, TriageResult


class TriageEngine:
    CATEGORY_SIGNALS = {
        Category.BILLING: {"charged", "payment", "refund", "invoice", "billing", "card", "twice"},
        Category.TECHNICAL: {"error", "bug", "crash", "broken", "timeout", "api", "failed"},
        Category.ACCOUNT: {"login", "password", "account", "locked", "access", "verify", "verification"},
    }

    URGENT_SIGNALS = {"urgent", "asap", "immediately", "blocked", "cannot access", "charged twice"}

    def analyse(self, ticket: Ticket) -> TriageResult:
        text = f"{ticket.subject} {ticket.message}".lower()

        category_scores: dict[Category, int] = {}
        matched_signals: list[str] = []
        for category, signals in self.CATEGORY_SIGNALS.items():
            matches = [signal for signal in signals if signal in text]
            category_scores[category] = len(matches)
            matched_signals.extend(matches)

        category = max(category_scores, key=category_scores.get)
        if category_scores[category] == 0:
            category = Category.GENERAL

        urgent_matches = [signal for signal in self.URGENT_SIGNALS if signal in text]
        matched_signals.extend(urgent_matches)

        if "charged twice" in text or len(urgent_matches) >= 2:
            priority = Priority.CRITICAL
        elif urgent_matches:
            priority = Priority.HIGH
        elif category in {Category.BILLING, Category.ACCOUNT}:
            priority = Priority.MEDIUM
        else:
            priority = Priority.LOW

        category_score = category_scores.get(category, 0)
        confidence = min(0.55 + (category_score * 0.12) + (len(urgent_matches) * 0.08), 0.98)
        if category is Category.GENERAL:
            confidence = 0.5

        actions = {
            Priority.CRITICAL: "Escalate immediately to a specialist support queue",
            Priority.HIGH: "Prioritise for same-day human review",
            Priority.MEDIUM: "Route to the relevant support queue",
            Priority.LOW: "Handle through the standard support workflow",
        }

        return TriageResult(
            category=category,
            priority=priority,
            confidence=round(confidence, 2),
            signals=sorted(set(matched_signals)),
            suggested_action=actions[priority],
        )
