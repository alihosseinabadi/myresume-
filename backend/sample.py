"""A realistic, fully-populated resume used for previews, demos and tests."""

from __future__ import annotations

from models import (
    CertificationItem,
    EducationItem,
    ExperienceItem,
    LanguageItem,
    PersonalInfo,
    ProjectItem,
    Resume,
    SkillGroup,
)


def sample_resume(locale: str = "en", template: str = "athens") -> Resume:
    return Resume(
        id="sample-resume",
        title="Senior Data Analyst - sample",
        template=template,
        locale=locale,
        accent_color="#0F766E",
        personal=PersonalInfo(
            full_name="Alex Morgan",
            headline="Senior Data Analyst | Experimentation & Reporting",
            email="alex.morgan@example.com",
            phone="+44 7700 900123",
            location="London, UK",
            linkedin="linkedin.com/in/alexmorgan",
            github="github.com/alexmorgan",
        ),
        summary=(
            "Senior Data Analyst with 6+ years in fintech and marketplaces, focused on "
            "experimentation, self-serve reporting and forecasting. Built the A/B testing "
            "framework now used by four product squads, cutting read-out time from two weeks "
            "to three days. Partnered with finance to rebuild revenue forecasting, reducing "
            "monthly variance from 11% to 3%. Now targeting analytics leadership roles where "
            "evidence drives roadmap decisions."
        ),
        experience=[
            ExperienceItem(
                role="Senior Data Analyst",
                company="Payflow",
                location="London, UK",
                start_date="2022-03",
                end_date="",
                current=True,
                bullets=[
                    "Built the A/B testing framework in dbt and Airflow, adopted by 4 product squads and cutting experiment read-out time from 14 days to 3.",
                    "Rebuilt revenue forecasting with finance, reducing monthly variance from 11% to 3% on GBP 48M of annual volume.",
                    "Led a churn model that flagged 2,300 at-risk accounts per quarter, supporting retention campaigns worth GBP 1.2M.",
                    "Mentored 3 junior analysts and introduced SQL review standards that cut rework by 35%.",
                ],
            ),
            ExperienceItem(
                role="Data Analyst",
                company="Marketa",
                location="Manchester, UK",
                start_date="2019-06",
                end_date="2022-02",
                bullets=[
                    "Automated 20+ recurring reports in Python and Tableau, saving 25 analyst hours per month.",
                    "Designed the customer segmentation model used to prioritise outbound sales, lifting conversion 18%.",
                    "Instrumented campaign tracking with marketing, improving attribution coverage from 62% to 94%.",
                ],
            ),
        ],
        education=[
            EducationItem(
                degree="MSc Data Science",
                school="University of Manchester",
                location="Manchester, UK",
                start_date="2017-09",
                end_date="2019-05",
                description="Dissertation: demand forecasting for on-demand logistics.",
            ),
            EducationItem(
                degree="BSc Mathematics",
                school="University of Leeds",
                location="Leeds, UK",
                start_date="2014-09",
                end_date="2017-06",
            ),
        ],
        skills=[
            SkillGroup(
                name="Data & tooling",
                skills=["SQL", "Python", "dbt", "Airflow", "Tableau", "Power BI", "BigQuery", "Looker"],
            ),
            SkillGroup(
                name="Methods",
                skills=["A/B testing", "Causal inference", "Forecasting", "Segmentation", "Data modelling"],
            ),
            SkillGroup(
                name="Collaboration",
                skills=["Stakeholder management", "Mentoring", "Roadmap prioritisation"],
            ),
        ],
        projects=[
            ProjectItem(
                name="Open revenue analytics",
                link="github.com/alexmorgan/revenue-analytics",
                description="Open-source dbt package for subscription revenue reporting.",
            )
        ],
        certifications=[
            CertificationItem(name="Google Advanced Data Analytics", issuer="Google", date="2023"),
            CertificationItem(name="dbt Analytics Engineering", issuer="dbt Labs", date="2022"),
        ],
        languages=[
            LanguageItem(name="English", level="Native"),
            LanguageItem(name="Spanish", level="B1"),
        ],
    )
