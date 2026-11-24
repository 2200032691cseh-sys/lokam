# Architecture decisions awaiting approval

| ID | Proposal | Consequence and confirmation |
|---|---|---|
| ADR-001 | Django 5.2 modular monolith with server-rendered HTML | One deployment and transaction boundary. Validate native Windows/Linux lockfile. |
| ADR-002 | PostgreSQL canonical catalogue, personal relationships and provenance | One database for graph/search/jobs; check extensions, schema constraints and actual query costs. |
| ADR-003 | Private-by-default, authorized media and read-time policy | Publication is explicit; measure media cost and revoke dependent representations. |
| ADR-004 | Bounded PostgreSQL worker | Local jobs first; verify public cadence, lease safety and delivery. |
| ADR-005 | Graph-first discovery with evaluated embeddings | Single-user slice before all domains; pgvector/model choice depends on measured value and rights. |
| ADR-006 | Free development and conditional beta | Public hosting and worker reliability need demonstrated capacity, verified email and recoverable backups. |
| ADR-007 | Optional profile inference | Remains disabled until privacy, isolation, quality and cost gates pass. |

Approval authorizes the architecture direction. The implementation operating rules still require an approved task before code changes. Resolve data rights, hosting region, sender, backup destination, workload, release jurisdiction and staffing in their linked backlog tasks.
