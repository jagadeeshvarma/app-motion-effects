# Animation, transition, interaction and effects taxonomy

Use the whole taxonomy for a broad application pass; for a focused request, consult relevant rows only. These are overlapping dimensions, not a universal standard or an instruction to implement every effect. Mark applicability and evidence honestly. Specialist or decorative work needs a product benefit, platform support and permission under the app's design rules.

## A. Interface and interaction patterns

| ID | Category | Technical vocabulary / representative cases |
| --- | --- | --- |
| A01 | Navigation transitions | Pages, routes, screens, navigation stacks, forward/back, push/pop |
| A02 | View and content transitions | Tabs, panels, form steps, replacement, crossfade, fade-through, shared-axis |
| A03 | Enter and exit animations | Entrance/exit, presence, insertion/removal, mount/unmount |
| A04 | Layout transitions | Reflow, position/size interpolation, intrinsic-size animation, FLIP: First, Last, Invert, Play |
| A05 | Shared-element transitions | Shared layout, container transforms, thumbnail-to-detail, hero transitions |
| A06 | Overlay transitions | Dialogs/modals, drawers, sheets, popovers, menus, tooltips, backdrops |
| A07 | Component-state animations | Checked, selected, enabled, active and permitted expansion/collapse states |
| A08 | Control microinteractions | Hover, press/release, focus, toggles, sliders, pickers, appropriate ripples |
| A09 | Gesture-driven interactions | Pan, swipe, pinch, rotation, scrubbing, direct manipulation, interactive dismissal/navigation |
| A10 | Drag-and-drop animations | Lift, previews, targets, insertion indicators, displacement, reordering, acceptance/rejection, snap-back |
| A11 | Scroll interactions | Scroll-triggered/scroll-linked animation, scroll-/view-progress timelines, snapping, sticky-header transitions |
| A12 | Scroll-boundary feedback | Overscroll, elasticity, rubber-banding, edge feedback, pull-to-refresh, scroll restoration |
| A13 | Form and input feedback | Validation, field status, character counters, submission/recovery, permitted floating labels |
| A14 | Loading and waiting states | Determinate/indeterminate progress, spinners, skeletons, shimmer, loaded-content reveal, placeholder replacement |
| A15 | Action and status feedback | Pending, success, error, confirmation, saving, synchronisation, optimistic updates, rollback |
| A16 | Transient notification feedback | Toast/snackbar entrance/exit, stacking/displacement, dismissal timing, countdown, swipe dismissal |
| A17 | Collection and data-change animations | Insertion/deletion, filtering/sorting/reordering, live-update highlighting, pagination, infinite scrolling |
| A18 | Data-visualisation animations | Chart/axis/series/path interpolation, bar growth, point movement, counters, gauges |
| A19 | Instructional and onboarding animations | Coach marks, spotlights, gesture demonstrations, tours, affordance animation |
| A20 | Responsive and adaptive transitions | Breakpoints, orientation, window resizing, pane-to-sheet, keyboard/inset transitions |
| A21 | Appearance transitions | Supported theme, colour-scheme, density, contrast-mode and application appearance changes |
| A22 | Application lifecycle transitions | Launch/splash, restoration, foreground/background, connection/reconnection |

## B. Visual, graphic and rendering techniques

| ID | Category | Technical vocabulary / representative cases |
| --- | --- | --- |
| B01 | Transform animation | Translation, scale, rotation, skew, transform origin, perspective, composition |
| B02 | Opacity and visibility effects | Fade-in/out, cross-dissolve, alpha interpolation, visibility transitions |
| B03 | Colour animation | Foreground/background, fill/stroke, colour-space interpolation, permitted colour-stop animation |
| B04 | Surface and elevation effects | Shadow/elevation, borders, outlines, corner-radius interpolation |
| B05 | Clipping and masking effects | Clip paths, alpha/luminance masks, wipes, iris, masked text/image reveals |
| B06 | Filter effects | Blur, brightness, contrast, saturation, hue rotation, grayscale, displacement, turbulence, lighting filters |
| B07 | Compositing and blending effects | Alpha compositing, blend modes, Porter-Duff operations, isolated groups |
| B08 | Path and shape animation | Path morphing, shape interpolation, stroke drawing/dashes, motion paths, deformation |
| B09 | Animated iconography | Stateful/morphing icons, strokes, icon-to-loader, status symbols |
| B10 | Kinetic typography | Characters/words/lines, text reveal/replacement, rolling numbers, odometers, variable-font axis interpolation |
| B11 | Vector motion graphics | SVG, keyframed illustrations, diagrams, rigged graphics, interactive vector assets |
| B12 | Character and illustration animation | Rigging, skeletal animation, inverse kinematics, facial animation, poses, lip synchronisation |
| B13 | Raster and frame animation | Sprite sheets, image sequences, frame-by-frame and animated raster assets |
| B14 | Image and media transitions | Crossfades, zoom/pan, thumbnail expansion, carousels, progressive reveal, poster-to-video |
| B15 | 2.5D and depth effects | Layered parallax, perspective tilt, depth separation, flips, depth-based scaling |
| B16 | 3D object and scene animation | Object transforms, scene transitions, skeletal/skinned animation, morph targets, assembly/disassembly |
| B17 | Camera animation | Dolly, truck, pedestal, pan, tilt, orbit, zoom, camera paths, projection transitions |
| B18 | Material and lighting animation | Material properties, texture coordinates, light motion/intensity/colour, reflections/refractions |
| B19 | Shader and procedural effects | Vertex displacement, fragment effects, noise fields, dissolves, distortion, procedural textures, signed-distance fields |
| B20 | Particle and simulation effects | Emitters, trails/ribbons, flocking, fluids, cloth, rigid/soft bodies |
| B21 | Post-processing effects | Bloom, depth of field, motion blur, chromatic aberration, grain, vignette, tone mapping |
| B22 | Ambient and decorative animation | Background loops, texture motion, decorative parallax, idle, pulses, celebrations where justified/permitted |
| B23 | Spatial and immersive effects | Spatial transitions, world-space UI, depth/occlusion, gaze response, tracked objects |

## C. Mechanics, drivers and orchestration

These describe operation, not additional visual styles.

| ID | Category | Technical vocabulary |
| --- | --- | --- |
| C01 | Property interpolation | Tweening, linear/spline/quaternion/discrete interpolation |
| C02 | Keyframe animation | Keyframes, offsets, property tracks, sequences, hold frames |
| C03 | Timing and easing | Duration, delay, easing, cubic Bezier, steps, acceleration/deceleration |
| C04 | Physics-based animation | Springs, damping, stiffness, mass, velocity, inertia, friction, decay, bounce, elasticity, overshoot |
| C05 | Constraint-based animation | Bounds, snapping, collisions, attachments, follow behaviour, inverse kinematics |
| C06 | Timeline orchestration | Sequencing, parallel playback, stagger, overlap, cascade, synchronisation, parent/child choreography |
| C07 | State-machine animation | States, transitions, guards/conditions, triggers, state-driven playback |
| C08 | Animation blending | Crossfades, blend trees, weights, additive/layered animation |
| C09 | Event-driven animation | Pointer, touch, keyboard, focus, navigation, data, lifecycle events |
| C10 | Progress-driven animation | Scroll, gesture, playback/task progress, timeline scrubbing |
| C11 | Reactive and procedural animation | Input mapping, derived values, expressions, noise, sensor-driven motion |
| C12 | Playback control | Play, pause, stop, seek, reverse, rate, repeat, alternate, loop |
| C13 | Interruption and continuity | Cancellation, retargeting, velocity continuity, reversal, interrupted-state blending |
| C14 | Animation composition | Replacement, addition, accumulation, multiple effects on one property |

## D. Related sensory feedback

| ID | Category | Technical vocabulary |
| --- | --- | --- |
| D01 | Haptic feedback | Selection, impact, notification, transient/continuous haptics, custom patterns |
| D02 | Auditory feedback | Earcons, auditory icons, interaction sounds, status cues, spatial audio |
| D03 | Multimodal orchestration | Synchronised visual/audio/haptic feedback |
| D04 | Sensor-responsive interaction | Device motion, tilt/gyroscope, orientation, proximity/gaze response |

## Primary terminology references

- [Material motion patterns](https://m2.material.io/design/motion/the-motion-system.html): container transform, shared axis, fade through and fade. Use patterns as vocabulary, not a mandate to import Material styling.
- [Web Animations](https://www.w3.org/TR/web-animations-1/): timing, keyframes, playback and effect composition.
- [View Transition API](https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API): same-document and cross-document transitions.
- [Scroll-driven animation](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations): scroll-/view-progress timelines.
- [CSS Masking](https://www.w3.org/TR/css-masking-1/), [Filter Effects](https://www.w3.org/TR/filter-effects/) and [Compositing](https://www.w3.org/TR/compositing-1/): distinct rendering operations.
- [glTF animations](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#animations): node transforms, skinning and morph targets.
- [Apple motion](https://developer.apple.com/design/human-interface-guidelines/motion) and [haptics](https://developer.apple.com/design/human-interface-guidelines/playing-haptics): platform feedback guidance.
