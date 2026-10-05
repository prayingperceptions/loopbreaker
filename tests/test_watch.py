"""Pytest suite for loopbreaker.StallWatcher."""

import pytest

from loopbreaker import StallWatcher, __version__


def test_version():
    assert __version__ == "0.1.0"


def test_climbing_progress_never_fires():
    """Strictly increasing progress never nudges or escalates."""
    watcher = StallWatcher(stall_ticks=5)
    for i in range(30):
        # Keep progress inside the 0..4 rubric while always increasing.
        assert watcher.observe(f"step_{i}", min(4.0, 0.1 * i + 0.1)) == "ok"


def test_flat_streak_nudges_at_exactly_stall_ticks():
    """'nudge' fires on the observation where flat_streak == stall_ticks."""
    watcher = StallWatcher(stall_ticks=5)
    watcher.observe("retry", 1.0)  # sets the initial best; streak stays 0
    results = [watcher.observe("retry", 1.0) for _ in range(5)]
    assert results == ["ok", "ok", "ok", "ok", "nudge"]
    assert watcher.flat_streak == 5


def test_nudge_fires_only_once():
    """'nudge' fires once per arming cycle, not every tick afterwards."""
    watcher = StallWatcher(stall_ticks=5)
    watcher.observe("retry", 1.0)  # sets the initial best
    results = [watcher.observe("retry", 1.0) for _ in range(7)]
    assert results.count("nudge") == 1


def test_escalate_after_second_flat_window():
    """Continued flatness triggers 'escalate' after a second full window."""
    watcher = StallWatcher(stall_ticks=5)
    watcher.observe("retry", 1.0)  # sets the initial best
    results = [watcher.observe("retry", 1.0) for _ in range(10)]
    assert results[-1] == "escalate"
    assert watcher.flat_streak == 10  # == 2 * stall_ticks


def test_progress_improvement_resets_and_rearms():
    """Strictly better progress resets the streak and re-arms nudge."""
    watcher = StallWatcher(stall_ticks=5)
    watcher.observe("retry", 1.0)  # sets the initial best
    for _ in range(5):
        watcher.observe("retry", 1.0)  # flat -> nudge fires at 5
    # Improvement resets everything.
    assert watcher.observe("retry", 2.0) == "ok"
    assert watcher.flat_streak == 0
    # The cycle re-arms: another flat window fires nudge again.
    results = [watcher.observe("retry", 2.0) for _ in range(5)]
    assert results[-1] == "nudge"


def test_equal_progress_does_not_count_as_improvement():
    """progress == best is still flat — only strictly-greater resets."""
    watcher = StallWatcher(stall_ticks=3)
    watcher.observe("retry", 1.0)
    assert watcher.observe("retry", 1.0) == "ok"
    assert watcher.flat_streak == 1


def test_ok_for_normal_observations():
    """Every tick before the stall threshold returns 'ok'."""
    watcher = StallWatcher(stall_ticks=20)
    watcher.observe("start", 0.5)
    assert watcher.observe("start", 0.5) == "ok"
    assert watcher.observe("start", 0.5) == "ok"
    assert watcher.flat_streak == 2


def test_reset_clears_state():
    watcher = StallWatcher(stall_ticks=3)
    watcher.observe("retry", 1.0)
    watcher.observe("retry", 1.0)
    watcher.reset()
    assert watcher.flat_streak == 0
    # After reset, a fresh best is recorded and the cycle starts over.
    assert watcher.observe("retry", 1.0) == "ok"


def test_invalid_stall_ticks_rejected():
    with pytest.raises(ValueError):
        StallWatcher(stall_ticks=0)
