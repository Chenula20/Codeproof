import 'package:flutter/material.dart';

import 'theme.dart';

import 'package:codeproof_desktop/features/startup/startup_screen.dart';

class CodeProofApp extends StatelessWidget {
  const CodeProofApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CodeProof',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      home: const StartupScreen(),
    );
  }
}
