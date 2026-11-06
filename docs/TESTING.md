# Testing and Evidence Summary

This summary describes the cases presented in the Hackathon demonstration. **Detailed test logs and source code are not included in this starter package.** Validate any public claims against the original evidence before publishing additional material.

## S2.2 — Skill improvement

The demonstration reports a PASS for fourteen changes restricted to two explicitly allowed files. The report distinguishes simulated scenario time from actual time. Do not extrapolate this result to arbitrary files or environments.

## S10-A — Preview only

A nine-column task preview is prepared without writing data. The preview and the later S10-B write are distinct evidence contexts; IDs, dates, or screenshots must **not** be silently joined into one transaction.

## S10-B — Approved execution

After narrow human approval, a single row is written to the authorized sandbox workbook. Eight cells are changed and the priority field is intentionally left empty. The file is read back from disk and the older rows are checked for unchanged values.

**Reported limitation:** the post-write gate reports `FAIL` on the baseline check. That is part of the recorded one-shot baseline behavior. Do not relabel it `PASS`, even if the workbook data read-back is consistent.

## S18-C — Gate-level negative tests

The matrix contains exactly **six tests**: `G1`, `G2`, `G3`, `G4`, `G5a`, and `G5b`.

- Expected outcome: each test is rejected with exit code `1`.
- Recorded total: `FATAL = 0`.
- Scope: integrity/security **gate-level** checks, not end-to-end agent security assurance.

## Additional demo scenarios

- **DEMO-01:** a distinct write event and independent disk read-back; its deadline differs from the earlier example and must not be collapsed into a single transaction.
- **Duplicate handling:** an attempted duplicate is detected and a new write is rejected in the demonstrated scenario.
- **Past-deadline rule:** the tested case is reported as `BLOCKED`, not as an error or a successful write.

## Evidence and reconstruction convention

`A` = authentic capture; `D` = explanation; `R` = clearly labeled reconstruction from logs. A reconstruction is not original screen-recorded evidence.

## Unverified claims to avoid

- All twenty test cases passed.
- The prototype is production ready.
- Security is proven end-to-end.
- A gate-level check itself enforces operating-system file permissions.
