# MyResume — AI resume platform (backend + landing page)

A working clone-style implementation of the makemycv.com product structure: an **AI resume
builder API** in Python/FastAPI and a **marketing landing page** in Next.js 15.

The core design decision: **the AI never has a single point of failure.** Every AI feature tries a
provider chain (OpenRouter → Groq → Gemini → Mistral → Cerebras → Ollama) and silently falls back
to a deterministic, rule-based offline engine. The API is therefore fully functional with **zero
API keys** — no spinner-forever demos, no crash when a provider is down.

```
myresume/
├─ backend/          FastAPI + AI provider chain + ATS engine + PDF/DOCX export
├─ landing/          Next.js 15 landing page (the makemycv-style marketing site)
├─ start-windows.bat  starts both servers
├─ .env.example      every supported environment variable, all optional
└─ README.md
```

---

## 1. Quick start

Two terminals. Backend first:

```powershell
cd "C:\Users\ali hosseinabadi\myresume\backend"
pip install -r requirements.txt          # fastapi, uvicorn, pydantic, httpx, reportlab
python -m uvicorn main:app --reload --port 8010
```

> **Use port 8010, not 8000.** `landing/.env.local` sets
> `NEXT_PUBLIC_API_BASE_URL=http://localhost:8010`, and on this machine port 8000 is
> already held by a Windows `svchost` service, so the backend cannot bind it.
> If you change the port, change `.env.local` too and restart `npm run dev`
> (`NEXT_PUBLIC_*` is inlined when the dev server starts).

Landing page:

```powershell
cd "C:\Users\ali hosseinabadi\myresume\landing"
npm install
npm run dev                              # http://localhost:3000
```

Or run `.\start-windows.bat` from the repo root.

* API docs: <http://localhost:8010/docs>
* Landing page: <http://localhost:3000>

No keys are required. To use a real model, copy `.env.example` → `.env` and set one key
(`GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `CEREBRAS_API_KEY`) or
run Ollama locally. `AI_PROVIDER=auto` picks the first configured provider, and every response
reports which one answered via its `provider` field.

---

## 2. Backend (`backend/`)

### Layout

| Path | Purpose |
| --- | --- |
| `main.py` | FastAPI app, CORS, lifespan DB init, `/api/health` |
| `config.py` | Pydantic-settings config loaded from `.env` |
| `models.py` | Every request/response schema (Resume, AI contracts, ATS) |
| `db.py` | SQLite storage: resumes, cover letters, `ai_events` telemetry |
| `catalog.py` / `sample.py` | 11 templates + a fully-populated sample resume |
| `ai/providers.py` | Provider catalog, chain resolution, Ollama liveness probe |
| `ai/runtime.py` | JSON repair, response cache, provider-agnostic `llm_json` |
| `ai/engine.py` | Writing features (summary, bullets, skills, rewrite, letters, draft) |
| `ai/engine_ats.py` | ATS scoring narrative + freeform CV assistant |
| `ai/tailor.py` | **The headline flow: advert → tailored CV** (title inference, seeded writing, score) |
| `ai/local_engine.py` | **The offline engine** — deterministic, no network |
| `ai/prompts.py`, `ai/prompts_letters.py` | Recruiter-grade prompt templates |
| `ai/lexicon.py`, `ai/skills.py` | Action verbs, stopwords, clichés, skill ontology |
| `ai/translations.py` | Section headings in **24 locales** |
| `ai/keywords.py` | Keyword/phrase extraction, bullet heuristics |
| `services/ats.py`, `services/ats_checks.py` | 15 weighted ATS checks + JD keyword blending |
| `services/export_pdf.py`, `services/pdf_styles.py` | A4 PDF via ReportLab Platypus |
| `services/export_docx.py`, `services/docx_parts.py` | `.docx` writer on stdlib `zipfile` |
| `services/job_import.py`, `services/html_extract.py` | Job-link import: engine output → JSON-LD → OG/meta → visible text |
| `services/scrapers.py`, `services/sg_extract.py`, `services/ats_boards.py` | **Fetch engine chain** — ATS board API → ScrapeGraphAI → Playwright → reader proxy → httpx |
| `routers/` | `resumes.py`, `ai.py`, `jobs.py`, `export.py` |
| `tests/` | 128 tests, all green |

### Endpoints

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/api/health` | Liveness + which AI provider will answer |
| GET | `/api/templates` | The 11 recruiter-approved templates |
| GET | `/api/resumes/sample` | Populated demo resume (`?locale=`, `?template=`) |
| GET/POST | `/api/resumes` | List / create |
| GET/PUT/DELETE | `/api/resumes/{id}` | Read / update / delete |
| POST | `/api/resumes/{id}/duplicate` | Duplicate |
| POST | `/api/jobs/import` | Fetch a job advert URL → posting (title, company, description, keywords, **which engine won**) |
| POST | `/api/jobs/tailor` | **Job link / advert text / job title → a CV written for it + its ATS score** |
| GET | `/api/jobs/engines` | Which fetch engines are configured and usable right now |
| POST | `/api/ai/summary` | 55-90 word professional summary |
| POST | `/api/ai/bullets` | Achievement bullets (action verb + metric) |
| POST | `/api/ai/skills` | ATS search terms for the target title |
| POST | `/api/ai/rewrite` | Rewrite a snippet without inventing facts |
| POST | `/api/ai/cover-letter` | 4-paragraph letter, mirrors job-ad keywords (`?save=true`) |
| GET | `/api/ai/cover-letters` | Saved letters |
| POST | `/api/ai/ats-score` | 0-100 score, matched/missing keywords, prioritised fixes |
| POST | `/api/ai/translate` | Section headings in 24 locales (no LLM needed) |
| POST | `/api/ai/draft` | One-line brief → editable resume skeleton |
| POST | `/api/ai/chat` | Freeform CV question |
| GET | `/api/ai/providers` | Which providers are configured |
| GET | `/api/ai/usage` | Calls per feature/provider from `ai_events` |
| POST | `/api/export/pdf` \| `/docx` \| `/txt` | ATS-safe exports of a `Resume` |

### ATS scoring

Fifteen weighted checks (weights sum to 100): contact email/phone/location, headline, summary
presence and length, experience, bullets, quantified metrics (≥40% target), action-verb openers
(≥60% target), first-person pronouns, clichés, six-or-more skills, education, extras.
With a job description the final score is `75% rules + 25% keyword coverage`, so it reflects both
readability and relevance. Grades: A+ ≥90, A ≥80, B ≥70, C ≥60, D ≥50, F below.

### Tests

```powershell
cd backend
python -m pytest -q          # 83 passed
```

`tests/conftest.py` forces `AI_PROVIDER=local`, so the suite never touches the network and is
fully deterministic.

---

## 3. Landing page (`landing/`) — “MyResume Studio”

Next.js 15 (App Router) + React 19 + Tailwind v4 + TypeScript, no UI library.

**Design language (deliberately unlike the reference product):** deep-indigo canvas `#0A0918`
with a warm **coral → rose → violet** gradient (`#FF7A59` → `#FF4D8D` → `#A78BFA`) for the
signature CTA, mint `#5EEAD4` for anything true/success (ATS score, engine online), display
serif headlines, mono labels, film grain and a slow aurora. The reference site is light, teal and
card-heavy; this one is dark, editorial and flat — the CV page itself is the hero visual.

**Eight blocks instead of fourteen** — the whole product is in one panel:

1. **TopBar** — wordmark, four mono links, one gradient CTA, mobile drawer
2. **Hero** — display headline, one-line pitch, two CTAs, proof row, tilted CV sheet
3. **Marquee** — single thin “users hired at …” line
4. **Studio** — *the product*, two tabs against a live CV sheet:
   * **Job → CV** — the headline flow. One input accepts a **job link**, the pasted **advert text**,
     or just a **job title**; `Build my CV` returns a summary, four achievement bullets and a skills
     block written around *that advert's* keywords, plus its ATS score, covered/missing keywords and
     honest notes ("carried 10 skills across — delete any that are not true for you"). One click
     downloads the result as **PDF / DOCX / TXT**.
   * **Style & export** — 11 template chips + 8/24 locales, with live heading translation, and the
     export bar for the current CV.
5. **Toolkit** — all nine tools as one wrapped chip cloud, not nine big cards
6. **Template rail** — horizontal snap-scroll of all 11 templates with CSS-drawn paper previews
7. **Pricing** — three minimal tiers, one highlighted
8. **FAQ + Footer** — five native `<details>` questions, compact three-column footer

```
landing/src/
├─ app/                 layout (dark metadata + fonts), page (block composition), globals.css,
│                       sitemap.ts, robots.ts
├─ components/
│  ├─ shell/            TopBar (client), SiteFooter
│  ├─ hero/             Hero
│  ├─ studio/           Studio, useStudio (state hook), JobToCv, TailorResult, StylePanel,
│  │                    PaperCard (renders a real Resume object)
│  ├─ sections/         AuditRow, Marquee, Toolkit, TemplateRail, PricingTiers, FaqShort
│  └─ shared/           Icon (inline SVG set), Logo, Reveal, StructuredData (JSON-LD)
└─ lib/                 api.ts (typed client + fallback data), content.ts, marketing.ts,
                        seo.ts, templates.ts, types.ts, demo.ts
```

State lives in one hook (`studio/useStudio.ts`) that talks to the API: it loads
`/api/resumes/sample`, translates headings via `/api/ai/translate`, generates copy via
`/api/ai/*` and streams files from `/api/export/*`. If the backend is down the page degrades to the
bundled sample resume (`lib/api.ts`) and the status pill reads *offline mode* — no error states.

```powershell
cd landing
npm run build       # verified: / prerendered as static content
npm run dev         # http://localhost:3000
```

---

## 4. The AI chain works

```
request → ai/engine.py
            └─ ai/runtime.llm_json()
                 ├─ AI_PROVIDER=local?  → offline engine (logged, no network)
                 ├─ provider chain: openrouter → groq → gemini → mistral → cerebras → ollama
                 │     • JSON coerced out of fenced / prose-wrapped responses
                 │     • cached per (feature, payload) for one hour
                 └─ every provider failed or response unparsable → ai/local_engine.py
```

Ollama is only placed in the chain when its daemon actually answers on
`OLLAMA_BASE_URL/api/tags` (probe cached for 60 s), so `auto` mode never burns a connection
attempt on a service that is not running.

The offline engine is honest by construction: it never invents employers, dates or metrics. It
reuses your real achievements and inserts explicit placeholders such as `[X%]`, `[Company]` or
`[team size]` where a number is genuinely required — the “pre-written content you edit” promise
rather than fabrication.

## 4b. Link fetching: the engine chain

A plain HTTP request is blocked by most job boards, so importing a URL walks a chain and reports
which engine answered (`engine`) plus what every other engine said (`attempts`):

| # | Engine | What it does | To enable |
| --- | --- | --- | --- |
| 1 | `ats` | Reads the board's own JSON API when we recognise it (Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee, Personio, Workday) — no bot wall, real fields | nothing (always on) |
| 2 | `scrapegraph` | **ScrapeGraphAI** — hosted API (`SGAI_API_KEY`) or the OSS library against a local LLM | key, or `pip install -r requirements-scraper.txt` + Ollama |
| 3 | `playwright` | Renders JS-heavy boards in headless Chromium | `pip install playwright && playwright install chromium` |
| 4 | `reader` | Markdown reader proxy, good against bot walls | nothing |
| 5 | `http` | Plain request + JSON-LD/meta parsing | nothing (always on) |

Order is set by `SCRAPE_ENGINES`; engines whose dependency or key is missing are skipped
automatically, and one engine crashing never stops the chain. Whatever HTML comes back is parsed
for schema.org `JobPosting` JSON-LD → Open Graph → visible text; markdown results are parsed as
markdown. A page that is really a *job list* (20+ job links, no JSON-LD) is rejected with a clear
message instead of being tailored by mistake.

Measured on a board that 403s a plain request: **playwright rendered and parsed it in ~3.6 s**.

---

## 5. Verified state

| Check | Result |
| --- | --- |
| `python -m pytest -q` (backend) | **111 passed** |
| `npm run build` (landing) | **success**, `/` static, 111 kB First Load JS |
| Live API smoke test | `/api/health`, `/api/jobs/import`, `/api/jobs/tailor`, `/api/ai/summary`, exports all reachable |
| Job-link fetch | a board that 403s a plain request is now parsed in **~3.6 s** via the engine chain; the response names the winning engine and every failed attempt |
| Offline mode (no keys) | every AI endpoint returns `provider: "local"` with real content |
| PDF export | valid `%PDF` … `%%EOF`, all 11 templates and 3 font families |
| DOCX export | valid OOXML zip, localised headings, XML-escaped input |
| Browser render | page is **~5,000 px tall** (was 11,600) and captured at 1440 px — `screenshots/01-hero.jpg` … `05-footer.jpg` |
| SEO endpoints | `/sitemap.xml` (4 URLs) and `/robots.txt` both 200, both prerendered; JSON-LD `WebApplication` + `FAQPage` + `ItemList` in the HTML |

### The redesign (v2)

The first build was structurally faithful to the reference site, which made it look like a clone.
v2 keeps every feature but changes the design language and cuts the page to a third of its length:

* **14 sections → 8 blocks.** Trustpilot grid, 4-step strip, testimonial wall, 6-reasons grid,
  cover-letter section and long-form SEO blocks were removed; that content now lives in the Studio
  tabs, the toolbar chips, the FAQ and the footer.
* **The product is the hero.** Instead of a marketing panel plus a separate builder section, one
  `Studio` panel with **01 Write / 02 Style / 03 Score** tabs sits directly under the hero, next to
  a live CV sheet and a **real PDF / DOCX / TXT export bar**.
* **Different visual identity** — near-black canvas, electric-lime accent, display serif headlines,
  mono labels, grain + aurora. Nothing about it reads as the light teal reference.
* **Simpler interaction** — one job-title input, one Generate button, suggestion chips, a score
  ring; state isolated in `useStudio()`.

Polish carried over from v1 (all still verified):

* **Scroll-reveal hardening** — the hidden pre-animation state is gated behind a `js` class on
  `<html>`, so crawlers, print and no-JS visitors always see content. `hashchange` reveals
  immediately, plus a 5 s failsafe.
* **SEO** — `metadataBase`, `themeColor`, canonical, `applicationName`, `locale`, JSON-LD,
  `sitemap.ts`, `robots.ts`.
* **Accessibility** — skip-to-content link, `aria-hidden` on the duplicated marquee, `aria-pressed`
  on tab/template/locale toggles, `aria-live` on generated output, `prefers-reduced-motion`
  honoured, WCAG-checked lime-on-black CTAs.


## 6. Known limits

* **Port 8000 can be taken on Windows.** On this machine an unrelated `svchost` service already
  holds 8000, so `uvicorn` reports *"access permissions"* when binding. Use another port and point
  the front end at it:
  ```powershell
  python -m uvicorn main:app --reload --port 8010
  # landing/.env.local
  # NEXT_PUBLIC_API_BASE_URL=http://localhost:8010
  ```
  `NEXT_PUBLIC_*` values are inlined at build time, so re-run `npm run build` (or restart
  `npm run dev`) after changing it.
* **PDF + non-Latin scripts.** ReportLab's bundled DejaVu fonts cover Latin, Greek and Cyrillic;
  CJK/Arabic/Persian glyphs fall back to boxes in PDF. Use the DOCX export for those locales
  (Word handles them natively). Headings themselves are translated for all 24 locales.
* **No auth layer yet.** Resumes are stored in SQLite without users; add auth before exposing the
  API publicly. `CORS_ORIGINS` already exists in `.env.example`.
* **Payments are UI-only.** The pricing section mirrors the reference product copy but no billing
  provider is wired up.
* **`FREE_RESUME_LIMIT`** is defined in config but not yet enforced per user.

