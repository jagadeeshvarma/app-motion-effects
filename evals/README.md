# Reproducible motion/UI evaluation corpus

Twelve local scenarios cover small web and Flutter motion tasks, preserved state/conventions, accessibility, honest API feedback, security, scope, tool absence, instruction trust and lifecycle checks. There are six development cases (A–F) and six validation cases (G–L). Validation task descriptions were exposed during harness inspection, so they must not be reported as untouched held out. The record is explicit in `scenarios.json` and `DESIGN.md`.

Acceptance criteria were established before instruction edits. The final fixture corpus and assertions were frozen before comparative runs, after instruction edits had begun; the independent task author did not inspect the improved candidate. This corrects the earlier stronger pre-edit freeze claim (MA04), without changing tasks, assertions or thresholds. Run `python3 evals/tools/validate.py` from the repository root to verify schema and hashes. Read [DESIGN.md](DESIGN.md) before running experiments. No model tasks are run by corpus preparation or validation.

```sh
python3 evals/run.py --cases A --conditions no-skill --output /path/to/new-private-run --dry-run
python3 evals/regrade.py --results /path/to/retained-results --output /path/to/new-private-regrades
```

The guarded runner is the supported entrypoint. GA01 trusted-input verification and GA02 containment are always enabled; there is no unsafe bypass. Direct frozen `grade.py` frontdoors are quarantined and return BLOCKED. Their exact original assertion bytes remain authenticated historical archive data, described in [GA03](GRADING_AMENDMENT_GA03.md). Native execution remains held pending its separate strict grading prerequisites.

Only the selected fixture and task go into an evaluated context. Keep graders, other tasks and condition labels hidden. Use the same model/tools/time limits in no-skill, original-v2 and improved conditions. Never fix an evaluated output before grading it.

Grader JSON includes `scenario`, `status`, `checks`, `blockers`, `manual_required`, and `limitations`. Exit codes: 0 automated pass, 1 output fail, 2 infrastructure blocked. Automated acceptance does not replace the frozen manual fit/playback rubric. Optional transcript/prior-workspace arguments support evidence honesty and lifecycle checks.

Web fixtures run by static serving. Browser grading uses the repository's existing Playwright development package and installed Chrome by default; set `MOTION_BROWSER_CHANNEL` consistently to use another installed Playwright channel. Native fixtures use Flutter SDK/flutter_test with resolved lock files and offline dependencies. Native device/simulator launch requires disposable platform-shell generation, described in DESIGN.md.
