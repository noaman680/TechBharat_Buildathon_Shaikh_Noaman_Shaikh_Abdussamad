"""
Data-access layer facade.

Agent code throughout this repo calls things like `db.meetings.find_by_hash(...)`
or `db.approvals.get(...)`. This module exposes those repository objects.

TODO before running for real: replace `_StubRepository` with actual
repository classes backed by an async SQLAlchemy session (see
app/db/repositories/ and the schema in app/db/schema.sql /
docs/BLUEPRINT.md #8). Each repository method below documents the query
it needs to perform.
"""


class _StubRepository:
    """Raises on first real use, but doesn't break imports at collection time."""

    def __init__(self, name: str):
        self._name = name

    def __getattr__(self, method_name: str):
        async def _unimplemented(*args, **kwargs):
            raise NotImplementedError(
                f"db.{self._name}.{method_name}() is not implemented yet -- "
                f"wire this up in app/db/repositories/{self._name}.py"
            )
        return _unimplemented


class _DB:
    meetings = _StubRepository("meetings")
    approvals = _StubRepository("approvals")
    action_items = _StubRepository("action_items")
    audit_logs = _StubRepository("audit_logs")
    integrations = _StubRepository("integrations")
    org_directory = _StubRepository("org_directory")


db = _DB()
