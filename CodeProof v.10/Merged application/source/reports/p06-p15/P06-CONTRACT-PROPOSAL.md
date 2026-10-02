# P06 controlled incidents: contract proposal

CURRENT: Connected challenges accept issue and target_file after AI analysis and describe an existing issue. They do not inject failures. Practice mode is simulated.

REQUEST: Add three deterministic incidents for a repository-owned Python training fixture. The external dummy remains ordinary investigation unless it matches an explicitly supported fixture; never assume its authentication is broken.

| Incident | Educational goal | Exact prerequisite | Injected failure |
|---|---|---|---|
| request-field | Trace request schema to authentication lookup | Approved fixture baseline manifest | Read an absent credential field instead of username |
| date-serialization | Convert boundary values to JSON primitives | Approved fixture baseline manifest | Return datetime instead of ISO-formatted text |
| database-init | Understand schema initialization before query | Approved fixture baseline manifest | Omit SQLite table initialization |

WHY: Make the three advertised challenges reproducible and bind AI coaching to a real failure while preserving the original-project guarantee.

AFFECTED COMPONENTS: backend session orchestration/models (Friend 3), Flutter challenge selection/models (Friend 1), fixture/product content (Friend 2); AI receives existing ChallengeContext and ProjectSnapshot types (Project Lead).

REQUIRED CHANGES:
- Add optional incident_id to ChallengeRequest; retain existing issue/target_file requests.
- Add optional active_incident and supported_incidents to SessionView with typed id/title/goal/target fields. Old sessions remain valid with empty defaults.
- Offer controlled incidents only for the exact supported healthy training fixture. Refuse unknown ids, changed prerequisites, wrong session phase or non-owned copies.
- Create the injected snapshot in a fresh registered temporary copy transactionally. Update the session snapshot, displayed files and coaching context together. Do not execute target code on the host.
- Bind relevant files and expected concepts to the selected incident. Keep all four progressive hints and the approved CORRECT plus score >=0.7 patch gate. A new explanation revokes old permission.
- Restore by closing and reopening the session from the unchanged original fixture; dispose only of that session's owned copy. No filesystem reset API is added.
- Use Docker to establish healthy baseline, injected failure and repaired success for each incident. Test rejection, ownership, teardown, deterministic bytes and before/after original hashes.

RISKS: Stale snapshot/context, partial copy creation and overly broad target matching. Fail closed on exact prerequisite mismatch; publish a new copy only after successful registration; preserve existing investigation behavior. No target dependencies or credentials are needed for the stdlib fixture.

RECOMMENDATION: Approve this additive contract and the bundled training fixture. It changes no existing AI response schema and no Docker execution policy. Native UI and real-provider quality must still be verified separately from deterministic fixtures.

Status: proposal only; no P06 shared contracts implemented yet.
