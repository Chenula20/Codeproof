class SkillEstimate {
  const SkillEstimate(
    this.category,
    this.relevance,
    this.confidence,
    this.evidence,
  );
  final String category;
  final double relevance;
  final double confidence;
  final List<String> evidence;
  factory SkillEstimate.fromJson(Map<String, dynamic> json) => SkillEstimate(
    json['category'] as String,
    (json['relevance'] as num).toDouble(),
    (json['confidence'] as num).toDouble(),
    List<String>.from(json['evidence'] as List),
  );
}

enum ExplanationClassification { correct, partiallyCorrect, incorrect }

class Evaluation {
  const Evaluation(
    this.passed,
    this.feedback,
    this.score, {
    this.classification,
  });
  final bool passed;
  final String feedback;
  final double score;
  final ExplanationClassification? classification;
  bool get permitsPatch =>
      passed &&
      score >= .7 &&
      (classification == null ||
          classification == ExplanationClassification.correct);
  String get label => switch (classification) {
    ExplanationClassification.correct => 'Correct',
    ExplanationClassification.partiallyCorrect => 'Partially correct',
    ExplanationClassification.incorrect => 'Incorrect',
    null => passed ? 'Root cause identified' : 'Keep investigating',
  };
  factory Evaluation.fromJson(Map<String, dynamic> json) {
    if (json.containsKey('classification') && json['classification'] == null) {
      throw const FormatException('Missing explanation classification value');
    }
    final classification = switch (json['classification']) {
      'CORRECT' => ExplanationClassification.correct,
      'PARTIALLY_CORRECT' => ExplanationClassification.partiallyCorrect,
      'INCORRECT' => ExplanationClassification.incorrect,
      null => null, // Compatibility with older backend payloads.
      _ => throw const FormatException('Unknown explanation classification'),
    };
    final score = (json['score'] as num).toDouble();
    final feedback = json['feedback'] as String;
    if (!score.isFinite || score < 0 || score > 1 || feedback.trim().isEmpty) {
      throw const FormatException('Invalid explanation evaluation');
    }
    return Evaluation(
      json['passed'] as bool,
      feedback,
      score,
      classification: classification,
    );
  }
}

class PatchProposal {
  const PatchProposal(
    this.description,
    this.diff,
    this.files,
    this.risk,
    this.warnings,
  );
  final String description;
  final String diff;
  final List<String> files;
  final String risk;
  final List<String> warnings;
  factory PatchProposal.fromJson(Map<String, dynamic> json) => PatchProposal(
    json['description'] as String,
    json['diff'] as String,
    List<String>.from(json['affected_files'] as List),
    json['risk_level'] as String,
    List<String>.from(json['validation_warnings'] as List),
  );
}

class TestCounts {
  const TestCounts({
    required this.total,
    required this.passed,
    required this.failed,
    required this.skipped,
  });
  final int total;
  final int passed;
  final int failed;
  final int skipped;
  bool get consistent =>
      total >= 0 &&
      passed >= 0 &&
      failed >= 0 &&
      skipped >= 0 &&
      total == passed + failed + skipped;
  bool get allPassed =>
      consistent && total > 0 && passed == total && failed == 0 && skipped == 0;
  factory TestCounts.fromJson(Map<String, dynamic> json) {
    final counts = TestCounts(
      total: json['total'] as int,
      passed: json['passed'] as int,
      failed: json['failed'] as int,
      skipped: json['skipped'] as int,
    );
    if (!counts.consistent) {
      throw const FormatException('Inconsistent test counts');
    }
    return counts;
  }
  Map<String, int> toJson() => {
    'total': total,
    'passed': passed,
    'failed': failed,
    'skipped': skipped,
  };
}

class ValidationResult {
  const ValidationResult({
    this.status = 'not_run',
    this.output = 'No validation has run yet.',
    this.testCounts,
    this.simulated = false,
    this.durationMs = 0,
    this.originalUnchanged,
    this.checks = const [],
  });
  final String status;
  final String output;
  final TestCounts? testCounts;
  final bool simulated;
  bool get hasPassingEvidence =>
      !simulated && status == 'passed' && testCounts?.allPassed == true;
  bool get successfulCheck =>
      simulated ? status == 'passed' : hasPassingEvidence;
  String get countSummary {
    if (simulated) return 'Simulated practice — no tests executed';
    if (testCounts == null) return 'Test counts unavailable';
    if (testCounts!.total == 0) return 'No tests collected';
    final c = testCounts!;
    return 'Total: ${c.total} · Passed: ${c.passed} · Failed/errors: ${c.failed} · Skipped: ${c.skipped}';
  }

  final int durationMs;
  final bool? originalUnchanged;
  final List<String> checks;
  factory ValidationResult.fromJson(Map<String, dynamic> json) =>
      ValidationResult(
        status: json['status'] as String,
        testCounts: json['test_counts'] == null
            ? null
            : TestCounts.fromJson(json['test_counts'] as Map<String, dynamic>),
        simulated: json['simulated'] as bool? ?? false,
        output: json['output'] as String,
        durationMs: json['duration_ms'] as int,
        originalUnchanged: json['original_unchanged'] as bool?,
        checks: List<String>.from(json['checks'] as List),
      );
}

class Incident {
  const Incident({
    required this.id,
    required this.title,
    required this.goal,
    required this.targetFile,
  });
  final String id;
  final String title;
  final String goal;
  final String targetFile;

  factory Incident.fromJson(Map<String, dynamic> json) {
    final incident = Incident(
      id: json['id'] as String,
      title: json['title'] as String,
      goal: json['goal'] as String,
      targetFile: json['target_file'] as String,
    );
    if ([
      incident.id,
      incident.title,
      incident.goal,
      incident.targetFile,
    ].any((value) => value.trim().isEmpty)) {
      throw const FormatException('Incomplete controlled incident');
    }
    return incident;
  }
}

class WorkspaceData {
  WorkspaceData({
    required this.id,
    required this.name,
    required this.sample,
    required this.files,
    required this.summary,
    required this.technologies,
    required this.issues,
    required this.skills,
    this.mode = 'Local backend',
    this.provider = 'Local inspection',
    this.phase = 'analyzed',
    this.challengeTitle = '',
    this.challengeDescription = '',
    this.relevantFiles = const [],
    this.supportedIncidents = const [],
    this.activeIncident,
    this.hints = const [],
    this.evaluation,
    this.patch,
    this.validation = const ValidationResult(),
    this.activity = const [],
  });
  final String id;
  final String name;
  final bool sample;
  Map<String, String> files;
  String summary;
  List<String> technologies;
  List<String> issues;
  List<SkillEstimate> skills;
  String mode;
  String provider;
  String phase;
  String challengeTitle;
  String challengeDescription;
  List<String> relevantFiles;
  List<Incident> supportedIncidents;
  Incident? activeIncident;
  List<String> hints;
  Evaluation? evaluation;
  PatchProposal? patch;
  ValidationResult validation;
  List<String> activity;
  bool get hasChallenge => phase != 'analyzed';
  bool get canReview => patch != null && evaluation?.permitsPatch == true;
  bool get applied => phase == 'applied' || phase == 'validated';
  bool get ready =>
      phase == 'validated' &&
      evaluation?.permitsPatch == true &&
      (practice
          ? validation.simulated && validation.status == 'passed'
          : validation.hasPassingEvidence &&
                validation.originalUnchanged == true);
  bool get practice => mode == 'Practice workspace';

  factory WorkspaceData.fromJson(Map<String, dynamic> json) => WorkspaceData(
    id: json['id'] as String,
    name: json['name'] as String,
    sample: json['sample'] as bool,
    files: Map<String, String>.from(json['files'] as Map),
    summary: json['summary'] as String,
    technologies: List<String>.from(json['technologies'] as List),
    issues: List<String>.from(json['issues'] as List),
    skills: (json['skills'] as List)
        .map((e) => SkillEstimate.fromJson(e as Map<String, dynamic>))
        .toList(),
    mode: json['mode'] as String,
    provider: json['provider'] as String,
    phase: json['phase'] as String,
    challengeTitle: json['challenge_title'] as String,
    challengeDescription: json['challenge_description'] as String,
    relevantFiles: List<String>.from(json['relevant_files'] as List),
    supportedIncidents: (json['supported_incidents'] as List? ?? const [])
        .map((item) => Incident.fromJson(item as Map<String, dynamic>))
        .toList(),
    activeIncident: json['active_incident'] == null
        ? null
        : Incident.fromJson(json['active_incident'] as Map<String, dynamic>),
    hints: List<String>.from(json['hints'] as List),
    evaluation: json['evaluation'] == null
        ? null
        : Evaluation.fromJson(json['evaluation'] as Map<String, dynamic>),
    patch: json['patch'] == null
        ? null
        : PatchProposal.fromJson(json['patch'] as Map<String, dynamic>),
    validation: ValidationResult.fromJson(
      json['validation'] as Map<String, dynamic>,
    ),
    activity: List<String>.from(json['activity'] as List),
  );
}
