# Rendered evaluation evidence

Actual Chrome captures of synthetic final-candidate outputs. These are evidence of the reviewed interfaces, not a passed release gate. No captures or model outputs were repaired. Full logs remain outside the repository.

| Output | Desktop | 320px | Playback |
| --- | --- | --- | --- |
| A · 492c26d0 | [View](final-evidence/492c26d0-desktop-light-central.png) | [View](final-evidence/492c26d0-mobile-dark-central.png) | [Play](final-evidence/492c26d0-desktop-playback.webm) |
| B · da1fa116 | [View](final-evidence/da1fa116-desktop-light-central.png) | [View](final-evidence/da1fa116-mobile-dark-central.png) | [Play](final-evidence/da1fa116-desktop-playback.webm) |
| E · 0ce511bf | [View](final-evidence/0ce511bf-desktop-light-central.png) | [View](final-evidence/0ce511bf-mobile-dark-central.png) | [Play](final-evidence/0ce511bf-desktop-playback.webm) |
| F · 3486b782 | [View](final-evidence/3486b782-desktop-light-central.png) | [View](final-evidence/3486b782-mobile-dark-central.png) | [Play](final-evidence/3486b782-desktop-playback.webm) |
| G · d36922d1 | [View](final-evidence/d36922d1-desktop-light-central.png) | [View](final-evidence/d36922d1-mobile-dark-central.png) | [Play](final-evidence/d36922d1-desktop-playback.webm) |
| H · 0a6201b4 | [View](final-evidence/0a6201b4-desktop-light-central.png) | [View](final-evidence/0a6201b4-mobile-dark-central.png) | [Play](final-evidence/0a6201b4-desktop-playback.webm) |
| I · dc96abbc | [View](final-evidence/dc96abbc-desktop-light-central.png) | [View](final-evidence/dc96abbc-mobile-dark-central.png) | [Play](final-evidence/dc96abbc-desktop-playback.webm) |
| J · 89ff8313 | [View](final-evidence/89ff8313-desktop-light-central.png) | [View](final-evidence/89ff8313-mobile-dark-central.png) | [Play](final-evidence/89ff8313-desktop-playback.webm) |
| K · b9cb1d71 | [View](final-evidence/b9cb1d71-desktop-light-central.png) | [View](final-evidence/b9cb1d71-mobile-dark-central.png) | [Play](final-evidence/b9cb1d71-desktop-playback.webm) |
| L · c788c6d4 | [View](final-evidence/c788c6d4-desktop-light-central.png) | [View](final-evidence/c788c6d4-mobile-dark-central.png) | [Play](final-evidence/c788c6d4-desktop-playback.webm) |

See [manual scores and limitations](final-manual-review.md), [capture integrity](final-evidence/manifest.json) and [runtime snapshot manifest](../../evals/outputs-final/manifest.json).

Run an unchanged synthetic output locally, for example:

```sh
python3 -m http.server 8000 --directory evals/outputs-final/A/public
```

I uses `evals/outputs-final/I/packages/warehouse/public`. Its automated animation failure remains FAIL. M/N runtime snapshots are also retained; they were held out until generation finished. Native pilot recordings remain exploratory and outside the clean comparison.

Held-out M/N: [manual review](heldout-manual-review.md), [capture manifest](final-evidence/heldout-MN/manifest.json), [M playback](final-evidence/heldout-MN/M-desktop-light-normal-playback.webm), [N playback](final-evidence/heldout-MN/N-320-dark-normal-playback.webm). Runtime PASS does not waive their failed manual evidence-honesty gates or agent timeouts.
