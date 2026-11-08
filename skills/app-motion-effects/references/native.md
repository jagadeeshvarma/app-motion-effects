# Native interaction implementation

Read only the relevant stack section after discovering the app's installed versions and supported targets. Use its existing engine and navigation/state architecture. These are implementation prompts, not a claim that every stack has been runtime-tested with this skill.

## Shared native contract

- Identify iOS/Android targets, navigation ownership, safe-area/inset handling, text scaling, keyboard avoidance and system back/interactive-dismiss behaviour. Retain native conventions and the app's actual brand.
- Keep draft/state outside transient presentation when it must survive closing, rotation, process restoration or backgrounding. Do not promise persistence beyond the existing storage contract.
- Handle loss of connectivity/permission while work is pending using existing rules. Do not request a device permission simply to demonstrate its animation. Mock permission outcomes in isolated tests.
- Separate UI dismissal from cancellation of underlying work. Ignore stale completions by request identity; preserve an explicit retry's existing idempotency contract. Invalidate callbacks and dispose controllers/listeners when their owner leaves.
- Observe the platform's reduced-motion preference, including changes while the screen is mounted. Keep final state, accessible meaning and task completion intact. Haptics/audio are optional reinforcement, never the only signal.
- Test touch targets, large text, screen-reader names/order, focus, keyboard, safe areas, back gestures, background/resume and repeated input where affected. Do not infer native behaviour from browser emulation.

## Flutter

Prefer existing implicit widgets for simple state changes; use an owned/disposed AnimationController only when playback control is needed. Keep stable keys and text controllers; do not replace a form merely to animate a record change. An AnimatedSwitcher can temporarily retain outgoing content: prevent obsolete controls and duplicate semantics from remaining active.

Check the installed SDK's accessibility APIs. Current Flutter distinguishes Android disableAnimations and iOS reduceMotion; inspecting only MediaQueryData.disableAnimations (or MediaQuery.disableAnimationsOf(context)) can miss iOS Reduce Motion. Custom explicit animations must observe the relevant platform features and update when accessibility settings change. A MediaQuery override in a widget test is not proof that framework controllers or actual OS settings behave correctly. Stop or replace nonessential repeating motion under reduced motion. Do not simply switch a repeating controller from AnimationBehavior.preserve to normal: preserve is the repeat default to avoid rapid flashing. Check the installed engine’s behaviour and keep a readable static status.

Use flutter analyze and focused widget tests for state, interruption and disposal. Then run the real app on each claimed native platform using the repository's normal runner/integration tests. A successful widget test or Dart compilation is a narrower result than a simulator/emulator run. Record SDK versions; APIs change.

Official references: [animation approaches](https://docs.flutter.dev/ui/animations), [disableAnimations and iOS distinction](https://api.flutter.dev/flutter/widgets/MediaQueryData/disableAnimations.html), [reduceMotion](https://api.flutter.dev/flutter/dart-ui/AccessibilityFeatures/reduceMotion.html), [integration testing](https://docs.flutter.dev/testing/integration-tests).

## React Native / Expo

Use the app's installed Animated/Reanimated/gesture versions. Do not copy web DOM/CSS APIs into native components. Confirm worklet/thread boundaries and supported scheduling APIs in the installed documentation; examples from different major versions can conflict. Prefer built-in press and scroll controls when gestures add no value. Keep gesture cancellation, scrolling and accessible non-gesture alternatives usable.

Observe the engine's reduced-motion configuration and application/platform accessibility settings; do not assume a web media query covers native. Clean up shared listeners, animations and asynchronous callbacks. Test actual iOS and Android navigation/keyboard/lifecycle behaviour; a Metro bundle or Expo web preview proves neither.

Official references: [React Native animations](https://reactnative.dev/docs/animations), [AccessibilityInfo](https://reactnative.dev/docs/accessibilityinfo), [Reanimated](https://docs.swmansion.com/react-native-reanimated/), [Expo](https://docs.expo.dev/).

## SwiftUI / UIKit

Use deployment-target-compatible animation/transition APIs and the app's existing state ownership. Honour accessibilityReduceMotion or the UIKit equivalent, including settings changes. Preserve focus, form identity, interactive dismissal and navigation state. Observe scenes becoming inactive/backgrounded; stop unnecessary continuous work without falsely completing the user's task.

Official references: [SwiftUI animations](https://developer.apple.com/documentation/swiftui/animations), [accessibilityReduceMotion](https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducemotion), [Apple motion guidance](https://developer.apple.com/design/human-interface-guidelines/motion).

## Android / Jetpack Compose

Use the app's existing Compose/View stack and version-compatible animation APIs. Retain state with the established ownership/restoration approach; do not introduce a second navigation or persistence system for motion. Confirm system duration-scale/reduced-motion behaviour for custom loops, focus/semantics of outgoing content, predictive/system back, IME/insets and lifecycle-aware collection.

Official references: [Compose animation](https://developer.android.com/develop/ui/compose/animation/introduction), [accessibility](https://developer.android.com/develop/ui/compose/accessibility), [lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle).

## Unavailable runtime

Complete safe source changes and available checks; supply launch/replay steps and identify the exact missing SDK, dependency, simulator, credential or hardware. Label native screenshots approximations when produced outside native. Report separately: source guidance, static analysis, widget/unit tests, build, simulator/emulator playback, hardware/accessibility checks and store release. A blocked level cannot silently become a pass.
