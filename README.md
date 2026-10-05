# loopbreaker [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Stall detection for any agent loop.**

## The pain

Every agent builder has the trauma story: an agent burned **$40 doing nothing for 3 hours** — retrying a dead task, calling a broken API, re-running a failed download, making zero progress the whole time. Nobody noticed until the bill arrived. Agent loops don't fail loudly; they fail *expensively and quietly*.

loopbreaker is the watchdog that notices "no progress" and escalates instead of letting the loop spin forever.

## 5-line integration

```python
from loopbreaker import StallWatcher

watcher = StallWatcher()  # stall_ticks=20 by default

for task in agent_loop():
    result = watcher.observe(task.action, score_progress(task))  # 0..4 rubric
    if result == "nudge":
        propose_new_tactic()          # agent: try something different
    elif result == "escalate":
        page_human_or_stop_gracefully()
```

Drop it into **any** loop — LangChain, CrewAI, AutoGPT, a raw `while True`, your homegrown orchestrator. It has zero dependencies and knows nothing about your framework.

## How detection works

1. **Best-progress tracking.** Every tick, the watcher records the best progress score (0..4 rubric, higher = closer to done) it has ever seen.
2. **Flat-streak windows.** Consecutive observations with *no improvement* (`progress <= best`) count toward a flat streak. Strictly better progress resets the streak.
3. **Nudge, then escalate.** When the flat streak reaches `stall_ticks` (default 20), you get `"nudge"` **once** — the agent should propose a new tactic. If the streak continues for another full window with still no improvement, you get `"escalate"` — ping a human or stop gracefully. Any real improvement re-arms both.

Equal scores don't count as progress. "Trying the same thing again" is exactly the failure mode this exists to catch.

## Jaw-drop demo

Watch the watcher kill a stuck agent in under a second:

```bash
python examples/spin_demo.py
```

It simulates an agent retrying `fetch_invoice_pdf` 60 times with flat progress: the nudge fires at step 20, the escalation at step 40, and the punchline shows what the bill would have been without the watcher.

## License

MIT. See [LICENSE](LICENSE).
