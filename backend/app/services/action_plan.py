import json
from app.config import get_settings
from app.services.data_brokers import KNOWN_BROKERS


class ActionPlanService:
    """Generate prioritized action plan from scan results. Uses OpenAI if key set, else rule-based."""

    def __init__(self):
        self.settings = get_settings()

    async def generate(
        self,
        email_or_username: str,
        breaches: list[dict],
        pastes: list[dict],
        broker_count: int,
    ) -> dict:
        if self.settings.openai_api_key:
            return await self._generate_with_openai(
                email_or_username, breaches, pastes, broker_count
            )
        return self._generate_rule_based(breaches, pastes, broker_count)

    async def _generate_with_openai(
        self,
        email_or_username: str,
        breaches: list[dict],
        pastes: list[dict],
        broker_count: int,
    ) -> dict:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=self.settings.openai_api_key)
            prompt = self._build_prompt(email_or_username, breaches, pastes, broker_count)
            r = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a privacy and security advisor. Output valid JSON only.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )
            text = r.choices[0].message.content or "{}"
            # Strip markdown code block if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception:
            return self._generate_rule_based(breaches, pastes, broker_count)

    def _build_prompt(
        self,
        email_or_username: str,
        breaches: list[dict],
        pastes: list[dict],
        broker_count: int,
    ) -> str:
        return f"""Based on this exposure scan, produce a prioritized action plan as JSON.

Account: {email_or_username}
Breaches: {len(breaches)} — {[b.get('Name', b) for b in breaches]}
Pastes: {len(pastes)}
Data brokers to consider opt-out: {broker_count}

Respond with exactly this JSON structure (no other text):
{{
  "summary": "One sentence overall risk summary",
  "actions": [
    {{ "title": "string", "category": "opt_out|password_change|delete_account|monitor|other", "priority": 1, "link_or_instruction": "string or null" }}
  ]
}}
Priority: 1 = high, 2 = medium, 3 = low. Include 3-8 actions. Use real opt-out links where relevant."""

    def _generate_rule_based(
        self,
        breaches: list[dict],
        pastes: list[dict],
        broker_count: int,
    ) -> dict:
        actions = []
        if breaches:
            actions.append({
                "title": "Change passwords for breached sites",
                "category": "password_change",
                "priority": 1,
                "link_or_instruction": "Change password on any site where this email was breached. Use unique passwords per site.",
            })
            for b in breaches[:3]:
                name = b.get("Name", "Unknown")
                actions.append({
                    "title": f"Review account on {name}",
                    "category": "delete_account",
                    "priority": 2,
                    "link_or_instruction": f"Consider deleting or securing the account associated with the breach: {name}",
                })
        if pastes:
            actions.append({
                "title": "Check pasted data and secure accounts",
                "category": "monitor",
                "priority": 1,
                "link_or_instruction": "Your email appeared in pastes. Enable 2FA and monitor for phishing.",
            })
        if broker_count:
            actions.append({
                "title": "Opt out of data broker sites",
                "category": "opt_out",
                "priority": 2,
                "link_or_instruction": f"Visit each of the {broker_count} known data broker opt-out pages and submit removal requests.",
            })
        if not actions:
            actions.append({
                "title": "No high-priority exposures found",
                "category": "other",
                "priority": 3,
                "link_or_instruction": "Keep monitoring periodically with DataShadow.",
            })
        return {
            "summary": f"Found {len(breaches)} breaches, {len(pastes)} pastes, and {broker_count} data brokers. Follow the actions below.",
            "actions": actions,
        }
