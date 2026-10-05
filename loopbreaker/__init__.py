"""loopbreaker — stall detection for any agent loop.

One class: :class:`StallWatcher`. Feed it an action name and a progress score
(0..4 rubric, higher = closer to done) on every loop tick. It tells you
"ok", "nudge" (agent should propose a new tactic), or "escalate" (ping a
human / stop gracefully) — so agents never burn money spinning in place.
"""

from loopbreaker.watch import StallWatcher

__version__ = "0.1.0"
__all__ = ["StallWatcher", "__version__"]
