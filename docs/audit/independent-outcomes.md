# Independent outcome review

Reviewed **2026-11-08**, against the five frozen `visualRubric` items in [acceptance.json](acceptance.json). Each item scores 0 inadequate, 1 partial, or 2 meets task. The first four conditions were genuinely hidden. For the later two outputs: **labels withheld; later-batch condition may be inferred from scheduling**. Only tasks A/B, provided anonymised source copies and independently generated browser evidence informed these scores; generator review files, mapping, original evaluation results and transcripts were not read.

| Anonymous output | Task | Product/task fit | Brand/conventions | Truthful feedback/interruption | Accessible clarity/input | Coherent/proportionate motion | Total |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `3fc0a8e6` | B: repair inspector | 2 | 2 | 2 | 2 | 2 | **10/10** |
| `ca146e90` | A: packing notes | 2 | 2 | 1 | 2 | 2 | **9/10** |
| `27d19673` | B: repair inspector | 2 | 2 | 2 | 1 | 2 | **9/10** |
| `759978a7` | A: packing notes | 2 | 2 | 2 | 2 | 2 | **10/10** |
| `942b4b00` | B: repair inspector, later batch | 2 | 2 | 2 | 1 | 2 | **9/10** |
| `bbd34f48` | A: packing notes, later batch | 2 | 2 | 2 | 2 | 2 | **10/10** |

All six meet the numerical 8/10 threshold in these tasks. No critical accessibility/security failure was observed. This is not a full accessibility/security assessment or a condition-level finding about skill effectiveness.

## Observed outcomes

**`3fc0a8e6`:** The heading fades from opacity 0.55 to 1 over the existing 140ms token. The form stays still and mounted. Rapid keyboard selection restores drafts, priority and the earlier text selection; repeated selection does not replay the cue. The plain repair-worker workflow and approved controls remain intact. [Desktop state](independent-evidence/3fc0a8e6-desktop-light-no-preference-mid.png), [mobile reduced-motion state](independent-evidence/3fc0a8e6-mobile-dark-reduce-final.png), [recorded playback](independent-evidence/3fc0a8e6-desktop-playback.webm).

**`ca146e90`:** Pending/failure/retry are truthful; repeated presses produce one attempt; saved notes survive reload. A different newer draft survives a pending save. Feedback fades and the new note arrives with a small 3px translation using the existing 140/220ms tokens. Conditional issue: editing away from the submitted text and back before completion clears that newly edited draft, because `public/app.js:45` uses equality alone. The submitted text is saved, so this is an editing-intent limitation rather than observed repository data loss. [Mobile failure](independent-evidence/ca146e90-mobile-dark-no-preference-error.png), [mobile state](independent-evidence/ca146e90-mobile-light-no-preference-final.png), [recorded playback](independent-evidence/ca146e90-desktop-playback.webm).

**`27d19673`:** The mounted inspector fades from opacity 0.75 and moves 4px over the approved 220ms token. Rapid switching cancels stale playback; drafts and priority remain correct, and keyboard selection works. Conditional issue: returning to Lamp restores text but puts selection at its end, 19–19, rather than the earlier 3–8 selection. Both form nodes retain identity, but editing position is lost (`public/app.js:13`). [Intermediate desktop state](independent-evidence/27d19673-desktop-light-no-preference-mid.png), [mobile state](independent-evidence/27d19673-mobile-light-no-preference-final.png), [recorded playback](independent-evidence/27d19673-desktop-playback.webm).

**`759978a7`:** Pending/failure/retry, duplicate prevention and reload persistence work. Revision-based tracking preserves the newer draft even after editing away and back to the same text. Feedback and new notes fade with the existing 140/220ms tokens. The failure switch is consumed once, so the next save retries directly; the task does not require persistent versus one-shot behaviour, and no deduction was made. [Mobile failure](independent-evidence/759978a7-mobile-dark-no-preference-error.png), [mobile state](independent-evidence/759978a7-mobile-dark-reduce-final.png), [recorded playback](independent-evidence/759978a7-desktop-playback.webm).

**`942b4b00`, later batch:** Only the heading fades from opacity 0.65 and moves 3px over 140ms; the mounted form remains still. Rapid keyboard switching, separate draft/priority values and same-record reselect work. Returning to Lamp loses the earlier 3–8 selection, restoring it at 19–19, so the same conditional input-behaviour deduction applies (`public/app.js:26`). [Desktop cue](independent-evidence/942b4b00-desktop-light-no-preference-mid.png), [mobile reduced state](independent-evidence/942b4b00-mobile-dark-reduce-final.png), [playback](independent-evidence/942b4b00-desktop-playback.webm), [both-record check](independent-evidence/per-record-942b4b00.json).

**`bbd34f48`, later batch:** Failure retains the draft, retry succeeds, repeated activation causes one attempt, and saved notes survive reload. Short feedback and new-note opacity fades use the approved 140/220ms tokens. The save button retains focus with `aria-disabled` and a working synchronous guard. The textarea becomes read-only while pending: real keyboard attempts to edit away or away-and-back are blocked, rather than accepted and lost. Concurrent editing is temporarily unavailable; it is not required by this task and was not deducted. [Mobile failure](independent-evidence/bbd34f48-mobile-dark-no-preference-error.png), [mobile state](independent-evidence/bbd34f48-mobile-dark-reduce-final.png), [playback](independent-evidence/bbd34f48-desktop-playback.webm).

## Evidence and limits

Google Chrome **158.0.8127.18**, through Playwright's Chrome channel, exercised all six outputs at **1280×900** and **390×844**, light/dark, normal/reduced motion: **48 cases**. Screenshots were visually inspected; live animation samples showed intermediate opacity/transform values. Reduced-mode follow-up recorded no active motion, and changing the preference during playback left no active animations after 40ms. All cases had no page errors or horizontal overflow. Source remained unchanged.

For the later A output, instrumentation attempted real keyboard input immediately in the read-only field; it did not let Playwright auto-wait for editability until after completion and mislabel the result as a pending edit. The first A-page sampler disappeared on reload; a separate follow-up captured its actual playback before reload. Immediate post-emulation animation counts are superseded by the 40ms settled check, not classified as failures. [Detailed scores and source hashes](independent-outcomes.json), [raw observations](independent-evidence/observations-first-four.json), [motion follow-up](independent-evidence/motion-followup.json).

Mobile evidence is responsive/touch browser emulation. Screen-reader audio, real mobile hardware/native runtime, 200% text/zoom, forced colours, other browsers and frame-rate/battery performance were not tested. Two development tasks and six outputs are too small a sample for broad comparative claims. No repairs were made.
