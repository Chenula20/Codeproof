import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:codeproof_desktop/app/theme.dart';
import 'package:codeproof_desktop/domain/workspace.dart';
import 'package:codeproof_desktop/domain/workspace_controller.dart';
import 'package:codeproof_desktop/features/workspace/workspace_shell.dart';
import 'package:codeproof_desktop/services/workspace_service.dart';
import 'package:codeproof_desktop/ui/glass.dart';

class LocalFaultService extends WorkspaceService {
  final List<String> actions = [];
  late WorkspaceData data;
  @override
  Future<WorkspaceData> open(String path) async => data = WorkspaceData(
    id: 'local-fault',
    name: 'Selected project',
    sample: false,
    files: {'main.py': 'value = 1\n'},
    summary: 'Local snapshot',
    technologies: [],
    issues: [],
    skills: [],
    supportedIncidents: [
      const Incident(
        id: 'syntax-safe',
        title: 'Python syntax failure',
        goal: 'Trace module loading.',
        targetFile: 'main.py',
      ),
    ],
  );
  @override
  Future<WorkspaceData> action(
    String id,
    String action, [
    Map<String, dynamic> body = const {},
  ]) async {
    actions.add(action);
    if (action == 'challenge') {
      expect(body, {'incident_id': 'syntax-safe'});
      data.phase = 'investigating';
      data.challengeTitle = 'Break My App: syntax failure';
      data.activeIncident = data.supportedIncidents.first;
      data.relevantFiles = ['main.py'];
    } else if (action == 'hint') {
      data.hints = [...data.hints, 'Local hint ${data.hints.length + 1}'];
    }
    return data;
  }

  @override
  Future<void> close(String id) async {}
}

void main() {
  for (final size in [const Size(400, 800), const Size(1440, 1000)]) {
    testWidgets('Main controls and four local hints at $size', (tester) async {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      final service = LocalFaultService();
      final controller = WorkspaceController(service);
      await controller.open(path: 'explicit-project');
      var consentOpened = false;
      await tester.pumpWidget(
        GlassSettings(
          reducedTransparency: true,
          reducedMotion: true,
          child: MaterialApp(
            theme: AppTheme.darkTheme,
            home: Scaffold(
              body: ListenableBuilder(
                listenable: controller,
                builder: (_, _) => WorkspaceShell(
                  controller: controller,
                  onAnalyze: () => consentOpened = true,
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('Investigate'), findsWidgets);
      await tester.tap(find.byKey(const Key('break-my-app-button')));
      await tester.pumpAndSettle();
      expect(find.byKey(const Key('incident-selector')), findsOneWidget);
      await tester.tap(find.text('Start challenge'));
      await tester.pumpAndSettle();
      await tester.tap(find.byKey(const Key('hints-button')));
      await tester.pumpAndSettle();
      for (var level = 1; level <= 4; level++) {
        await tester.ensureVisible(find.text('Get hint').last);
        await tester.tap(find.text('Get hint').last);
        await tester.pumpAndSettle();
        expect(controller.data!.hints.length, level);
      }
      expect(find.text('All hints revealed'), findsWidgets);
      final evaluation = tester.widgetList<PrimaryButton>(
        find.byWidgetPredicate(
          (widget) =>
              widget is PrimaryButton && widget.label == 'Evaluate explanation',
        ),
      );
      expect(evaluation.every((button) => button.onPressed == null), isTrue);
      expect(service.actions, ['challenge', 'hint', 'hint', 'hint', 'hint']);
      await tester.ensureVisible(find.text('Enable AI review').last);
      await tester.tap(find.text('Enable AI review').last);
      await tester.pumpAndSettle();
      expect(consentOpened, isTrue);

      await tester.pumpWidget(const SizedBox());
      controller.dispose();
    });
  }
  testWidgets('Unsupported project cannot submit an empty break request', (
    tester,
  ) async {
    tester.view.physicalSize = const Size(1000, 800);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    final service = LocalFaultService();
    final controller = WorkspaceController(service);
    await controller.open(path: 'explicit-project');
    controller.data!.supportedIncidents = [];
    await tester.pumpWidget(
      GlassSettings(
        reducedTransparency: true,
        reducedMotion: true,
        child: MaterialApp(
          theme: AppTheme.darkTheme,
          home: Scaffold(
            body: WorkspaceShell(controller: controller, onAnalyze: () {}),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('break-my-app-button')));
    await tester.pumpAndSettle();
    expect(find.textContaining('No compatible modules found.'), findsOneWidget);
    expect(
      tester
          .widget<PrimaryButton>(
            find.byWidgetPredicate(
              (widget) =>
                  widget is PrimaryButton && widget.label == 'Start challenge',
            ),
          )
          .onPressed,
      isNull,
    );
    expect(service.actions, isEmpty);
    await tester.pumpWidget(const SizedBox());
    controller.dispose();
  });
}
