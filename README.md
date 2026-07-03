# 057 · Liberty Lights

**Category:** Interactive (I)
**Shipped:** July 3, 2026
**Live URL:** https://augustineiacopelli.github.io/appaday-057-liberty-lights/

## What it does

Tap anywhere on the night sky to launch a firework toward that point. Choose from six burst styles before you tap: Peony, a classic gold radial burst; Willow, long silver cascading trails with heavier gravity; Chrysanthemum, a layered sapphire bloom with a twinkle effect; Liberty Ring, a tight uniform red ring; Freedom Palm, an upward crackle burst that pops a second time mid-fall; and the signature ★ 250 Salute, concentric red, white, and blue rings with thirteen gold sparks on the outer edge, one for each of the original colonies. A seventh option, Random Mix, picks a weighted random style on every tap instead of a fixed one.

An Auto Show toggle runs a self-playing display at randomized intervals. Sound is synthesized live through the Web Audio API, a launch whistle and a filtered-noise boom, with no external audio files, and the mute state persists across visits. The header badge shows a live countdown to July 4, 2026, computed from the system clock, so it reads correctly whether it's viewed a day before, on the day, or years from now.

Record Show captures every tap during a session, its position, timing, and resolved firework type, so a Random Mix show replays with the same specific bursts it had originally rather than re-rolling. Stopping the recording saves it to the browser automatically, so Play Show and Save Show stay available after a reload. Save Show downloads the sequence as a dated JSON file, and Load Show reads one back in, so a show can be handed to someone else or moved between devices. Play Show replays the full sequence on its own timeline. Starting a recording or playback turns off Auto Show automatically to avoid the three modes overlapping.

## Technical notes

Single-file vanilla HTML, CSS, and JavaScript. Canvas-based particle system using `globalCompositeOperation: 'lighter'` for glow blending and a low-alpha overlay fill each frame for motion trails instead of a hard clear. Physics runs in CSS pixel space with the canvas scaled by `devicePixelRatio` via `ctx.setTransform`. Pointer events handle both mouse and touch in one listener. Recording and playback timing runs through the same delta-time accumulator as Auto Show, so the file makes no use of `setTimeout` or `setInterval` anywhere. All DOM access is wrapped in a `window.addEventListener('load', ...)` block, canvas context creation is null-guarded, and the render loop is wrapped in try/catch so a drawing error can't kill the animation frame loop. `localStorage` access for the sound preference and saved show is wrapped in try/catch to tolerate sandboxed iframes. Save/Load uses a `Blob` and `FileReader` for file export and import, with no server involved.

## Design

Deep navy-to-black sky gradient rather than pure black, with a gold accent (nodding to the semiquincentennial branding) layered over Old Glory red and blue. Big Shoulders Display for the header type, Space Grotesk for UI, IBM Plex Mono for the countdown badge.
