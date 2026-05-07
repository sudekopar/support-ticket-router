import json
import os

class SupportTicketRouter:
    def __init__(self):
        self.category_rules = {
            "billing": ["payment", "paid", "card", "invoice", "refund", "money", "fee", "charge"],
            "account": ["login", "password", "account", "access", "sign in", "profile"],
            "technical": ["crash", "bug", "error", "upload", "broken", "not working", "slow", "api"]
        }

        self.team_mapping = {
            "billing": "payments-team",
            "account": "account-support",
            "technical": "technical-support",
            "general": "general-support"
        }

        self.critical_keywords = [
            "outage", "hacked", "breach", "security", "database down", 
            "server error", "unauthorized", "compromised", "data loss", 
            "leaked", "vulnerability", "ddos"
        ]

        self.urgent_keywords = ["urgent", "asap", "immediately", "cannot use", "blocked", "critical"]

    def identify_category(self, text):
        text = text.lower()
        for category, keywords in self.category_rules.items():
            if any(word in text for word in keywords):
                return category
        return "general"

    def calculate_priority(self, ticket, category):
        subject = ticket.get("subject", "").lower()
        message = ticket.get("message", "").lower()
        full_text = f"{subject} {message}"
        customer_type = ticket.get("customerType", "").lower()

        is_premium = (customer_type == "premium")
        is_urgent_msg = any(word in full_text for word in self.urgent_keywords)
        is_special_technical = any(word in full_text for word in self.critical_keywords)
        is_critical_billing = (category == "billing" and any(word in full_text for word in ["money", "refund", "withdrawn"]))

        if is_premium or is_urgent_msg or is_special_technical or is_critical_billing:
            reasons = []
            if is_premium: reasons.append("Premium Customer")
            if is_urgent_msg: reasons.append("Urgent Keyword Detected")
            if is_special_technical: reasons.append("Critical Technical/Security Issue")
            if is_critical_billing: reasons.append("Financial Dispute")
            return "high", f"High priority assigned due to: {', '.join(reasons)}."
        elif category in ["technical", "account"]:
            return "medium", f"Standard {category} related inquiry."
        else:
            return "low", "General inquiry with no priority triggers."

    def run(self, input_path, output_path):
        if not os.path.exists(input_path):
            print(f"Hata: '{input_path}' dosyası bulunamadı!")
            return

        with open(input_path, 'r', encoding='utf-8') as f:
            try:
                tickets = json.load(f)
            except json.JSONDecodeError:
                print("Hata: JSON dosyası geçersiz formatta!")
                return

        processed_data = []
        print("\n--- BILET ISLEME BASLADI ---\n")
        
        for t in tickets:
            category = self.identify_category(f"{t.get('subject','')} {t.get('message','')}")
            priority, reason = self.calculate_priority(t, category)
            assigned_team = self.team_mapping.get(category, "general-support")

            result = {
                "id": t.get("id"),
                "category": category,
                "priority": priority,
                "assignedTeam": assigned_team,
                "reason": reason
            }
            
            processed_data.append(result)

            
            print(json.dumps(result, indent=4, ensure_ascii=False))
            print("-" * 40) 

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=4, ensure_ascii=False)
        
        return processed_data

if __name__ == "__main__":
    router = SupportTicketRouter()
    results = router.run('input.json', 'output.json')
    
    if results:
        print(f"\nISLEM TAMAMLANDI!")
        print(f"Toplam {len(results)} bilet islendi ve 'output.json' dosyasina kaydedildi.")
