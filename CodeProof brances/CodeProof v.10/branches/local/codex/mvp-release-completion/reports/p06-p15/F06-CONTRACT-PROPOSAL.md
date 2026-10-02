# F06 — evaluation contract proposal (approval required)

Status: investigated; implementation has NOT started. Worktree inspected: C:\Codeproof-fix-ai-setup (codex/fix-ai-setup). Original checkout preserved. This proposal includes the existing P01/P02 fixes as the starting point; no source changes, branch operations or provider requests in this task.

CURRENT:
- AI already supplies ExplanationClassification enum CORRECT/PARTIALLY_CORRECT/INCORRECT, bounded 0..1 score, feedback and passed in ai/models/explanation.py.
- ai/services/explanation_evaluator.py discards the provider passed decision but recomputes it from score alone. A PARTIALLY_CORRECT or INCORRECT result with score >= 0.7 can therefore pass. The prompt also hardcodes 0.7 rather than using the evaluator's configured threshold.
- backend/services/sessions.py drops classification when constructing backend/session_models.py Evaluation. Connected API returns only passed/feedback/score under SessionView.evaluation.
- Passing evaluation immediately triggers patch generation and phase=review. Applying requires review + patch + evaluation.passed. There is no three-way classification check.
- A malformed provider result fails before new state is published. If the session already has an accepted explanation/patch, that previous review state remains. A failed re-evaluation can therefore leave an old patch approval available.
- Dart domain/workspace.dart parses the three fields and canReview checks patch + passed. coach.dart shows only two headings and feedback; score is parsed but not displayed. evidence.dart uses passed for the Cause explained readiness check. practice_service.dart constructs the same Evaluation type using local keyword simulation.
- Separate legacy backend/services/challenge_service.py marks partial explanations passed. Separate demo_fixtures.py has a stale patch_unlocked flag after a previously correct answer is followed by a weaker answer. These are deterministic demo/legacy paths, not live quality evidence.

REQUEST — smallest compatible wire change:
Add ONE field, classification, to the connected SessionView.evaluation object. It uses the existing AI enum strings. Keep passed, feedback, score, response envelopes, endpoint paths, request bodies and phase names unchanged. No new endpoint or provider interface is required.

Example updated response fragment:
{
  "evaluation": {
    "classification": "PARTIALLY_CORRECT",
    "score": 0.65,
    "feedback": "You identified the affected boundary but omitted the cause.",
    "passed": false
  },
  "patch": null,
  "phase": "investigating"
}

Server policy:
passed = classification == CORRECT AND finite score >= configured passing_threshold (default 0.7).
The server owns this derived field. Provider passed=true cannot override classification or threshold. A CORRECT answer below the existing threshold still cannot unlock patching.

Required changes:
1. AI model/evaluator: retain enum and existing output shape; strictly reject invalid/nonfinite/out-of-range scores, unknown/missing classification and empty feedback; reject malformed JSON through production provider parsing. Correct the prompt and derive passed from classification plus threshold. No new classification inferred from keywords or score.
2. Backend typed session Evaluation: add required classification and bound score; map the AI classification without loss. Connected explain and apply gates require the classification/score policy as well as the existing investigation/review/patch requirements. Revoke previous evaluation/patch approval at the start of a new explanation attempt, so malformed output or patch-generation failure cannot preserve stale approval. Errors remain sanitized, non-success responses; no new error contract.
3. Dart domain: add typed classification enum and parse known values. For legacy payloads without this additive field, preserve the old boolean behavior and generic two-way label; do not pretend a missing classification is a real three-way judgment. Unknown explicit classification is rejected. The new backend always supplies classification; its gates remain authoritative.
4. Dart UI: show Correct / Partially correct / Incorrect, score percentage and feedback; only a passing CORRECT result enables review. Keep explanation-before-patch and server application checks. Missing-field fallback is for old backend compatibility only and does not certify the old backend's classification safety.
5. Dart practice and backend demo/legacy paths: supply explicit simulated classifications where consumed by the new Dart type; ensure partial/incorrect do not pass or retain stale unlocks. Preserve their existing response shapes and simulation labels. No keyword-demo result is reported as real evaluation quality.

WHY:
The classification already exists upstream. Its loss makes the desktop binary and permits score-only authorization inconsistent with the three-way grading requirement. An additive field avoids renaming or removing current consumer fields; retaining the 0.7 threshold avoids weakening the existing explanation gate.

AFFECTED COMPONENTS / OWNERS:
- AI Engine and evaluation models/prompts: Project Lead.
- Backend session DTOs, mapping and gates; legacy/demo consistency: Friend 3 (Backend + Sandbox Lead), with Friend 2 for demo/product behavior.
- Dart domain, practice consumer, review/readiness gates and coach UI: Friend 1 (Flutter Desktop Lead) + Friend 2 (UI/Product Developer).
- Guardian/provider-context redaction: unchanged; P01 remains a prerequisite for live requests.

RISKS:
- New backend + old Dart remains compatible: old parser ignores the extra field and receives a safer passed boolean.
- New Dart + old backend uses an explicitly legacy fallback; old backend safety is not repaired by that fallback. Deploy backend and desktop updates together for the verified three-way guarantee.
- Stricter validation rejects malformed provider outputs instead of silently accepting coercions; failures must clear stale patch approval and show actionable generic failure feedback.
- Revoking previous approval on re-evaluation is an intentional behavior tightening: the developer must receive a fresh passing result before patching.
- No provider-quality improvement is established by deterministic regression fixtures. Live model classifications may be nondeterministic.

Verification after approval:
- Deterministic provider-output fixtures over the production JSON serialization/parsing path: each classification at scores below/at/above threshold; adversarial partial/incorrect score 0.95 with passed=true; correct score 0.95 with passed=false (server derives true); correct below threshold; invalid enum, missing fields, nonnumeric/boolean/nonfinite/out-of-range scores, blank feedback and malformed JSON.
- Connected HTTP journeys: explanation before investigation rejected; patch before accepted explanation rejected; partial/incorrect produce no Patch request and patch application 409; correct/high-enough result produces validated patch and review; rejected or malformed re-evaluation after success revokes old approval. Original harmless fixture hashes unchanged and no dummy secrets in intercepted provider payloads.
- Dart parsing and widget regressions for three labels, score/feedback, review gates and legacy missing-field fallback; Flutter analyze/test. Run security-critical backend/workspace/AI tests; use real Docker separately when relevant. Record transport mocks explicitly.
- Live safe-fixture evaluation only after P01 verified and private provider/model configuration exists. Check presence without revealing values. Current process OPENROUTER_API_KEY absent, CODEPROOF_MODEL absent, trusted worktree .env absent: live evaluation currently NOT TESTABLE. No live request attempted.

RECOMMENDATION:
Approve the additive classification field, server-owned CORRECT + existing threshold gate, stale-approval revocation, typed Dart/UI propagation, and consistent simulated/legacy gating. Do not redesign endpoints or accept provider-supplied passed as authority.

TASK: Investigate F06 and propose contract before implementation.
IMPLEMENTED: Read-only boundary/consumer investigation and this proposal.
FILES CREATED/CHANGED: setup-evidence/F06-CONTRACT-PROPOSAL.md only.
ARCHITECTURE IMPACT: Proposed cross-component evaluation propagation; not implemented.
API IMPACT: Proposed additive SessionView.evaluation.classification; not implemented.
DATA MODEL IMPACT: Proposed typed backend/Dart classification; not implemented.
SECURITY IMPACT: Identified score-only and stale-approval gating weaknesses; fix pending approval.
TESTS: Source mapping and credential-presence checks only; no new regression PASS claims.
KNOWN ISSUES: Findings above remain unfixed; live prerequisites absent.
NEXT DEPENDENCY: Human approval of the shared contract/gate proposal before source changes.
