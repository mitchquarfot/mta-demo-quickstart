import re


def build_channel_filter(exclude_channels: str | None, col: str = "CHANNEL") -> str:
    if not exclude_channels:
        return ""
    channels = [re.sub(r"[^a-zA-Z0-9_]", "", c.strip()) for c in exclude_channels.split(",") if c.strip()]
    if not channels:
        return ""
    in_list = ",".join(f"'{c}'" for c in channels)
    return f"{col} NOT IN ({in_list})"


def build_date_filter(date_start: str | None, date_end: str | None, col: str) -> list[str]:
    clauses = []
    if date_start and re.match(r"^\d{4}-\d{2}-\d{2}$", date_start):
        clauses.append(f"{col} >= '{date_start}'")
    if date_end and re.match(r"^\d{4}-\d{2}-\d{2}$", date_end):
        clauses.append(f"{col} <= '{date_end}'")
    return clauses


def build_where(base: list[str], exclude_channels: str | None, date_start: str | None = None,
                date_end: str | None = None, channel_col: str = "CHANNEL", date_col: str | None = None) -> str:
    clauses = list(base)
    ch_filter = build_channel_filter(exclude_channels, channel_col)
    if ch_filter:
        clauses.append(ch_filter)
    if date_col:
        clauses.extend(build_date_filter(date_start, date_end, date_col))
    if not clauses:
        return ""
    return "WHERE " + " AND ".join(clauses)
