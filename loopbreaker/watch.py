"""Stall detection for any agent loop. Stdlib only, framework-agnostic."""

from __future__ import annotations


class StallWatcher:
    """Watch an agent loop and fire when progress stalls.

    Feed every loop tick to :meth:`observe` with a short ``action`` label and
    a ``progress`` score on a 0..4 rubric (higher = closer to done). The
    watcher tracks the best progress ever seen and counts consecutive
    observations with *no improvement* (``progress <= best``).

    - When the flat-streak reaches exactly ``stall_ticks`` -> return
      ``"nudge"`` **once**: the agent should propose a new tactic.
    - If the streak continues for another full ``stall_ticks`` window with
      still no improvement -> return ``"escalate"``: ping a human or stop
      gracefully instead of spinning forever.
    - Otherwise return ``"ok"``.
    - Any observation with ``progress`` strictly greater than the best seen
      resets the streak (re-arming nudge and escalate) and records the new
      best.

    Equal scores don't count as progress: only *strictly* better scores move
    the bar, because "trying the same thing again" is exactly the failure
    mode this exists to catch.
    """

    def __init__(self, stall_ticks: int = 20) -> None:
        if stall_ticks < 1:
            raise ValueError("stall_ticks must be >= 1")
        self.stall_ticks = stall_ticks
        self.reset()

    def reset(self) -> None:
        """Clear all state: forget the best progress and restart the streak."""
        self._best: float | None = None  # best progress score seen so far
        self.flat_streak: int = 0  # consecutive observations with no improvement
        self._nudged: bool = False  # True once "nudge" has been returned

    def observe(self, action: str, progress: float) -> str:
        """Record one loop tick. Returns "ok" | "nudge" | "escalate".

        ``action`` is a free-form label (e.g. "fetch_invoice_pdf") used for
        debugging, not for scoring. ``progress`` is a 0..4 rubric score where
        higher means closer to done.
        """
        # Improvement: strictly above the best we've ever seen. Reset the
        # flat streak and re-arm the nudge/escalate cycle.
        if self._best is None or progress > self._best:
            self._best = progress
            self.flat_streak = 0
            self._nudged = False
            return "ok"

        # No improvement: progress is flat (or regressed). Count the streak.
        self.flat_streak += 1

        # First full window of flatness -> tell the agent to try a new tactic.
        # Fire exactly once per arming cycle.
        if not self._nudged and self.flat_streak >= self.stall_ticks:
            self._nudged = True
            return "nudge"

        # A second full window with still no improvement -> stop and escalate.
        if self._nudged and self.flat_streak >= 2 * self.stall_ticks:
            return "escalate"

        return "ok"
