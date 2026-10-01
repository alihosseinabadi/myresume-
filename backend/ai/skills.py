"""Skill ontology: map a job title onto a family of ATS-friendly skills."""

from __future__ import annotations

ROLE_SKILLS: dict[str, list[str]] = {
    "software": [
        "Python", "TypeScript", "React", "Node.js", "REST APIs", "PostgreSQL",
        "Docker", "CI/CD", "Git", "Unit testing", "Cloud (AWS/GCP/Azure)",
        "System design",
    ],
    "data": [
        "SQL", "Python", "Pandas", "dbt", "Airflow", "Tableau", "Power BI",
        "A/B testing", "Statistical modelling", "ETL pipelines",
        "Data warehousing", "Experimentation",
    ],
    "product": [
        "Roadmapping", "User research", "A/B testing", "Jira", "Figma",
        "Stakeholder management", "OKRs", "Product analytics", "Discovery",
        "Go-to-market",
    ],
    "marketing": [
        "SEO", "Content strategy", "Google Analytics", "Paid social",
        "Email automation", "CRM (HubSpot)", "Copywriting", "CRO",
        "Attribution modelling", "Marketing automation",
    ],
    "sales": [
        "Pipeline management", "CRM (Salesforce)", "Prospecting",
        "Negotiation", "Forecasting", "Account planning", "Cold outreach",
        "Upselling", "Quota attainment",
    ],
    "design": [
        "Figma", "Design systems", "Prototyping", "User research",
        "Accessibility (WCAG)", "Interaction design", "Wireframing",
        "Usability testing",
    ],
    "finance": [
        "Financial modelling", "Excel", "Budgeting", "Forecasting",
        "IFRS", "Variance analysis", "Power BI", "Stakeholder reporting",
    ],
    "operations": [
        "Process improvement", "Lean/Six Sigma", "Vendor management",
        "SOP design", "Capacity planning", "KPI reporting", "Inventory control",
    ],
    "support": [
        "Zendesk", "SLA management", "Escalation handling", "Knowledge base",
        "Customer onboarding", "CSAT improvement", "Troubleshooting",
    ],
    "healthcare": [
        "Patient care", "Clinical documentation", "EMR/EHR", "HIPAA",
        "Care coordination", "Triage", "Quality assurance",
    ],
    "education": [
        "Curriculum design", "Lesson planning", "Assessment design",
        "Classroom management", "LMS (Moodle)", "Differentiated instruction",
        "Student mentoring",
    ],
}

# `data` is checked before `engineer`: "Data Engineer" must map to the data
# family (SQL, Spark, dbt…), not to software (React/Node.js).
ROLE_FAMILY_HINTS: dict[str, str] = {
    "data": "data", "analyst": "data", "scientist": "data",
    "engineer": "software", "developer": "software", "programmer": "software",
    "sre": "software", "devops": "software", "qa": "software",
    "product": "product", "pm": "product", "owner": "product",
    "marketing": "marketing", "growth": "marketing", "seo": "marketing",
    "content": "marketing", "brand": "marketing",
    "sales": "sales", "account": "sales", "business development": "sales",
    "designer": "design", "ux": "design", "ui": "design", "researcher": "design",
    "finance": "finance", "accountant": "finance", "auditor": "finance",
    "controller": "finance", "treasury": "finance",
    "operations": "operations", "logistics": "operations", "supply": "operations",
    "support": "support", "success": "support", "service": "support",
    "nurse": "healthcare", "doctor": "healthcare", "clinical": "healthcare",
    "physician": "healthcare", "pharmac": "healthcare",
    "teacher": "education", "tutor": "education", "lecturer": "education",
    "instructor": "education", "professor": "education",
}


def family_for_role(job_title: str) -> str:
    """Map a free-text job title onto a family key in ``ROLE_SKILLS``."""
    lowered = (job_title or "").lower()
    for hint, family in ROLE_FAMILY_HINTS.items():
        if hint in lowered:
            return family
    return "operations"


# Every concrete tool/method the ontology knows about, lower-cased. Used to
# recognise genuine technical terms inside a job advert.
KNOWN_SKILL_TERMS: set[str] = {skill.lower() for group in ROLE_SKILLS.values() for skill in group}

# Widely demanded technologies the role ontology does not enumerate per family.
# Maps lower-case term -> the casing a CV should print ("sql" -> "SQL").
# Used to (a) recognise real skills in advert text and (b) print them properly.
TECH_TERMS: dict[str, str] = {
    # data / engineering stack
    "spark": "Spark", "pyspark": "PySpark", "kafka": "Kafka", "flink": "Flink",
    "scala": "Scala", "java": "Java", "kotlin": "Kotlin", "clickhouse": "ClickHouse",
    "kubernetes": "Kubernetes", "docker": "Docker", "hadoop": "Hadoop", "hdfs": "HDFS",
    "yarn": "YARN", "hive": "Hive", "hbase": "HBase", "zookeeper": "ZooKeeper",
    "iceberg": "Iceberg", "delta lake": "Delta Lake", "hudi": "Hudi",
    "airflow": "Airflow", "dbt": "dbt", "prefect": "Prefect", "dagster": "Dagster",
    "snowflake": "Snowflake", "databricks": "Databricks", "bigquery": "BigQuery",
    "redshift": "Redshift", "synapse": "Synapse", "vertica": "Vertica",
    "etl": "ETL", "elt": "ELT", "elt pipelines": "ELT pipelines", "etl pipelines": "ETL pipelines",
    "dwh": "DWH", "data lake": "Data Lake", "data warehouse": "Data Warehouse",
    "data warehousing": "Data warehousing", "scd": "SCD", "cdc": "CDC",
    "data quality": "Data Quality", "data governance": "Data Governance",
    "streaming": "Streaming", "batch processing": "Batch Processing",
    "sql": "SQL", "t-sql": "T-SQL", "pl/sql": "PL/SQL", "mysql": "MySQL",
    "postgresql": "PostgreSQL", "oracle": "Oracle", "sql server": "SQL Server",
    "mongodb": "MongoDB", "redis": "Redis", "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch", "neo4j": "Neo4j", "clickhouse db": "ClickHouse",
    "s3": "S3", "gcs": "GCS", "azure": "Azure", "aws": "AWS", "gcp": "GCP",
    "terraform": "Terraform", "ansible": "Ansible", "jenkins": "Jenkins",
    "gitlab": "GitLab", "github": "GitHub", "bitbucket": "Bitbucket",
    "grafana": "Grafana", "prometheus": "Prometheus", "splunk": "Splunk",
    "datadog": "Datadog", "superset": "Superset", "looker": "Looker",
    "metabase": "Metabase", "power bi": "Power BI", "tableau": "Tableau",
    "excel": "Excel", "vba": "VBA",
    # engineering practice
    "bash": "Bash", "shell": "Shell scripting", "powershell": "PowerShell",
    "linux": "Linux", "unix": "Unix", "git": "Git", "ci/cd": "CI/CD",
    "devops": "DevOps", "frontend": "Frontend", "backend": "Backend",
    "oop": "OOP", "solid": "SOLID", "tdd": "TDD", "bdd": "BDD",
    "microservices": "Microservices", "rest": "REST", "restful": "RESTful",
    "graphql": "GraphQL", "grpc": "gRPC", "oauth": "OAuth", "jwt": "JWT",
    "unit testing": "Unit testing", "integration testing": "Integration testing",
    "code review": "Code review", "system design": "System design",
    "scrum": "Scrum", "kanban": "Kanban", "agile": "Agile",
    "pytest": "pytest", "unittest": "unittest", "selenium": "Selenium",
    "playwright": "Playwright", "jira": "Jira", "confluence": "Confluence",
    # programming languages & web
    "python": "Python", "typescript": "TypeScript", "javascript": "JavaScript",
    "c#": "C#", "c++": "C++", "go": "Go", "golang": "Go", "rust": "Rust",
    "ruby": "Ruby", "php": "PHP", "swift": "Swift", "r": "R",
    "html": "HTML", "css": "CSS", "react": "React", "vue": "Vue",
    "angular": "Angular", "next.js": "Next.js", "node.js": "Node.js",
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI",
    "spring": "Spring", ".net": ".NET",
    # ml / ai
    "numpy": "NumPy", "pandas": "Pandas", "scikit-learn": "scikit-learn",
    "tensorflow": "TensorFlow", "pytorch": "PyTorch", "keras": "Keras",
    "xgboost": "XGBoost", "opencv": "OpenCV", "nltk": "NLTK", "spacy": "spaCy",
    "mlflow": "MLflow", "langchain": "LangChain", "llm": "LLM",
    "machine learning": "Machine Learning", "deep learning": "Deep Learning",
    "nlp": "NLP", "computer vision": "Computer Vision",
    "a/b testing": "A/B testing", "experimentation": "Experimentation",
    "statistical modelling": "Statistical modelling",
}

# Lower-case term -> the way it should be printed on a CV.
SKILL_DISPLAY: dict[str, str] = {
    **{skill.lower(): skill for group in ROLE_SKILLS.values() for skill in group},
    **TECH_TERMS,
}

KNOWN_SKILL_TERMS |= set(TECH_TERMS)

FAMILY_LABELS: dict[str, str] = {
    "software": "software engineering",
    "data": "analytics and data",
    "product": "product",
    "marketing": "marketing",
    "sales": "sales",
    "design": "design",
    "finance": "finance",
    "operations": "operations",
    "support": "customer support",
    "healthcare": "healthcare",
    "education": "education",
}


def family_label(family: str) -> str:
    """A human phrase for a family, so summaries read naturally."""
    return FAMILY_LABELS.get(family, "the sector")
