# PPA Smart Agent

**Controlled Task Execution with Tencent WorkBuddy**  
*AI CAN DO IT Hackathon Indonesia 2026 — The Office Agent*

## Overview

PPA Smart Agent is a **prototype**, built with Tencent WorkBuddy to turn operational work instructions into a process that a human can review, authorize, execute, and verify. Its primary goals are traceability, controlled changes, and evidence-based reporting.

**This repository is a submission documentation package, not a production-ready service.** The tested workflow uses simulated data in an isolated environment.

## The problem

Work instructions often arrive in conversations without consistent project identifiers, priorities, task numbers, or structured logs. This can lead to missed or duplicate entries and changes that are difficult to audit.

## Workflow

`Instruction → Preview → Human approval → Controlled execution → Verification`

1. **Instruction:** interpret an incoming operational message and associate it with the project context.
2. **Preview:** draft a nine-column task entry, without changing the workbook.
3. **Human approval:** require explicit, narrow authorization for a specific write.
4. **Controlled execution:** write only to the allowed test workbook/range.
5. **Verification:** read the workbook back from disk, inspect the change, and record evidence.

## Architecture

A four-layer conceptual model: **instructions**, **knowledge**, **execution**, and **evidence**. See [Architecture](docs/ARCHITECTURE.md).

## Demonstrated scenarios

|Scenario|Evidence-supported observation|Important qualification|
|-|-|-|
|S2.2 — skill refinement|14 changes limited to two authorized files|Test evidence, not full production validation|
|S10-A — task preview|Nine-column preview; no write before approval|Distinct from the later write transaction|
|S10-B — authorized write|Eight cells updated on one row; separate read-back|Post-write baseline gate produced `FAIL` and is reported transparently|
|S18-C — security gate|Six gate-level negative tests produced expected exit code `1`; `FATAL = 0`|This is **not** end-to-end security validation|
|DEMO-01 and follow-on checks|Independent verification, duplicate handling, and past-deadline block explored|Demonstrations and reconstructions are labeled by evidence type|

Details and caveats: [Testing summary](docs/TESTING.md), [Security and limitations](docs/SECURITY.md).

## Evidence labels

* **A — Authentic evidence:** captured results from the test environment.
* **D — Explanation diagram:** conceptual illustration, not a test result.
* **R — Labeled reconstruction:** visualization of recorded logs/test notes, not original screen footage.

## Video demonstration

The demonstration is approximately **6 minutes 30 seconds** and includes Indonesian AI narration. A public video URL will be added after its hosting and access are verified.

## Repository contents

* `docs/ARCHITECTURE.md` — architecture and execution flow
* `docs/TESTING.md` — evidence-based scenario summary
* `docs/SECURITY.md` — security model and limitations
* `docs/SUBMISSION\_CHECKLIST.md` — publication checklist
* `skill/README.md` — status of the skill-source publication

The actual WorkBuddy skill files and selected evidence images will be added **only after reviewing them for credentials, client information, personal data, and third-party rights**. Their absence in this starter package must not be treated as a complete reproducible release.

## Status and scope

**Hackathon prototype / sandbox demonstration. Not ready for production use.** No claim is made that all possible security tests, batch workflows, recovery paths, or unapproved writes have been tested end-to-end.

## License

No license has been selected yet. Do not assume permission to reuse source code or visual assets until the rights and license are explicitly stated.

