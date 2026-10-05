"""The viral demo: an agent stuck retrying the same failing action.

Simulates 60 loop ticks where the agent keeps doing "fetch_invoice_pdf" and
making no progress (progress pinned at 1.0). The StallWatcher fires "nudge"
at step 20 and "escalate" at step 40 — without it, the loop would spin
forever and burn $40+ doing nothing.

Run it:  python examples/spin_demo.py
"""

import sys

sys.path.insert(0, ".")  # run from the repo root

from loopbreaker import StallWatcher

COST_PER_STEP = 0.02  # dollars: rough cost of one agent loop tick


def main() -> None:
    watcher = StallWatcher(stall_ticks=20)
    action = "fetch_invoice_pdf"  # the failing action, retried forever
    total_steps = 60

    watcher.observe(action, 1.0)  # sets the baseline best; the flat window starts after this

    for step in range(1, total_steps + 1):
        result = watcher.observe(action, 1.0)  # flat progress: no improvement
        if result != "ok":
            print(f"step {step:>3}: {result.upper():<9}  (flat streak: {watcher.flat_streak})")
            if result == "escalate":
                break

    wasted = 40
    print()
    print("=== punchline ===")
    print(f"Stopped after {wasted} wasted steps instead of spinning forever.")
    print(
        f"At ~${COST_PER_STEP:.2f}/step, that's the universal story: "
        f"~${wasted * COST_PER_STEP:.2f} burned doing nothing."
    )
    print("The nudge at step 20 asked for a new tactic. The agent ignored it.")
    print("The escalation at step 40 paged a human. Loop closed.")


if __name__ == "__main__":
    main()
