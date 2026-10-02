import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:codeproof_desktop/app/theme.dart';
import 'package:codeproof_desktop/domain/workspace.dart';
import 'package:codeproof_desktop/domain/workspace_controller.dart';
import 'package:codeproof_desktop/features/workspace/workspace_shell.dart';

import 'support/practice_fixture.dart';

import 'package:codeproof_desktop/ui/glass.dart';

class IncidentService extends PracticeWorkspaceService {
  Map<String, dynamic>? sent;
  @override
  Future<WorkspaceData> action(
    String id,
    String action, [
    Map<String, dynamic> body = const {},
  ]) async {
    sent = body;
    final data = await open('');
    data.mode = 'Local backend';
    data.phase = 'investigating';
    data.activeIncident = const Incident(
      id: 'request-field',
      title: 'Request field mismatch',
      goal: 'Trace fields',
      targetFile: 'app.py',
    );
    return data;
  }
}

void main() {
  test('Incident metadata rejects empty content', () {
    expect(
      () => Incident.fromJson({
        'id': '',
        'title': 'Training',
        'goal': 'Trace',
        'target_file': 'app.py',
      }),
      throwsFormatException,
    );
  });
  testWidgets('Approved incident sends only its id', (tester) async {
    tester.view.physicalSize = const Size(1440, 960);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final service = IncidentService();
    final controller = WorkspaceController(service);
    await controller.open();
    controller.data!.mode = 'Local backend';
    controller.data!.provider = 'AI provider';
    controller.data!.supportedIncidents = [
      const Incident(
        id: 'request-field',
        title: 'Request field mismatch',
        goal: 'Trace fields',
        targetFile: 'app.py',
      ),
    ];
    await tester.pumpWidget(
      GlassSettings(
        reducedTransparency: true,
        reducedMotion: true,
        child: MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: ListenableBuilder(
              listenable: controller,
              builder: (context, _) => WorkspaceShell(
                controller: controller,
                onAnalyze: () async {},
              ),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Choose challenge'));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('incident-selector')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Request field mismatch').last);
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('incident-goal')), findsOneWidget);
    expect(find.byKey(const Key('observed-issue-field')), findsNothing);
    await tester.tap(find.text('Start challenge'));
    await tester.pumpAndSettle();
    expect(service.sent, {'incident_id': 'request-field'});
    expect(find.byKey(const Key('active-incident-title')), findsOneWidget);
    await tester.pumpWidget(const SizedBox());
    controller.dispose();
  });
}
