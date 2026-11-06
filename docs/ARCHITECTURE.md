# Architecture — PPA Smart Agent

## Conceptual layers

1. **Instructions:** interpret operational requests and extract task context.
2. **Knowledge:** use project-specific references and permitted context to assemble a draft.
3. **Execution:** carry out an explicitly authorized change within the allowed workbook/range.
4. **Evidence:** preserve the preview, approval scope, file changes, and independent read-back.

```text
Incoming instruction
       |
       v
Project/task context
       |
       v
Nine-column draft preview (no write)
       |
       v
Explicit human approval for one permitted operation
       |
       v
Controlled write to sandbox workbook
       |
       v
Save, checksum/diff, read-back from disk
       |
       v
Evidence and limitation report
```

## Key invariants demonstrated

- A preview is not a write.
- Approval is scoped to a particular test file, row, and set of columns.
- Protected master/reference files are outside the approved modification scope.
- Evidence is checked from disk after execution rather than relying only on an agent's written claim.

## What this diagram does not imply

This is an **explanatory diagram**, not a complete executable system map. The prototype does not claim an independently enforced access-control boundary, a production-grade authorization policy, or exhaustive security coverage.
