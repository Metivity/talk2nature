# Zero Command direct-fragment focus

**Date:** 2026-10-31  
**Baseline:** public `main` after `221ce30`; local noindex build  
**Question:** when a person opens the Station directly at `#station-console`, does keyboard focus identify the destination before they continue?

## Change and evidence

The named Station section now has `tabindex="-1"`, allowing direct fragment navigation to place focus on the console without adding it to the normal Tab sequence. A visible focus outline makes that destination visible. In a fresh local browser tab at 2560 × 1440 CSS pixels, the direct route focused the Station region and rendered its outline; the next Tab reached the Station link inside the region. The ordinary route still exposes **Skip to content** as its first Tab stop.

The focused regression, all **171 Node tests**, all **244 Python tests** (one intentional skip), local noindex build (**162 pages plus 404**), site check (**163 HTML documents / 11,341 links**) and `git diff --check` passed. No microphone, audio playback, animal or participant data was used.

## Limits and next step

This establishes maintainer-run browser focus behavior only. VoiceOver, TalkBack, physical-device behavior and independent first-use remain **not run**. On the direct fragment, the first Tab after the focused region still reaches the Station link; this change does not make Skip to content the first Tab stop after that fragment. Continue the active five-track goal with named-device and screen-reader checks from `ZERO_COMMAND_DEVICE_CHECKLIST.md` when hardware is available. Keep the passive-output and real-data admission boundaries unchanged.
