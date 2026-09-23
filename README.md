# 139. Static Sleep Mixer

**Live app:** https://augustineiacopelli.github.io/appaday-139-static-sleep-mixer/

**Part of AppADay:** https://augustineiacopelli.github.io/appaday/

Static Sleep Mixer blends white, pink, and brown noise into one continuous sleep sound, with a sleep timer that fades the mix to silence.

## What it does

Tap play and pink noise starts within a moment. Each of the three layers has its own toggle and volume slider, and a master volume sits beneath them. Layers fade in and out rather than switching abruptly, and every volume change is smoothed so there are no clicks or zipper noise. Choose a sleep timer of 15, 30, 45, 60, or 90 minutes and the sound holds steady, then eases down to silence over the final stretch before stopping. The screen uses a dim navy and amber palette so it does not light up a dark bedroom. Your mix, volumes, and timer choice are saved in the browser and restored on your next visit, without starting any sound until you tap play.

## How it works

The noise is generated in the browser with the Web Audio API. Nothing is downloaded. When you first tap play, the app creates an audio context and builds three eight second noise buffers at the device's sample rate. White noise is plain random samples. Pink noise uses Paul Kellet's refined filter. Brown noise uses a leaky integrator so the random walk never drifts. Each buffer has its end crossfaded into its beginning with an equal power curve, which removes the thump that would otherwise mark the loop point, most noticeably in brown noise.

All three sources loop continuously for the life of the session, and layers are switched purely by gain, which avoids start latency. A limiter on the output keeps the combined layers from clipping. The sleep timer fade is scheduled on the audio thread itself, so it completes on time even when the phone is locked and the browser slows down page scripts.

## Notes

On iPhone and iPad, the ring/silent switch mutes web audio. The app shows a reminder to flip it to ring on those devices.

## Built with

A single `index.html` file of vanilla HTML, CSS, and JavaScript, using the Web Audio API and the Outfit typeface from Google Fonts. No frameworks, no build step, and no API key required.

---

Built on 2026-09-23 as app 139 of AppADay by Augustine Iacopelli.
