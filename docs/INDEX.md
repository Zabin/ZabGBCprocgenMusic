# Docs — Master router

All prose documentation for **Driftune**, organized by pipeline stage (see
[`.claude/skills/README.md`](../.claude/skills/README.md) for the pipeline itself and
[`ROADMAP.md`](../ROADMAP.md) for per-document status). Every directory has its own `INDEX.md`;
statuses live there and in the ROADMAP, kept in sync by the owning skill.

This pipeline and toolchain foundation are harvested from a separate reference project (see
`docs/master/MSTR-001-program-vision.md` §0 for exactly what's reused vs. rebuilt). This is a
from-scratch increment — there is no shipped ROM yet, so every index below starts `⛔ Planned`
except what this session authors.

| Directory | Contents | Owning skill(s) |
|---|---|---|
| [`pipeline/`](pipeline/BOOTSTRAP.md) | The run-book ([BOOTSTRAP.md](pipeline/BOOTSTRAP.md)), the manager's journal ([pipeline-journal.md](pipeline/pipeline-journal.md)), backlog ([backlog.md](pipeline/backlog.md)) | `00-pipeline-manager`, `00-intake` |
| [`master/`](master/INDEX.md) | Program-level MSTR documents (vision, governance, …) | `01-vision` (+ `03`) |
| [`research/`](research/INDEX.md) | Encyclopedia tiers R100 (GBC hardware, esp. sound) / R200 (generative-music design) / R300 (tooling & verification) | the three `02-research-*` skills |
| [`architecture/`](architecture/INDEX.md) | The GDS-00…10 ladder, ADS clusters, ADRs, assumptions register | `03-architecture-design-synthesis` (+ `01-vision` for GDS-00) |
| [`requirements/`](requirements/INDEX.md) | FR/NFR baselines, Requirements Review, RTM | `04-requirements-engineering` |
| [`feature-planning/`](feature-planning/INDEX.md) | Release plan, epic/feature catalogs (FEAT-xxxx), dependency graph, feature review | `05-feature-decomposition` |
| [`features/`](features/INDEX.md) | Full Feature Specifications (FS-xxx) | `06-feature-specification` |
| [`implementation/`](implementation/00-master-build-plan.md) | Master Build Plan, TWBS, packages (IP-xxxx), verification reports (VR-xxxx) | `07-implementation-planning`, stage-08 peers, `09-package-verification` |
| [`reviews/`](reviews/INDEX.md) | Content reviews, integration reviews, release assessments | `09-content-review`, `10-integration-review`, `11-release-readiness` |

Repo-root working docs: `Claude.md` (developer quick-reference) and `memory.md` (runtime notes &
quick-reference tables), maintained the same way as the reference project's.
