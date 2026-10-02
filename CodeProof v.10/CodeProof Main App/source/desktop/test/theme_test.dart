import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:codeproof_desktop/app/theme.dart';

import 'widget_test.dart' as preview;

void main() {
  setUpAll(preview.loadPreviewFonts);
  test('Both palettes meet normal text contrast on panels', () {
    for (final p in [Palette.light, Palette.dark]) {
      for (final color in [
        p.text,
        p.muted,
        p.cyan,
        p.mint,
        p.violet,
        p.amber,
        p.red,
      ]) {
        final a = color.computeLuminance();
        final b = p.panel.computeLuminance();
        final ratio = (a > b ? (a + .05) / (b + .05) : (b + .05) / (a + .05));
        expect(ratio, greaterThanOrEqualTo(4.5));
      }
    }
  });
  testWidgets('Session-only theme and opt-in remembering use native options', (
    tester,
  ) async {
    final calls = <MethodCall>[];
    tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
      const MethodChannel('codeproof/native'),
      (call) async {
        calls.add(call);
        return null;
      },
    );
    addTearDown(
      () => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
        const MethodChannel('codeproof/native'),
        null,
      ),
    );
    await preview.boot(tester, const Size(1440, 960), fixture: false);
    expect(
      tester.widget<MaterialApp>(find.byType(MaterialApp)).themeMode,
      ThemeMode.dark,
    );
    await tester.tap(find.byTooltip('Appearance & shortcuts'));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('light-theme-switch')));
    await tester.pumpAndSettle();
    expect(
      tester.widget<MaterialApp>(find.byType(MaterialApp)).themeMode,
      ThemeMode.light,
    );
    expect((calls.last.arguments as Map)['remember'], false);
    await tester.tap(find.byKey(const Key('remember-theme-switch')));
    await tester.pumpAndSettle();
    expect((calls.last.arguments as Map)['remember'], true);
    await tester.tap(find.byKey(const Key('remember-theme-switch')));
    await tester.pumpAndSettle();
    expect((calls.last.arguments as Map)['clear_preference'], true);
    await tester.tap(find.text('Done'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Connect your project'));
    await tester.pumpAndSettle();
    expect(find.text('Local pairing token'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
  for (final light in [false, true]) {
    testWidgets(
      'Theme ${light ? 'light' : 'dark'} renders full simulated journey',
      (tester) async {
        tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
          const MethodChannel('codeproof/native'),
          (call) async => call.method == 'load_theme' ? light : null,
        );
        addTearDown(
          () => tester.binding.defaultBinaryMessenger.setMockMethodCallHandler(
            const MethodChannel('codeproof/native'),
            null,
          ),
        );
        await preview.boot(tester, const Size(1440, 960));
        await preview.capture(
          tester,
          'p12-${light ? 'light' : 'dark'}-welcome',
        );
        await tester.pumpAndSettle();
        await tester.tap(find.text('Break My App').first);
        await tester.pumpAndSettle();
        await preview.capture(
          tester,
          'p12-${light ? 'light' : 'dark'}-challenge',
        );
        await tester.tap(find.text('Start challenge'));
        await tester.pumpAndSettle();
        for (var i = 0; i < 4; i++) {
          await tester.ensureVisible(find.text('Get hint'));
          await tester.tap(find.text('Get hint'));
          await tester.pumpAndSettle();
        }
        await tester.ensureVisible(find.byKey(const Key('explanation-field')));
        await tester.enterText(
          find.byKey(const Key('explanation-field')),
          'email key is sent but username is expected',
        );
        await tester.ensureVisible(find.text('Evaluate explanation'));
        await tester.tap(find.text('Evaluate explanation'));
        await tester.pumpAndSettle();
        await preview.capture(tester, 'p12-${light ? 'light' : 'dark'}-review');
        await tester.ensureVisible(find.text('Apply to challenge copy'));
        await tester.tap(find.text('Apply to challenge copy'));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Tests').last);
        await tester.pumpAndSettle();
        await tester.ensureVisible(find.text('Run practice check'));
        await tester.tap(find.text('Run practice check'));
        await tester.pumpAndSettle();
        await preview.capture(
          tester,
          'p12-${light ? 'light' : 'dark'}-results',
        );
        expect(tester.takeException(), isNull);
        expect(find.textContaining('Simulated'), findsWidgets);
      },
    );
  }
}
