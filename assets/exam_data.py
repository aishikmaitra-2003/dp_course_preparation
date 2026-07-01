"""
DP-700 Exam — Complete Module & Syllabus Data
10-day study plan mapped to official exam objectives.
"""

MODULES = [
    {
        "id": 1,
        "day": 1,
        "title": "Ingest Data — Pipelines",
        "icon": "🔄",
        "weight": "~15%",
        "description": "Data pipelines, Copy Activity, triggers, parameterization, and orchestration in Microsoft Fabric.",
        "topics": [
            "Data Pipeline concepts in Fabric",
            "Copy Activity — source & sink configs",
            "Pipeline triggers (scheduled, tumbling window, event-based)",
            "Pipeline parameters and expressions",
            "Lookup, ForEach, If Condition activities",
            "Pipeline monitoring and error handling",
            "Pipeline templates and best practices",
        ],
        "key_concepts": [
            "Copy Activity vs Dataflow vs Notebook",
            "Expression language (@pipeline().parameters)",
            "Incremental load patterns",
            "Pipeline retry policies",
        ],
        "exam_tips": [
            "Know the difference between Copy Activity and Dataflow Gen2 — Copy is for simple ETL, Dataflow for complex transformations",
            "Pipeline variables vs parameters — parameters are set at trigger time, variables change during execution",
            "Event-based triggers watch for blob creation/deletion events",
        ],
    },
    {
        "id": 2,
        "day": 2,
        "title": "Ingest Data — Dataflows & Shortcuts",
        "icon": "🌊",
        "weight": "~10%",
        "description": "Dataflows Gen2, Power Query Online, OneLake shortcuts, and database mirroring.",
        "topics": [
            "Dataflows Gen2 — architecture and use cases",
            "Power Query Online transformations",
            "Data destinations in Dataflows Gen2",
            "OneLake shortcuts (ADLS, S3, GCS, Dataverse)",
            "Database mirroring (Azure SQL, Cosmos DB, Snowflake)",
            "Staging lakehouse in Dataflows",
            "Incremental refresh in Dataflows",
        ],
        "key_concepts": [
            "Dataflows Gen2 vs Gen1 — Gen2 writes to Lakehouse/Warehouse",
            "Shortcuts = virtual pointers (no data copy)",
            "Mirroring = continuous replication",
            "Fast copy vs standard copy in Dataflows",
        ],
        "exam_tips": [
            "Shortcuts DO NOT copy data — they're live references. Mirroring DOES replicate data.",
            "Dataflows Gen2 can output to Lakehouse, Warehouse, or KQL Database",
            "Know when to use shortcuts vs mirroring vs Copy Activity",
        ],
    },
    {
        "id": 3,
        "day": 3,
        "title": "Transform Data — Spark & PySpark",
        "icon": "⚡",
        "weight": "~15%",
        "description": "PySpark notebooks, Delta Lake operations, Spark configs, and V-Order optimization.",
        "topics": [
            "Fabric Spark notebooks — architecture",
            "PySpark DataFrame operations (read, transform, write)",
            "Delta Lake — ACID transactions, time travel",
            "Delta table MERGE, UPDATE, DELETE",
            "V-Order optimization (read-optimized parquet)",
            "Spark session configuration",
            "Notebook scheduling and parameterization",
            "High-concurrency mode vs standard sessions",
            "Fabric Runtime and Spark pools",
        ],
        "key_concepts": [
            "Delta Lake = open-source storage layer for ACID on data lakes",
            "V-Order = Fabric's special parquet optimization for faster reads",
            "OPTIMIZE and VACUUM commands",
            "mssparkutils — Fabric notebook utilities",
        ],
        "exam_tips": [
            "V-Order is applied by default in Fabric — it's a write-time optimization",
            "OPTIMIZE compacts small files into larger ones (bin-packing)",
            "VACUUM removes files older than retention period (default 7 days)",
            "Know the Delta Lake MERGE syntax — very commonly tested!",
        ],
    },
    {
        "id": 4,
        "day": 4,
        "title": "Transform Data — T-SQL & KQL",
        "icon": "📊",
        "weight": "~10%",
        "description": "T-SQL in Fabric Warehouses, KQL in Eventhouse/KQL databases, stored procedures.",
        "topics": [
            "T-SQL in Fabric Warehouse vs SQL Analytics Endpoint",
            "CREATE TABLE, CTAS (CREATE TABLE AS SELECT)",
            "Stored procedures in Warehouse",
            "Cross-database and cross-warehouse queries",
            "KQL (Kusto Query Language) basics",
            "KQL Database and Eventhouse concepts",
            "Real-time data ingestion with KQL",
            "Materialized views in KQL",
        ],
        "key_concepts": [
            "Warehouse = full DML (INSERT, UPDATE, DELETE)",
            "SQL Analytics Endpoint = read-only T-SQL on Lakehouse",
            "KQL for real-time/streaming analytics",
            "CTAS is the most efficient way to create tables in Warehouse",
        ],
        "exam_tips": [
            "SQL Analytics Endpoint is AUTO-GENERATED for every Lakehouse — you can't create tables through it!",
            "Warehouse supports stored procedures; Lakehouse SQL endpoint does NOT",
            "KQL uses pipe (|) syntax: TableName | where Timestamp > ago(1h) | count",
        ],
    },
    {
        "id": 5,
        "day": 5,
        "title": "Design — Lakehouse Architecture",
        "icon": "🏠",
        "weight": "~10%",
        "description": "Lakehouse design, medallion architecture, file formats, Delta tables, and OneLake.",
        "topics": [
            "Lakehouse architecture in Fabric",
            "OneLake — unified data lake",
            "Medallion architecture (Bronze → Silver → Gold)",
            "File formats: Parquet, Delta, CSV, JSON",
            "Managed vs external tables",
            "Lakehouse file structure (Files/ vs Tables/)",
            "Schema enforcement and evolution",
            "Data partitioning strategies",
        ],
        "key_concepts": [
            "OneLake = single data lake for the entire Fabric tenant",
            "Bronze = raw, Silver = cleaned, Gold = business-ready",
            "Tables/ folder = managed Delta tables",
            "Files/ folder = unmanaged files (any format)",
        ],
        "exam_tips": [
            "Medallion architecture is THE go-to pattern — know it cold!",
            "Partition by commonly filtered columns (e.g., date, region)",
            "Don't over-partition! Too many small partitions = bad performance",
        ],
    },
    {
        "id": 6,
        "day": 6,
        "title": "Design — Warehouse & Data Modeling",
        "icon": "🏗️",
        "weight": "~10%",
        "description": "Fabric Warehouse design, star schema, dimension/fact tables, and cross-database queries.",
        "topics": [
            "Fabric Warehouse vs Lakehouse — when to use which",
            "Star schema design (facts + dimensions)",
            "Slowly Changing Dimensions (SCD Type 1, 2)",
            "Surrogate keys vs natural keys",
            "Table distribution and indexing",
            "Cross-database queries in Fabric",
            "Data Warehouse loading patterns",
            "Warehouse schemas (dbo, custom)",
        ],
        "key_concepts": [
            "Warehouse = structured, SQL-first, BI-optimized",
            "Lakehouse = flexible, Spark-first, data engineering",
            "SCD Type 1 = overwrite, Type 2 = add new row with version",
            "Star schema = central fact table + surrounding dimension tables",
        ],
        "exam_tips": [
            "Use Warehouse when you need full T-SQL DML and stored procedures",
            "Use Lakehouse when you need Spark notebooks and file-based processing",
            "Cross-database queries work across Warehouses AND Lakehouses!",
        ],
    },
    {
        "id": 7,
        "day": 7,
        "title": "Security & Governance",
        "icon": "🔒",
        "weight": "~10%",
        "description": "Workspace roles, RLS, CLS, sensitivity labels, OneSecurity, and data governance.",
        "topics": [
            "Workspace roles (Admin, Member, Contributor, Viewer)",
            "Row-Level Security (RLS) implementation",
            "Column-Level Security (CLS)",
            "Object-Level Security (OLS)",
            "Sensitivity labels (Microsoft Purview)",
            "OneLake data access roles",
            "Item permissions vs workspace permissions",
            "Data governance best practices",
        ],
        "key_concepts": [
            "Workspace roles hierarchy: Admin > Member > Contributor > Viewer",
            "RLS = filter rows based on user identity (DAX filters)",
            "CLS = restrict column access (GRANT/DENY in Warehouse)",
            "Sensitivity labels flow downstream through Fabric items",
        ],
        "exam_tips": [
            "RLS is defined differently in Semantic Models (DAX) vs Warehouse (T-SQL)",
            "Contributors can create items but can't manage workspace settings",
            "OneLake data access roles provide FOLDER-level security in Lakehouse",
        ],
    },
    {
        "id": 8,
        "day": 8,
        "title": "Monitor & Optimize",
        "icon": "📈",
        "weight": "~10%",
        "description": "Monitoring Hub, Capacity Metrics, query optimization, caching, and performance tuning.",
        "topics": [
            "Monitoring Hub in Fabric",
            "Microsoft Fabric Capacity Metrics app",
            "Capacity Units (CUs) and throttling",
            "Spark job optimization (partitioning, caching, broadcast joins)",
            "Warehouse query optimization (statistics, result set caching)",
            "Pipeline run monitoring and debugging",
            "Apache Spark UI and job analysis",
            "Autoscale and burst capacity",
        ],
        "key_concepts": [
            "CU = Capacity Unit (billing unit for Fabric)",
            "Smoothing = Fabric spreads CU usage over 24 hours",
            "Throttling happens when you exceed capacity limits",
            "Result set caching = auto-caches repeated queries in Warehouse",
        ],
        "exam_tips": [
            "Monitoring Hub shows ALL Fabric item runs in one place",
            "Know the Spark UI tabs: Jobs, Stages, Storage, SQL",
            "Statistics are auto-created in Warehouse but can be manually updated",
        ],
    },
    {
        "id": 9,
        "day": 9,
        "title": "End-to-End & CI/CD",
        "icon": "🔗",
        "weight": "~5%",
        "description": "Integration scenarios, Git integration, deployment pipelines, and CI/CD workflows.",
        "topics": [
            "Git integration in Fabric workspaces",
            "Deployment pipelines (Dev → Test → Prod)",
            "Deployment rules and parameter overrides",
            "End-to-end data engineering scenarios",
            "Connecting all Fabric items together",
            "Lifecycle management best practices",
            "Automation with Fabric REST APIs",
        ],
        "key_concepts": [
            "Git integration = source control for Fabric items",
            "Deployment pipelines = promote items across stages",
            "Deployment rules = change data sources/connections per stage",
            "REST APIs for programmatic management",
        ],
        "exam_tips": [
            "Git integration supports Azure DevOps AND GitHub",
            "Deployment pipelines can only deploy SUPPORTED item types",
            "Not all item types support deployment pipelines — know which ones do!",
        ],
    },
    {
        "id": 10,
        "day": 10,
        "title": "🏆 Final Mock Exam",
        "icon": "🏆",
        "weight": "100%",
        "description": "Full-length mock exam covering ALL modules. 60 questions, 90 minutes. Let's see if you're ready!",
        "topics": [
            "All topics from Days 1-9",
            "Cross-domain scenario questions",
            "Code interpretation (PySpark, T-SQL, KQL)",
            "Architecture decision questions",
            "Security implementation scenarios",
            "Monitoring and troubleshooting scenarios",
        ],
        "key_concepts": [
            "This is the real deal — treat it like the actual exam",
            "Time management: ~1.5 minutes per question",
            "Read ALL options before selecting an answer",
            "Eliminate obviously wrong answers first",
        ],
        "exam_tips": [
            "The real exam is 40-60 questions in 120 minutes",
            "No penalty for guessing — never leave a question blank!",
            "Scenario-based questions are worth reading carefully",
        ],
    },
]


def get_module(module_id: int) -> dict:
    """Get a specific module by ID."""
    for m in MODULES:
        if m["id"] == module_id:
            return m
    return None


def get_all_modules() -> list:
    """Get all modules."""
    return MODULES


def get_module_context(module_id: int) -> str:
    """Get a formatted string of module context for AI prompts."""
    module = get_module(module_id)
    if not module:
        return "General DP-700 exam topics"

    context = f"## Module: {module['title']} (Day {module['day']})\n"
    context += f"**Weight:** {module['weight']}\n\n"
    context += "### Topics:\n"
    for t in module["topics"]:
        context += f"- {t}\n"
    context += "\n### Key Concepts:\n"
    for c in module["key_concepts"]:
        context += f"- {c}\n"
    context += "\n### Exam Tips:\n"
    for tip in module["exam_tips"]:
        context += f"- 🎯 {tip}\n"
    return context
