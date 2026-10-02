// This is a basic Flutter widget test for the CodeProof startup screen.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:codeproof_desktop/app/app.dart';

void main() {
  testWidgets('CodeProof startup screen displays correctly', (
    WidgetTester tester,
  ) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const CodeProofApp());

    // Verify the title is displayed
    expect(find.text('CodeProof'), findsOneWidget);

    // Verify the description is displayed
    expect(
      find.textContaining('developer engineering environment'),
      findsOneWidget,
    );

    // Verify the empty state is displayed
    expect(find.text('No Project Selected'), findsOneWidget);
    expect(
      find.textContaining('Select a project to begin analysis'),
      findsOneWidget,
    );

    // Verify the core principle footer is displayed
    expect(
      find.textContaining('original user project is never directly modified'),
      findsOneWidget,
    );

    // Verify the disabled action button is present
    expect(find.byType(OutlinedButton), findsOneWidget);
  });

  testWidgets('Startup screen handles resizing without overflow', (
    WidgetTester tester,
  ) async {
    // Test at a narrow width
    await tester.pumpWidget(
      const SizedBox(width: 400, height: 800, child: CodeProofApp()),
    );

    // Verify no overflow errors
    expect(find.text('CodeProof'), findsOneWidget);

    // Test at a wide width
    await tester.pumpWidget(
      const SizedBox(width: 1200, height: 800, child: CodeProofApp()),
    );

    // Verify no overflow errors
    expect(find.text('CodeProof'), findsOneWidget);
  });
}
