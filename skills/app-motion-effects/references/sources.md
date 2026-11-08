# Source catalogue by use case

Starting shortlist researched 8 November 2026. This is not a universal ranking, compatibility guarantee or licence audit. Read current official docs and inspect the exact example, package version and asset licence before adoption. Search beyond this catalogue when justified. Prefer existing tools and compare at most two serious candidates for each improvement.

First establish the product/customer context, visual contract and intended behaviour using the [adaptation guide](adaptation.md). Then research a mechanism for that need. A resource's impressive demo, popularity or sector label does not establish fit. Assess actual state integration, task frequency/consequence, existing primitives/tokens, platform/access behaviour, cost and maintenance. Retain sufficient existing tools; original code is appropriate when it offers a clear advantage. Record meaningful adaptation, not just cosmetic changes, and preserve source notices.

Sources fall into different classes: platform primitives, animation/gesture libraries, reusable UI source, rendering engines and asset marketplaces. Do not substitute one class for another or import a whole visual system for one effect. Code, runtime, editor and asset terms can differ. Free and paid access varies; no purchase is authorised by this skill.

## Web primitives and general engines

### S01. Simple browser animation and playback
- [Web Animations API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Animations_API)
- [Web Animations specification](https://www.w3.org/TR/web-animations-1/)
Consider native CSS/browser capabilities for simple effects before adding a dependency.

### S02. Browser page/view continuity
- [View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API)
Check same-/cross-document support, routing, focus, interaction and fallbacks in actual target browsers.

### S03. Native scroll-driven animation
- [CSS scroll-driven animations](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations)
Distinguish event-triggered playback from progress continuously driven by scrolling.

### S04. React layout, presence, gestures and shared elements
- [Motion docs](https://motion.dev/docs)
- [Motion layout animation](https://motion.dev/docs/react-layout-animations)
Match installed versions and actual element/layout behaviour; test scrolling containers and text/image distortion.

### S05. Coordinated DOM/SVG timelines
- [GSAP docs](https://gsap.com/docs/v3/)
- [Anime.js docs](https://animejs.com/documentation/)
Use official code examples for relevant timeline, SVG, text, path and orchestration features. Do not install both without a clear benefit.

### S06. FLIP and substantial layout changes
- [GSAP Flip](https://gsap.com/docs/v3/Plugins/Flip/)
- [Motion layout](https://motion.dev/docs/react-layout-animations)
Check interruption, resize, scroll and actual DOM/state preservation.

### S07. Complex scroll choreography
- [GSAP ScrollTrigger](https://gsap.com/docs/v3/Plugins/ScrollTrigger/)
Preserve normal scrolling, meaningful reading order and a suitable reduced-motion equivalent.

### S08. Spring-driven React animation
- [React Spring introduction](https://www.react-spring.dev/docs/getting-started)
- [React Spring useTransition](https://www.react-spring.dev/docs/components/use-transition)
Evaluate physics, presence and collection transitions. React's own useTransition is a scheduling primitive, not a visual animation engine.

### S09. Gestures and direct manipulation
- [use-gesture](https://use-gesture.netlify.app/docs/)
Gesture input can drive the chosen animation engine. Test touch, pointer, scroll coexistence and accessible alternatives.

### S10. Drag/drop, sorting and reordering
- [dnd kit](https://dndkit.com/)
Choose the adapter supported by the actual framework/version. Keep keyboard operation and item identity intact.

## Reusable UI and framework-native components

### S11. Accessible controls and overlays
- [shadcn/ui components](https://ui.shadcn.com/docs/components)
- [Radix animation guidance](https://www.radix-ui.com/primitives/docs/guides/animation)
Keep focus, semantics, dismissal, keyboard and presence behaviour. Avoid replacing an established component system unnecessarily.

### S12. Animated React components and effects
- [React Bits](https://reactbits.dev/)
- [Magic UI](https://magicui.design/)
Inspect individual source and dependency choices. Adapt the effect to the app's rules instead of adopting default decoration.

### S13. Expressive React components and interface references
- [Aceternity UI](https://ui.aceternity.com/)
- [Kokonut UI Pro](https://kokonutui.pro/)
Some material is paid. Use only authorised source; access to a demo is not reuse permission. Do not import a whole landing-page style into an operational app.

### S14. Vue transitions
- [Vue Transition](https://vuejs.org/guide/built-ins/transition.html)
Prefer native framework transitions/transition groups when sufficient.

### S15. Svelte transitions
- [Svelte transition documentation](https://svelte.dev/docs/svelte/transition)
Use transition, animation and motion APIs for the installed version.

### S16. Charts, dashboards and interpolation
- [D3 transitions](https://d3js.org/d3-transition)
- [Nivo](https://nivo.rocks/)
- [Bklit UI](https://bklit.com/)
Inspect at most two relevant candidates, including the existing chart library. Preserve data accuracy, stable scales, readable labels and clear live updates.

## Icons, illustrations and vector assets

### S17. Animated icons and status symbols
- [useAnimations](https://useanimations.com/)
- [Lordicon](https://lordicon.com/)
Match stroke, optical size, family and control meaning. Verify selected asset and runtime licences separately.

### S18. Interactive graphics and state machines
- [Rive docs](https://rive.app/docs/getting-started/introduction)
- [Rive marketplace](https://rive.app/marketplace/)
Evaluate supported runtimes, data/state binding and the exact asset's licence. Editor/export access does not establish runtime or asset rights.

### S19. Vector animation assets
- [LottieFiles](https://lottiefiles.com/)
Check asset terms, rendering fidelity, feature support, target runtime and cost. A successful web preview does not prove native parity.

### S20. Illustrations and illustration animation
- [Storyset](https://storyset.com/)
- [unDraw](https://undraw.co/illustrations)
Storyset offers animation tools; unDraw is an illustration source, not an animation engine. Check adaptation and attribution requirements.

## Native and desktop

### S21. React Native UI animation
- [React Native Animated](https://reactnative.dev/docs/animations)
- [Reanimated docs](https://docs.swmansion.com/react-native-reanimated/)
- [Reanimated first animation](https://docs.swmansion.com/react-native-reanimated/docs/fundamentals/your-first-animation/)
Choose installed-version-compatible APIs. Check feature maturity, gesture integration and actual native runtime behaviour, especially shared-element features.

### S22. React Native custom graphics/shaders
- [React Native Skia](https://wcandillon.github.io/react-native-skia/)
Use only when custom drawing justifies integration/rendering cost. Select the docs matching the installed major version; historical Shopify URLs may redirect.

### S23. Flutter
- [Flutter animation docs and samples](https://docs.flutter.dev/ui/animations)
Evaluate implicit/explicit animation, physics, animated lists and Hero/shared-element transitions.

### S24. Apple platforms
- [SwiftUI animations](https://developer.apple.com/documentation/swiftui/animations)
- [Apple motion guidance](https://developer.apple.com/design/human-interface-guidelines/motion)
Use appropriate native transitions, gestures and animation APIs; check deployment-target availability.

### S25. Android
- [Compose animation](https://developer.android.com/develop/ui/compose/animation/introduction)
Choose installed-version-compatible visibility, content, state, gesture and shared-element approaches.

### S26. Windows desktop
- [Microsoft composition animation](https://learn.microsoft.com/en-us/windows/apps/develop/composition/composition-animation)
Match the actual desktop UI framework and platform versions.

## 3D, advanced rendering and sensory feedback

### S27. 3D scenes, cameras, materials and specialist effects
- [Three.js examples](https://threejs.org/examples/)
- [React Three Fiber](https://r3f.docs.pmnd.rs/getting-started/introduction)
Three.js is a rendering engine; React Three Fiber is a React renderer for it. Profile specialist shaders, particles/simulations and post-processing; provide appropriate low-cost alternatives.

### S28. Ready-made scenes and model assets
- [Spline Community](https://community.spline.design/)
- [Poly Pizza](https://poly.pizza/)
These are scene/model sources. Verify per-asset terms, attribution, export/runtime needs and optimisation.

### S29. Masking, filters and compositing
- [CSS Masking](https://www.w3.org/TR/css-masking-1/)
- [Filter Effects](https://www.w3.org/TR/filter-effects/)
- [Compositing and Blending](https://www.w3.org/TR/compositing-1/)
These are distinct mechanisms. Use appropriate platform examples; browser support, cost and the app's design permissions still govern adoption.

### S30. Variable fonts and text effects
- [Variable fonts](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Fonts/Variable_fonts)
- [Anime.js](https://animejs.com/documentation/)
- [GSAP](https://gsap.com/docs/v3/)
Preserve readable, selectable and accessible text, localisation and appropriate font licensing. Avoid splitting text in ways that duplicate screen-reader announcements.

### S31. Haptics and multimodal feedback
- [Apple haptic guidance](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- [Apple motion guidance](https://developer.apple.com/design/human-interface-guidelines/motion)
Use each target platform's own audio/haptic APIs and expected meanings. Keep essential information available without audio/haptics; respect user settings.

For an unlisted stack, discover its official animation/graphics/gesture APIs. Do not translate web compatibility claims into native or desktop claims. Runtime support and all licence/access conditions must be verified at implementation time.
