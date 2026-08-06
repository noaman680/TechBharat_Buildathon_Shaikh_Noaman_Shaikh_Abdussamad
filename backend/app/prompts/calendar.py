CALENDAR_PROMPT = """
Convert the following natural language date expression to an exact calendar date.

Context:
- Meeting date: {meeting_date}
- Timezone: {timezone}
- Organization calendar context: {calendar_context}

Date expression: "{date_raw}"

Rules:
- "tomorrow" -> next day after meeting date
- "next Friday" -> the upcoming Friday after meeting date
- "end of quarter" -> last day of current quarter
- "next sprint" -> calculate based on sprint cadence if known
- "before Diwali" -> day before Diwali in the relevant year
- "ASAP" -> set priority=high, due_date=3 business days from meeting
- "EOD" -> end of day on meeting date

Return JSON: {{ "resolved_date": "YYYY-MM-DD", "confidence": 0.0-1.0, "reasoning": "..." }}
"""
