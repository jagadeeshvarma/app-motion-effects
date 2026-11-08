# Corpus amendments

## Amendment 1, before model evaluations

Initial freeze: a0a7975ce1c981bb4bb6527769417d1fdadbf0a90ea4e616d4a9126b6f0a2090. Preserved in frozen.json.

Native C/D grader tests now explicitly advance fake time before settling asynchronous local repository completions. This prevents a correct unmount/cancellation path from failing because pumpAndSettle stopped before a Future.delayed timer elapsed. Reduced-motion widget tests now set the platform accessibility feature directly and clear it after the test. No task, fixture, acceptance behavior or other grader assertion changed. tools/validate.py now verifies the superseding full manifest.

The amendment is based only on untreated fixture validation, not evaluated model outputs. All three experimental conditions must use this superseding version. No model tasks have run.

## Amendment 2 (MA04), chronology correction

Acceptance criteria were established before instruction edits. Final A–L corpus freezing finished before comparative runs but after instruction edits had begun. The task author worked independently and did not inspect the improved candidate. The earlier `frozen_before_skill_changes=true` metadata and pre-edit wording were too strong and are corrected. All task prompts, fixtures, grader assertions and acceptance thresholds remain unchanged. The initial and first-amendment manifests are retained. Supplemental M/N were genuinely authored after the candidate freeze and remained held out until outputs.
