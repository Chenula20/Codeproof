import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../domain/workspace_controller.dart';
import '../features/startup/startup_screen.dart';
import '../features/workspace/workspace_shell.dart';
import '../services/workspace_service.dart';
import '../ui/glass.dart';
import 'theme.dart';

const _nativeChannel = MethodChannel('codeproof/native');

class CodeProofApp extends StatefulWidget {
  const CodeProofApp({super.key, this.controller});
  final WorkspaceController? controller;
  @override
  State<CodeProofApp> createState() => _CodeProofAppState();
}

class _CodeProofAppState extends State<CodeProofApp> {
  bool reducedTransparency = false;
  bool reducedMotion = false;
  ThemeMode themeMode = ThemeMode.dark;
  bool rememberTheme = false;
  String? appearanceError;

  @override
  void initState() {
    super.initState();
    _loadTheme();
  }

  Future<void> _loadTheme() async {
    try {
      final saved = await _nativeChannel.invokeMethod<bool>('load_theme');
      if (!mounted) return;
      if (saved != null) {
        setState(() {
          themeMode = saved ? ThemeMode.light : ThemeMode.dark;
          rememberTheme = true;
        });
      }
      await _nativeChannel.invokeMethod<void>('set_theme', {
        'light': themeMode == ThemeMode.light,
        'remember': false,
      });
    } on MissingPluginException {
      // Other platforms and widget tests keep the default/session-only choice.
    } on PlatformException {
      if (mounted) {
        setState(
          () => appearanceError = 'Saved appearance could not be loaded. Session-only themes are still available.',
        );
      }
    }
  }

  Future<void> _applyTheme({bool clearPreference = false}) async {
    try {
      await _nativeChannel.invokeMethod<void>('set_theme', {
        'light': themeMode == ThemeMode.light,
        'remember': rememberTheme,
        'clear_preference': clearPreference,
      });
      if (mounted && appearanceError != null) {
        setState(() => appearanceError = null);
      }
    } on MissingPluginException {
      if (mounted && rememberTheme) {
        setState(
          () => appearanceError =
              'Saving appearance is available in the Windows desktop build.',
        );
      }
    } on PlatformException {
      if (mounted) {
        setState(
          () => appearanceError = 'Appearance changed for this session; the saved preference could not be updated.',
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) => GlassSettings(
    reducedTransparency: reducedTransparency,
    reducedMotion: reducedMotion,
    child: MaterialApp(
      title: 'CodeProof Main App',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: themeMode,
      builder: (context, child) => MediaQuery(
        data: MediaQuery.of(context).copyWith(
          disableAnimations:
              reducedMotion || MediaQuery.disableAnimationsOf(context),
        ),
        child: child!,
      ),
      home: _Home(
        controller: widget.controller,
        onSettings: (context) => showDialog<void>(
          context: context,
          builder: (context) => StatefulBuilder(
            builder: (context, update) => AlertDialog(
              title: const Text('Make this space yours'),
              content: SizedBox(
                width: 430,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SwitchListTile(
                      key: const Key('light-theme-switch'),
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Light theme'),
                      subtitle: const Text('Use a bright, readable workspace'),
                      value: themeMode == ThemeMode.light,
                      onChanged: (value) {
                        setState(
                          () => themeMode = value
                              ? ThemeMode.light
                              : ThemeMode.dark,
                        );
                        update(() {});
                        _applyTheme();
                      },
                    ),
                    SwitchListTile(
                      key: const Key('remember-theme-switch'),
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Remember theme'),
                      subtitle: const Text(
                        'Off keeps this choice for this session only',
                      ),
                      value: rememberTheme,
                      onChanged: (value) {
                        setState(() => rememberTheme = value);
                        update(() {});
                        _applyTheme(clearPreference: !value);
                      },
                    ),
                    if (appearanceError != null) Text(appearanceError!),
                    SwitchListTile(
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Reduce transparency'),
                      subtitle: const Text(
                        'Solid surfaces for clarity and performance',
                      ),
                      value: reducedTransparency,
                      onChanged: (value) {
                        setState(() => reducedTransparency = value);
                        update(() {});
                      },
                    ),
                    SwitchListTile(
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Reduce motion'),
                      subtitle: const Text(
                        'Keep navigation still and predictable',
                      ),
                      value: reducedMotion,
                      onChanged: (value) {
                        setState(() => reducedMotion = value);
                        update(() {});
                      },
                    ),
                    const Divider(),
                    const SizedBox(height: 12),
                    Text(
                      'Keyboard shortcuts\nCtrl+1–5   Workspace sections\nCtrl+K      Find a file\nF1             Open engineering coach',
                      style: TextStyle(
                        color: Palette.of(context).muted,
                        height: 2,
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Done'),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}

class _Home extends StatefulWidget {
  const _Home({required this.onSettings, this.controller});
  final WorkspaceController? controller;
  final void Function(BuildContext) onSettings;
  @override
  State<_Home> createState() => _HomeState();
}

class _HomeState extends State<_Home> {
  late final controller =
      widget.controller ??
      WorkspaceController(LocalWorkspaceService(token: ''));
  final shellKey = GlobalKey<WorkspaceShellState>();
  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  Future<void> connect() async {
    final result = await showDialog<_Connection>(
      context: context,
      builder: (context) => const _ConnectDialog(),
    );
    if (result != null && mounted) {
      await controller.open(
        path: result.path,
        using: LocalWorkspaceService(token: result.token, port: result.port),
      );
    }
  }

  Future<void> analyze() async {
    final approved = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Analyze with your AI provider?'),
        content: SizedBox(
          width: 450,
          child: Text(
            'The backend will send selected, redacted project contents to your configured OpenRouter model for analysis and coaching. Review your project for sensitive material before continuing.\n\nYour API key stays in the backend environment.',
            style: TextStyle(color: Palette.of(context).muted),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          PrimaryButton(
            'Enable AI analysis',
            onPressed: () => Navigator.pop(context, true),
          ),
        ],
      ),
    );
    if (approved == true && mounted) {
      await controller.act('analysis', {'use_ai': true});
    }
  }

  Future<void> closeProject() async {
    final accepted = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Close this workspace?'),
        content: const Text(
          'The temporary copy and session progress will be discarded. Copy any diff or evidence you want to keep. Your original project is unchanged.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Keep working'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Close workspace'),
          ),
        ],
      ),
    );
    if (accepted == true && mounted) await controller.close();
  }

  @override
  Widget build(BuildContext context) => ListenableBuilder(
    listenable: controller,
    builder: (context, _) {
      final data = controller.data;
      return CallbackShortcuts(
        bindings: {
          for (final (key, tab) in [
            (LogicalKeyboardKey.digit1, WorkspaceTab.analysis),
            (LogicalKeyboardKey.digit2, WorkspaceTab.skills),
            (LogicalKeyboardKey.digit3, WorkspaceTab.code),
            (LogicalKeyboardKey.digit4, WorkspaceTab.investigation),
            (LogicalKeyboardKey.digit5, WorkspaceTab.patch),
          ])
            SingleActivator(key, control: true): () {
              if (data != null) controller.selectTab(tab);
            },
          const SingleActivator(LogicalKeyboardKey.keyK, control: true): () =>
              shellKey.currentState?.showFiles(),
          const SingleActivator(LogicalKeyboardKey.f1): () =>
              shellKey.currentState?.showCoach(),
        },
        child: Focus(
          autofocus: true,
          child: Scaffold(
            body: AmbientBackground(
              child: SafeArea(
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(20, 12, 16, 5),
                      child: LayoutBuilder(
                        builder: (context, size) => Row(
                          children: [
                            Brand(compact: size.maxWidth < 430),
                            const SizedBox(width: 22),
                            if (data != null && size.maxWidth > 700) ...[
                              Container(
                                width: 1,
                                height: 24,
                                color: Palette.of(context).line,
                              ),
                              const SizedBox(width: 20),
                              Expanded(
                                child: Text(
                                  data.name,
                                  overflow: TextOverflow.ellipsis,
                                  style: TextStyle(
                                    color: Palette.of(context).muted,
                                    fontSize: 12,
                                  ),
                                ),
                              ),
                              StatusBadge(
                                data.mode,
                                color: Palette.of(context).violet,
                              ),
                            ] else
                              const Spacer(),
                            if (size.maxWidth > 1000) ...[
                              const SizedBox(width: 10),
                              StatusBadge(
                                'Original protected',
                                icon: Icons.shield_outlined,
                                color: Palette.of(context).mint,
                              ),
                            ],
                            if (data != null)
                              IconButton(
                                tooltip: 'Close workspace',
                                onPressed: controller.busy
                                    ? null
                                    : closeProject,
                                icon: Icon(
                                  Icons.logout_rounded,
                                  size: 18,
                                  color: Palette.of(context).muted,
                                ),
                              ),
                            IconButton(
                              tooltip: 'Appearance & shortcuts',
                              onPressed: () => widget.onSettings(context),
                              icon: Icon(
                                Icons.tune_rounded,
                                size: 20,
                                color: Palette.of(context).muted,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    if (controller.busy)
                      LinearProgressIndicator(
                        minHeight: 2,
                        color: Palette.of(context).cyan,
                        semanticsLabel: controller.operation,
                      )
                    else
                      const SizedBox(height: 2),
                    if (controller.error != null)
                      Container(
                        margin: const EdgeInsets.symmetric(
                          horizontal: 14,
                          vertical: 8,
                        ),
                        padding: const EdgeInsets.fromLTRB(16, 6, 5, 6),
                        decoration: BoxDecoration(
                          color: Palette.of(context).red.withValues(alpha: .12),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              Icons.error_outline,
                              size: 18,
                              color: Palette.of(context).red,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                controller.error!,
                                style: const TextStyle(fontSize: 12),
                              ),
                            ),
                            IconButton(
                              tooltip: 'Dismiss error',
                              onPressed: controller.clearError,
                              icon: const Icon(Icons.close, size: 17),
                            ),
                          ],
                        ),
                      ),
                    Expanded(
                      child: data == null
                          ? StartupScreen(
                              busy: controller.busy,
                              onConnect: connect,
                            )
                          : WorkspaceShell(
                              key: shellKey,
                              controller: controller,
                              onAnalyze: analyze,
                            ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 20,
                        vertical: 7,
                      ),
                      decoration: BoxDecoration(
                        color: Palette.of(context).panel.withValues(alpha: .65),
                        border: Border(
                          top: BorderSide(color: Palette.of(context).line),
                        ),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            Icons.circle,
                            color: Palette.of(context).mint,
                            size: 6,
                          ),
                          const SizedBox(width: 7),
                          Expanded(
                            child: Text(
                              controller.busy
                                  ? controller.operation
                                  : data == null
                                  ? 'A safe space to understand your software'
                                  : data.practice
                                  ? 'Practice mode · in-memory workspace'
                                  : 'Guardian · read-only project access',
                              style: TextStyle(
                                color: Palette.of(context).muted,
                                fontSize: 10,
                              ),
                            ),
                          ),
                          if (MediaQuery.sizeOf(context).width > 650)
                            Text(
                              data?.hasChallenge == true
                                  ? 'Challenge copy   •   UTF-8'
                                  : 'CodeProof   /   Engineering workspace',
                              style: TextStyle(
                                color: Palette.of(context).muted,
                                fontSize: 10,
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
    },
  );
}

class _Connection {
  const _Connection(this.path, this.token, this.port);
  final String path;
  final String token;
  final int port;
}

class _ConnectDialog extends StatefulWidget {
  const _ConnectDialog();
  @override
  State<_ConnectDialog> createState() => _ConnectDialogState();
}

class _ConnectDialogState extends State<_ConnectDialog> {
  final path = TextEditingController();
  final token = TextEditingController();
  final port = TextEditingController(text: '8000');
  String? error;
  @override
  void dispose() {
    path.dispose();
    token.dispose();
    port.dispose();
    super.dispose();
  }

  Future<void> browseForProject() async {
    try {
      final selected = await _nativeChannel.invokeMethod<String>(
        'pick_directory',
      );
      if (selected != null && selected.isNotEmpty && mounted) {
        setState(() {
          path.text = selected;
          error = null;
        });
      }
    } on MissingPluginException {
      if (mounted) {
        setState(
          () => error =
              'Folder browsing is available in the Windows desktop build.',
        );
      }
    } on PlatformException catch (exception) {
      if (mounted) {
        setState(
          () =>
              error = exception.message ?? 'Could not open the folder picker.',
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) => AlertDialog(
    title: const Text('Connect your project'),
    content: SizedBox(
      width: 490,
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Start the local service with python -m backend, then paste its pairing token. Project files stay on this computer unless you explicitly enable AI analysis.',
              style: TextStyle(color: Palette.of(context).muted),
            ),
            const SizedBox(height: 22),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: TextField(
                    controller: path,
                    decoration: const InputDecoration(
                      labelText: 'Project folder',
                      hintText: r'C:\Projects\my-app',
                      helperText: 'Select your project folder. Demo projects are packaged separately.',
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: OutlinedButton.icon(
                    onPressed: browseForProject,
                    icon: const Icon(Icons.folder_open_outlined, size: 17),
                    label: const Text('Browse'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 13,
                        vertical: 15,
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              controller: token,
              obscureText: true,
              enableSuggestions: false,
              autocorrect: false,
              decoration: const InputDecoration(
                labelText: 'Local pairing token',
                prefixIcon: Icon(Icons.key_outlined, size: 18),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: port,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Port on 127.0.0.1'),
            ),
            if (error != null)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(
                  error!,
                  style: TextStyle(color: Palette.of(context).red),
                ),
              ),
            const SizedBox(height: 20),
            StatusBadge(
              'Loopback connection only',
              color: Palette.of(context).mint,
              icon: Icons.lock_outline,
            ),
          ],
        ),
      ),
    ),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(context),
        child: const Text('Cancel'),
      ),
      PrimaryButton(
        'Open project',
        icon: Icons.folder_open_outlined,
        onPressed: () {
          if (path.text.trim().isEmpty) {
            setState(
              () => error = 'Select a project folder before connecting.',
            );
            return;
          }
          final number = int.tryParse(port.text);
          if (token.text.trim().length < 32) {
            setState(
              () => error = 'Paste the pairing token from the successfully running CodeProof service (at least 32 characters).',
            );
            return;
          }
          if (number == null || number < 1 || number > 65535) {
            setState(
              () => error = 'Enter the CodeProof service port from 1 to 65535; this is the CodeProof service port.',
            );
            return;
          }
          Navigator.pop(
            context,
            _Connection(path.text.trim(), token.text.trim(), number),
          );
        },
      ),
    ],
  );
}
