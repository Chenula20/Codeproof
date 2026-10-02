import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart' hide Evaluation;
import 'package:codeproof_desktop/domain/workspace.dart';
import 'package:codeproof_desktop/domain/workspace_controller.dart';

import 'support/practice_fixture.dart';

import 'package:codeproof_desktop/features/workspace/evidence.dart';
import 'package:codeproof_desktop/ui/glass.dart';

void main() {
  test('count parser rejects inconsistent and invalid counters', () {
    for (final changes in [
      {'total': 2},
      {'passed': -1},
      {'failed': 1.2},
      {'skipped': true},
      {'total': '1'},
    ]) {
      expect(
        () => TestCounts.fromJson({
          'total': 1,
          'passed': 1,
          'failed': 0,
          'skipped': 0,
          ...changes,
        }),
        throwsA(anything),
      );
    }
  });
  test('unknown counts do not certify a status-only pass', () {
    final legacy = ValidationResult.fromJson({
      'status': 'passed',
      'output': 'old',
      'duration_ms': 0,
      'original_unchanged': true,
      'checks': <String>[],
    });
    expect(legacy.testCounts, isNull);
    expect(legacy.hasPassingEvidence, false);
    expect(legacy.countSummary, 'Test counts unavailable');
  });
  test('simulated check has no real passing evidence or invented counts', () {
    const result = ValidationResult(status: 'passed', simulated: true);
    expect(result.hasPassingEvidence, false);
    expect(result.countSummary, 'Simulated practice — no tests executed');
  });
  test('known counts render exactly and skipped tests are not all-pass', () {
    const result = ValidationResult(
      status: 'passed',
      testCounts: TestCounts(total: 3, passed: 2, failed: 0, skipped: 1),
    );
    expect(result.hasPassingEvidence, false);
    expect(
      result.countSummary,
      'Total: 3 · Passed: 2 · Failed/errors: 0 · Skipped: 1',
    );
    expect(
      const ValidationResult(
        status: 'failed',
        testCounts: TestCounts(total: 0, passed: 0, failed: 0, skipped: 0),
      ).countSummary,
      'No tests collected',
    );
  });
  for (final result in [
    const ValidationResult(status: 'passed'),
    const ValidationResult(status: 'unavailable'),
    const ValidationResult(status: 'timeout'),
    const ValidationResult(status: 'error'),
    const ValidationResult(
      status: 'passed',
      testCounts: TestCounts(total: 1, passed: 0, failed: 0, skipped: 1),
    ),
  ]) {
    test(
      'stale validated phase blocked for ${result.status}/${result.testCounts?.skipped}',
      () async {
        final service = PracticeWorkspaceService();
        final data = await service.open('');
        data.mode = 'Local backend';
        data.phase = 'validated';
        data.evaluation = const Evaluation(
          true,
          'fixture',
          .95,
          classification: ExplanationClassification.correct,
        );
        data.validation = result;
        expect(data.ready, false);
      },
    );
  }
  testWidgets('results UI shows counters and blocks unknown readiness', (
    tester,
  ) async {
    final controller = WorkspaceController(PracticeWorkspaceService());
    await controller.open();
    controller.data!.mode = 'Local backend';
    controller.data!.phase = 'validated';
    controller.data!.validation = const ValidationResult(
      status: 'passed',
      originalUnchanged: true,
      testCounts: TestCounts(total: 3, passed: 2, failed: 1, skipped: 0),
    );
    controller.evidence = EvidenceTab.tests;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: GlassSettings(
            reducedTransparency: true,
            reducedMotion: true,
            child: EvidencePanel(
              controller: controller,
              expanded: true,
              onToggle: () {},
              onValidate: () {},
            ),
          ),
        ),
      ),
    );
    expect(
      find.text('Total: 3 · Passed: 2 · Failed/errors: 1 · Skipped: 0'),
      findsOneWidget,
    );
    controller.data!.validation = const ValidationResult(status: 'unavailable');
    controller.evidence = EvidenceTab.readiness;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: GlassSettings(
            reducedTransparency: true,
            reducedMotion: true,
            child: EvidencePanel(
              controller: controller,
              expanded: true,
              onToggle: () {},
              onValidate: () {},
            ),
          ),
        ),
      ),
    );
    expect(find.text('MORE EVIDENCE NEEDED'), findsOneWidget);
    expect(find.text('READY FOR HUMAN REVIEW'), findsNothing);
    await tester.pumpWidget(const SizedBox());
    controller.dispose();
  });
}
