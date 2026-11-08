# Independent final web corpus review

All ten final candidate2 web outputs reach the frozen manual threshold of 10/12 with no zero dimensions. This **does not pass full corpus acceptance**: I retains its failed automated animation assertion, and native acceptance remains BLOCKED. No failed assertion is waived. Earlier five-item/390px reviews remain unchanged.

The review is independent, **not blinded**. The reviewer examined submitted source and incremental evidence notes, checked claims against supplied command-execution transcripts, rendered 80 cases in Chrome, and visually inspected desktop/mobile captures. Each output ran at 1280×900 and 320×720, light/dark and normal/reduced motion. Actual animation samples, interruption/reversal, state, focus and recovery observations supplement screenshots. Outputs were served unchanged through the contained loopback transport; no repairs, model calls or external requests occurred. There were no page or flow errors.

Scores below are Product fit / Observed playback / Scope and preservation / Accessibility / Honest state feedback / Source and evidence honesty. The frozen rule requires at least 10/12, no 0, all applicable automated assertions passing and no required-platform blocker.

| Task | Anonymous output | Six scores | Total | Material finding |
| --- | --- | --- | --- | --- |
| I | `dc96abbc` | 1 / 2 / 2 / 2 / 2 / 1 | 10/12 | Missing motion for the first-row-only A filter; Stale pending evidence note |
| G | `d36922d1` | 2 / 2 / 2 / 1 / 2 / 2 | 11/12 | Unbroken literal payload overflows 320px by 48px |
| F | `3486b782` | 2 / 2 / 2 / 2 / 2 / 2 | 12/12 | No material issue observed |
| H | `0a6201b4` | 2 / 2 / 2 / 1 / 2 / 1 | 10/12 | Transient foreground/background contrast 1.0; Claimed HTTP server denial lacks transcript corroboration |
| K | `b9cb1d71` | 2 / 2 / 2 / 1 / 2 / 2 | 11/12 | Unbroken literal payload overflows 320px by 48px |
| E | `0ce511bf` | 2 / 2 / 2 / 2 / 2 / 1 | 11/12 | Evidence note left at pending checkpoint |
| J | `89ff8313` | 2 / 2 / 2 / 2 / 2 / 1 | 11/12 | Claimed HTTP server denial lacks transcript corroboration |
| B | `da1fa116` | 2 / 2 / 2 / 1 / 2 / 2 | 11/12 | Per-record caret selection not retained |
| A | `492c26d0` | 2 / 2 / 2 / 2 / 1 / 2 | 11/12 | Same-string re-entry during pending cleared |
| L | `c788c6d4` | 2 / 2 / 2 / 2 / 2 / 2 | 12/12 | No material issue observed |

I's initial A filter changes the result set with zero animation in all four normal-motion cases. B filtering does show row movement, and newly visible rows fade; that partial coverage cannot cure the frozen assertion failure. Counts and filtering remain correct. The stale pending note is incomplete, rather than a claim that browser checks passed.

G/K preserve literal text and reject markup-shaped content as executable markup, but an unbroken synthetic payload extends the 320px page by 48px. Exact frozen CSS comparison and unchanged paragraph/textContent structure establish this as inherited layout behaviour. H changes only the requested background transition from 1200ms to the existing 140ms token. The immediate foreground colour swap and background-only interpolation are inherited; sampled early frames still reach contrast 1.0. These inherited outcome limitations retain their rubric deductions and are not presented as regressions.

B retains drafts, priority and the same textarea element, but loses a per-record selection range when returning. The baseline also overwrites input.value on each record show; the candidate does not repair that limitation. A saves, retries and survives reload correctly, including preserving a different newer draft. Editing away and re-entering the submitted string during pending clears that later editor intent; the same text has been saved, so this is an intent/recovery limitation rather than disappearance of the submitted note.

F's 403/401 feedback persists and preserves the address; editor retry produces one success, and a newer draft is explicitly unsaved. E's labelled native dialog contains Tab focus and restores the trigger after confirm/Escape. J/L keep immediate row/count updates under rapid changes. Focused keyboard typeahead selects Ready with filter focus retained at desktop/320; headless arrow-popup trials did not commit selection, so they are not counted as reversals.

Evidence notes generally distinguish mocked logic checks from browser playback. E/I notes remain at an initial pending checkpoint. H/J report an HTTP server PermissionError that is **not corroborated by the available transcript**; denied operations may be omitted from CLI traces, so this is an evidence limitation and is not called fabrication. Their source/VM checks are separately corroborated. No generator self-assessment was the sole evidence for a passing playback score.

The structured report binds supplied source trees, changed files against frozen fixtures, notes, transcripts and retained artifacts with SHA256. Full raw observations, 20 screenshots and 10 recordings remain outside the repository; the artifact manifest records exact filenames/sizes/hashes. Portable instrumentation is under [final-review-evidence](final-review-evidence/). Captured video is available for replay; not every video frame was manually watched. Chrome/emulated viewport results do not establish native playback, device performance, assistive-technology support or full accessibility conformance. Live-preference checks establish no running animation 45ms after the preference switch, without claiming every retriggered effect had already started.

[Structured scores, source hashes, coverage and artifact manifest](final-manual-review.json). [Separate native grading checkpoint](native-grading-readiness.md).
