"""Site-level constants for the marketing shell around the app.

Every value below that points at an external identity (a repo, a contact channel, an
institutional affiliation) is either taken from a file already in this repository or
left as an explicit placeholder. None of it is invented: a wrong GitHub link or a
false program affiliation is worse than an honest "not set yet" state.
"""

from __future__ import annotations

#: Taken from `git remote get-url origin`.
GITHUB_REPOSITORY_URL: str | None = "https://github.com/zyn-llc/colories_detector"

#: Set to a t.me/... URL to show the Telegram button in the contact section.
TELEGRAM_CONTACT_URL: str | None = None

CREATOR_NAME: str = "Zayniddin"

#: The programs section stays hidden until a real affiliation is confirmed.
SHOW_PROGRAMS_SECTION: bool = False

AFFILIATED_PROGRAMS: list[dict[str, str]] = []
