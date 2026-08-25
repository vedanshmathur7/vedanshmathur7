# GitHub Profile Plan - vedanshmathur7

This is the handoff plan for making the profile look like a serious engineering signal, not a decorative README.

## Current Verdict

The reference repo works because it has three things at once:

- Custom generated SVGs that do not depend on third-party README-stat services.
- A short, sharp identity with no generic badge wall.
- Projects that match the claimed identity.

Your strongest proven identity from the resume and LinkedIn export is not "pure low-level C++" yet. It is:

> AI backend systems: FastAPI services, LLM inference/evaluation workflows, async pipelines, databases, Docker, and AWS.

That is the profile direction implemented in this repo. The low-level/systems angle should be built next through real repos, not only README language.

## What Was Changed

- Rewrote `README.md` around AI backend systems and LLM infra.
- Removed third-party GitHub stat-card widgets from the main design.
- Added generated local SVG assets:
  - `header.svg`
  - `hd-about.svg`
  - `hd-stack.svg`
  - `hd-projects.svg`
  - `hd-stats.svg`
  - `hd-roadmap.svg`
  - `stats.svg`
  - `langs.svg`
  - `year.svg`
- Added `scripts/generate_profile.py` to regenerate all SVGs.
- Added `.github/workflows/profile.yml` to refresh assets daily and on manual dispatch.
- Added local JetBrains Mono font assets under `scripts/fonts/`.

## Immediate Fixes Needed From Vedansh

1. Make `CallLevelAnalytics` public, or provide the correct public repo URL.
   - Current public check: `https://github.com/vedanshmathur7/CallLevelAnalytics` returns 404.
   - Until fixed, the README mentions it without a link.

2. Decide whether PlagLe should be presented as FastAPI/backend or full-stack.
   - Public GitHub shows `plagle-backend` and `plagle-frontend`.
   - Resume says Python/FastAPI/MySQL/Docker.
   - README currently frames it as backend, which is fine only if the backend folder is substantial and documented.

3. Upload or link a current resume URL.
   - README keeps the existing GitHub attachment link.
   - Better: add `resume.pdf` to a personal site or release asset and link that stable URL.

4. Pin repositories in this order:
   - CallLevelAnalytics, once public and cleaned.
   - ModelArena.
   - PlagLe.
   - Greywater Recycling and Smart Irrigation System.
   - Best recent deployed app.
   - One new C++/systems repo once built.

## Repo-Level Work To Do Next

### CallLevelAnalytics

Goal: make it the flagship repo.

Checklist:

- Add a top-level README with problem, architecture, setup, screenshots, and evaluation output.
- Add `.env.example`.
- Add a small anonymized sample dataset or generated fixture.
- Add a `docs/architecture.md` or architecture diagram.
- Add a one-command local smoke test.
- Add repo topics: `fastapi`, `llm-evaluation`, `asyncio`, `postgresql`, `openai`, `rag`, `aws`.

### ModelArena

Goal: keep it as the public LLM comparison/demo repo.

Checklist:

- Ensure the Hugging Face demo link still works.
- Put screenshots near the top of the README.
- Keep evaluation tables, but make the first 30 seconds of reading crisp.
- Add badges only for deployment/test status if they are real.

### PlagLe

Goal: make it look like a maintained product/backend repo, not a random hackathon dump.

Checklist:

- Add a root README if missing.
- Document `plagle-backend` and `plagle-frontend` separately.
- Add setup instructions for local backend, frontend, and database.
- Add screenshots or a deployed link preview.
- Add topics: `fastapi`, `plagiarism-detection`, `mysql`, `document-analysis`, `full-stack`.

### New Systems Repo

Goal: earn the low-level/systems identity.

Pick one:

- `cachelab-cpp`: cache-aware benchmarks for arrays, linked lists, matrix traversal, and struct layout.
- `tiny-allocator`: malloc/free style allocator with free list, coalescing, fragmentation tests, and benchmark notes.
- `chip8-cpp`: CHIP-8 emulator with SDL display, instruction tests, and ROM screenshots.

Best first choice: `cachelab-cpp`. It is fastest to ship, visual, benchmarkable, and easier to explain than an emulator.

Required README shape:

- What the project proves.
- How to run.
- Benchmarks with machine info.
- Graphs or tables.
- What changed after optimization.
- Clear limitations.

## Profile README Maintenance

Run locally:

```bash
python3 scripts/generate_profile.py
```

Without `GITHUB_TOKEN`, the generated stats use fallback values. On GitHub Actions, `secrets.GITHUB_TOKEN` is available automatically and will render real contribution/language data.

Manual GitHub refresh:

1. Push the repo.
2. Open Actions.
3. Run the `profile` workflow manually if needed.

## What Not To Do

- Do not claim "low-level systems engineer" until there is at least one strong C++ systems repo pinned.
- Do not add a wall of shields.io skill badges.
- Do not link dead/private repos from the profile README.
- Do not use generic GitHub stat-card services as the main visual identity.
- Do not over-explain every project. The profile README should be sharp; project READMEs carry the depth.
