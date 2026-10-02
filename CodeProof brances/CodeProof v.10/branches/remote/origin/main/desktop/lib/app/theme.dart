import 'package:flutter/material.dart';

class Palette {
  const Palette({
    required this.background,
    required this.panel,
    required this.text,
    required this.muted,
    required this.cyan,
    required this.mint,
    required this.violet,
    required this.amber,
    required this.red,
    required this.line,
  });
  final Color background,
      panel,
      text,
      muted,
      cyan,
      mint,
      violet,
      amber,
      red,
      line;
  static const dark = Palette(
    background: Color(0xFF080E1A),
    panel: Color(0xFF121D30),
    text: Color(0xFFF1F5FC),
    muted: Color(0xFFA0B0C8),
    cyan: Color(0xFF58E6ED),
    mint: Color(0xFF78EBC4),
    violet: Color(0xFFB59BFF),
    amber: Color(0xFFFFCA81),
    red: Color(0xFFFF8F9C),
    line: Color(0xFF2C3A50),
  );
  static const light = Palette(
    background: Color(0xFFF5F8FC),
    panel: Color(0xFFFFFFFF),
    text: Color(0xFF16233B),
    muted: Color(0xFF52627A),
    cyan: Color(0xFF006770),
    mint: Color(0xFF146C50),
    violet: Color(0xFF6744A4),
    amber: Color(0xFF865100),
    red: Color(0xFFAA253D),
    line: Color(0xFFCED7E4),
  );
  static Palette of(BuildContext context) =>
      Theme.of(context).brightness == Brightness.light ? light : dark;
}

class AppTheme {
  static ThemeData get darkTheme => _build(Palette.dark, Brightness.dark);
  static ThemeData get lightTheme => _build(Palette.light, Brightness.light);
  static ThemeData _build(Palette p, Brightness brightness) => ThemeData(
    useMaterial3: true,
    brightness: brightness,
    fontFamily: 'Segoe UI',
    scaffoldBackgroundColor: p.background,
    colorScheme: ColorScheme.fromSeed(seedColor: p.cyan, brightness: brightness)
        .copyWith(
          primary: p.cyan,
          secondary: p.violet,
          surface: p.panel,
          onSurface: p.text,
          error: p.red,
        ),
    textTheme: TextTheme(
      bodyMedium: TextStyle(fontSize: 13, height: 1.55, color: p.text),
      bodySmall: TextStyle(fontSize: 11, height: 1.5, color: p.muted),
      bodyLarge: TextStyle(fontSize: 15, height: 1.6, color: p.muted),
      titleLarge: const TextStyle(
        fontSize: 21,
        fontWeight: FontWeight.w600,
        letterSpacing: -.4,
      ),
      titleMedium: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
      headlineMedium: const TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.w600,
        letterSpacing: -.8,
      ),
    ),
    dividerColor: p.line,
    tooltipTheme: const TooltipThemeData(
      waitDuration: Duration(milliseconds: 500),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: p.background,
      contentPadding: const EdgeInsets.all(15),
      hintStyle: TextStyle(color: p.muted, fontSize: 13),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: p.line),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: p.line),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(14),
        borderSide: BorderSide(color: p.cyan),
      ),
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(foregroundColor: p.muted),
    ),
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: p.text,
        side: BorderSide(color: p.line),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(13)),
      ),
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: p.panel,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(26),
        side: BorderSide(color: p.line),
      ),
    ),
  );
}
