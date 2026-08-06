"""Generate synthetic test transcripts for evaluation."""
from pathlib import Path

TRANSCRIPTS = {
    "all_hands_01.txt": """[00:00:15] CEO John: Good morning everyone. Let's start with engineering updates.
[00:00:30] CTO Maria: We're on track with Q3 deliverables. I need to mention — the API performance issues from last week are resolved.
[00:01:00] John: Great. What about the mobile launch?
[00:01:10] Maria: I'll get the mobile team to prepare a launch readiness report by this Friday.
[00:01:25] PM David: I can have the release notes drafted by Thursday. Also, I'll coordinate with marketing on the press release by Wednesday.
[00:01:45] QA Lead Sara: We have 12 open P1 bugs. I'll assign all P1 bugs to the team by end of today and get them resolved before the release.
[00:02:10] John: Perfect. Any blockers?
[00:02:20] Maria: We're waiting on the security audit results. Without that, we can't go to production.
[00:02:35] John: I'll escalate to the security team and get the audit results by next Tuesday.
[00:02:50] David: One more thing — we decided last month to deprecate the v1 API. I'll send the deprecation notice to all customers by next Monday.
[00:03:05] John: Good. Let's make the mobile launch our top priority this week.
""",

    "retrospective_01.txt": """[00:00:10] Scrum Master Leo: Let's start with what went well.
[00:00:20] Dev Ana: The new deployment process worked great. Zero downtime this sprint.
[00:00:35] Dev Vikram: Code reviews were faster. Good improvement.
[00:00:50] Leo: Now, what didn't go well?
[00:01:00] Ana: We had too many meetings interrupting dev time.
[00:01:15] Vikram: Tech debt is piling up. We keep deferring it.
[00:01:30] Leo: What actions can we take?
[00:01:40] Ana: I'll create a tech debt board in Jira by next Monday so we can track it properly.
[00:01:55] Vikram: I can take the first 2 tech debt items and resolve them this sprint.
[00:02:10] Leo: Good. Can we reduce meetings?
[00:02:20] Ana: I'll propose a new meeting schedule to the team by Wednesday. We should cap standups at 10 minutes.
[00:02:40] Leo: We've decided to adopt a "no meeting Wednesday" policy starting next sprint.
[00:02:55] Vikram: I'll update the team calendar to block Wednesdays by tomorrow.
""",
}


def generate():
    output_dir = Path(__file__).parent.parent / "backend/tests/eval/test_cases"
    output_dir.mkdir(parents=True, exist_ok=True)

    for filename, content in TRANSCRIPTS.items():
        path = output_dir / filename
        path.write_text(content)
        print(f"Generated: {path}")

    print(f"\n✅ {len(TRANSCRIPTS)} test transcripts generated in {output_dir}")


if __name__ == "__main__":
    generate()
