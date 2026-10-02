import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:codeproof_desktop/app/app.dart';

void main() {
  testWidgets(
    'Main startup has no sample action and requires a project folder',
    (tester) async {
      tester.view.physicalSize = const Size(1440, 960);
      tester.view.devicePixelRatio = 1;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);
      await tester.pumpWidget(const CodeProofApp());
      await tester.pumpAndSettle();
      expect(find.text('Open sample project'), findsNothing);
      expect(find.text('Student Event Management'), findsNothing);
      expect(find.text('Connect your project'), findsOneWidget);
      await tester.tap(find.text('Connect your project'));
      await tester.pumpAndSettle();
      expect(find.textContaining('Leave empty'), findsNothing);
      await tester.tap(find.text('Open project'));
      await tester.pumpAndSettle();
      expect(
        find.text('Select a project folder before connecting.'),
        findsOneWidget,
      );
      expect(find.byType(AlertDialog), findsOneWidget);
      expect(tester.takeException(), isNull);
    },
  );
}
