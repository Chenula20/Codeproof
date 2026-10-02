import 'package:flutter_test/flutter_test.dart' hide Evaluation;
import 'package:flutter/material.dart';
import 'package:codeproof_desktop/domain/workspace_controller.dart';

import 'support/practice_fixture.dart';

import 'package:codeproof_desktop/features/workspace/coach.dart';
import 'package:codeproof_desktop/domain/workspace.dart';
import 'package:codeproof_desktop/ui/glass.dart';

void main() {
  for (final (wire, label) in [
    ('CORRECT', 'Correct'),
    ('PARTIALLY_CORRECT', 'Partially correct'),
    ('INCORRECT', 'Incorrect'),
  ]) {
    testWidgets('$wire coach shows classification, score and feedback', (
      tester,
    ) async {
      final controller = WorkspaceController(PracticeWorkspaceService());
      await controller.open();
      final editor = TextEditingController();
      controller.data!.phase = 'investigating';
      controller.data!.evaluation = Evaluation.fromJson({
        'classification': wire,
        'score': .95,
        'feedback': 'Typed provider fixture feedback',
        'passed': wire == 'CORRECT',
      });
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: GlassSettings(
              reducedTransparency: true,
              reducedMotion: true,
              child: CoachPanel(controller: controller, explanation: editor),
            ),
          ),
        ),
      );
      expect(find.text('$label · 95%'), findsOneWidget);
      expect(find.text('Typed provider fixture feedback'), findsOneWidget);
      await tester.pumpWidget(const SizedBox());
      editor.dispose();
      controller.dispose();
    });
    test('$wire retains score and feedback and controls review', () {
      final e = Evaluation.fromJson({
        'classification': wire,
        'score': .95,
        'feedback': 'Fixture feedback',
        'passed': true,
      });
      expect(e.label, label);
      expect(e.score, .95);
      expect(e.feedback, 'Fixture feedback');
      expect(e.permitsPatch, wire == 'CORRECT');
    });
  }
  test('correct below threshold stays locked', () {
    expect(
      const Evaluation(
        true,
        'feedback',
        .69,
        classification: ExplanationClassification.correct,
      ).permitsPatch,
      false,
    );
  });
  test('missing classification uses honest legacy label', () {
    final e = Evaluation.fromJson({
      'score': .95,
      'feedback': 'legacy',
      'passed': true,
    });
    expect(e.classification, isNull);
    expect(e.label, 'Root cause identified');
    expect(e.permitsPatch, true);
  });
  test('malformed evaluation is rejected', () {
    for (final changes in [
      {'classification': 'MAYBE'},
      {'classification': null},
      {'score': double.nan},
      {'score': double.infinity},
      {'score': 1.1},
      {'score': -.1},
      {'feedback': ' '},
    ]) {
      expect(
        () => Evaluation.fromJson({
          'classification': 'CORRECT',
          'score': .95,
          'feedback': 'fixture',
          'passed': true,
          ...changes,
        }),
        throwsFormatException,
      );
    }
  });
}
