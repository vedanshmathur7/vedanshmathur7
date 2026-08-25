# GitHub Profile Revamp Plan — vedanshmathur7

**Goal:** Make the GitHub profile read as "C++ / low-level systems developer" instead of the current generic AI/backend template README. Anyone (Vedansh, or a fresh Claude session) can pick up from wherever this stopped — just check the boxes.

**Current state (checked 2026-08-25):**
- Profile README exists at `vedanshmathur7/vedanshmathur7` — has shields.io badges, GitHub stats/streak/trophy widgets (generic template style, thousands of profiles look like this).
- Pinned repos: CallSight (JS), agrochain (fork, TS), Insurance-Cost-Prediction (Jupyter), ModelArena (Python), PlagLe (JS), ReLive-AI (JS). **Zero C++/low-level repos pinned or visible.**
- Resume lists C++ and C as languages but no dedicated low-level project exists yet in the visible repo list.
- Reference profile liked: `github.com/andriidrok1` — custom ASCII art + auto-generated SVGs via GitHub Actions, JetBrains Mono, dark terminal aesthetic.

---

## Phase 0 — Decide the actual positioning (do this first, 5 min)
- [ ] Confirm identity: "systems/low-level C++ dev learning towards embedded" vs "backend+AI dev who also does C++ for fun." Be honest — overselling a vibe with nothing behind it reads worse than owning the AI-backend work and treating C++ as a growing focus.
- [ ] Pick 1 sentence for the README hero line reflecting this (e.g. "FastAPI/LLM infra by day, chasing cycles and cache misses by night").

## Phase 1 — Backing content (the part that actually matters)
Without this, the README is decoration. Pick 1–2 to build:
- [ ] **CHIP-8 emulator in C++** — classic, small, universally recognized as a "real" low-level project, ~1–2 weekends.
- [ ] **Custom memory allocator** (malloc/free reimplementation with a free-list or buddy allocator) — directly demonstrates low-end-machine thinking.
- [ ] **Tiny cooperative task scheduler / RTOS-lite** in C++ for a microcontroller (or simulated) — pairs well with the Arduino badge already on the profile.
- [ ] **Cache-aware benchmark repo** — e.g. matrix multiply / linked-list traversal comparisons showing cache-line effects, with graphs. Good because it's visual + quantifiable.
- [ ] Once built: **pin it** on the GitHub profile (replace 1–2 of the current JS/AI pins), add a proper repo description + topics (`cpp`, `embedded`, `systems-programming`, `low-level`).

## Phase 2 — README structure (the "vibe" part)
Rewrite `vedanshmathur7/vedanshmathur7/README.md`. Two directions discussed — pick one or merge:
- [ ] **Boot-log style**: whole README framed as a fake system boot sequence (`[ OK ] Mounting /skills`, `[ OK ] Loading vedansh.sys`, register-dump-style stats block).
- [ ] **neofetch-card style**: custom SVG with ASCII/circuit art on the left, info block on the right (Focus: Systems/Embedded, Languages, Uptime since 2023, etc.) generated via a script, not a static image, so it can auto-refresh.
- [ ] Keep the good parts already there (contact badges, resume link) but swap the generic shields.io skill badges for something less templated — either the neofetch card or a monospace text block.
- [ ] Font: JetBrains Mono / monospace throughout, dark theme — matches the systems-dev aesthetic and is consistent with the andriidrok1 reference.

## Phase 3 — Visual assets (SVGs)
- [ ] Build 1 custom SVG: ASCII-art chip/circuit-board header, rendered as SVG (not a raw image) so it stays crisp and can be theme-aware (light/dark).
- [ ] Optional: a "compile-time" or "lines of C++" joke stat instead of generic contribution stats — more on-brand than default streak widgets.
- [ ] Store SVG-generation scripts in a `scripts/` folder in the profile repo (mirrors what andriidrok1 does) so it's clearly automated, not hand-edited.

## Phase 4 — Automation (GitHub Actions)
- [ ] Add a `.github/workflows/` action that regenerates the stats/ASCII SVGs on a schedule (daily/weekly) and commits them — this is what makes a profile look "alive" vs a one-time edit.
- [ ] Keep it simple at first: a Python or Node script that outputs SVG, run on a cron trigger.

## Phase 5 — Polish
- [ ] Add repo topics/tags to every real project (helps discoverability + signals intentionality).
- [ ] Reorder pinned repos: lead with the new C++/low-level project(s), then ModelArena/CallSight (real AI work), drop weaker ones (forked agrochain, empty PlagLe/ReLive-AI if they have no README).
- [ ] Add short, punchy one-line descriptions to every repo (GitHub shows this next to the name — currently several have no description).

---

## Notes for whoever continues this
- Don't just theme the README — Phase 1 (real project) is the actual differentiator. A boot-log README pointing at JS/Jupyter repos will look like cosplay.
- Reference profile for visual style: `github.com/andriidrok1`.
- Vedansh's current stack for context: Python/FastAPI/AWS/LLM infra (day job at WittingAI on DataVox) + wants to build out C++/low-level as a second identity.
