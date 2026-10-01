"""Throwaway probe: what does the link chain actually read, per board?

Run from the repo root:  python probe_jobs.py
"""

from __future__ import annotations

import json
import sys

sys.path.insert(0, "backend")

from config import settings  # noqa: E402
from models import TailorRequest  # noqa: E402
from services.job_import import fetch_job  # noqa: E402
from services.scrapers import engines_status  # noqa: E402
from ai.tailor import tailor_resume  # noqa: E402

URLS = [
    "https://boards.greenhouse.io/crunchyroll/jobs/8211106?gh_jid=8211106",
    "https://jobs.lever.co/hatchit/18541acc-71ff-4a4e-8964-5cbd4650acf9",
    "https://jobs.workable.com/view/eGbn98jyCCEi8kjrkeJjMQ/remote-senior-backend-engineer-in-dallas-at-steer-health",
    "https://staff-emory.icims.com/jobs/164209/senior-systems-software-engineer-%28backend-engineer%29---school-of-nursing/job",
    "https://www.linkedin.com/jobs/view/4000000000/",
]


def main() -> None:
    print(f"SCRAPE_ENGINES = {settings.scrape_engines}")
    for row in engines_status():
        print(f"  engine {row['engine']:<12} ready={row['ready']:<5} enabled={row['enabled']:<5} {row['detail']}")

    for url in URLS:
        print("\n" + "=" * 78)
        print(f"URL: {url}")
        job = fetch_job(url)
        print(f"  won={job.engine!r} source={job.source!r} ok={job.ok}")
        print(f"  title={job.title!r}")
        print(f"  company={job.company!r} location={job.location!r}")
        print(f"  description {len(job.description)} chars")
        print(f"  keywords={job.keywords[:12]}")
        print(f"  message={job.message[:160]!r}")
        print(f"  attempts={job.attempts}")
        if job.description:
            print(f"  head: {job.description[:220]!r}")

        res = tailor_resume(TailorRequest(url=url, template="athens", locale="en"))
        r = res.resume
        print("  --- generated CV ---")
        print(f"  headline={r.personal.headline!r}")
        print(f"  summary={r.summary!r}")
        for item in r.experience:
            print(f"  experience: role={item.role!r} company={item.company!r} location={item.location!r}")
            for b in item.bullets:
                print(f"    - {b}")
        for group in r.skills:
            print(f"  skills({group.name})={group.skills}")
        print(f"  notes={res.notes}")
        print(f"  missing={res.missing_keywords[:10]}")


if __name__ == "__main__":
    main()
