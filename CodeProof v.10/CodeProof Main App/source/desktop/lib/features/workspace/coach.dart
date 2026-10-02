import 'package:flutter/material.dart';

import '../../app/theme.dart';
import '../../domain/workspace_controller.dart';
import '../../ui/glass.dart';

class CoachPanel extends StatelessWidget {
  const CoachPanel({
    super.key,
    required this.controller,
    required this.explanation,
    this.onClose,
    this.onAnalyze,
  });
  final WorkspaceController controller;
  final TextEditingController explanation;
  final VoidCallback? onClose;
  final VoidCallback? onAnalyze;
  @override
  Widget build(BuildContext context) {
    final data = controller.data!;
    return GlassPanel(
      blur: true,
      padding: EdgeInsets.zero,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.auto_awesome_outlined,
                  color: Palette.of(context).cyan,
                  size: 19,
                ),
                const SizedBox(width: 10),
                const Expanded(
                  child: Text(
                    'Your engineering coach',
                    style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                  ),
                ),
                if (onClose != null)
                  IconButton(
                    tooltip: 'Close coach',
                    onPressed: onClose,
                    icon: const Icon(Icons.close, size: 17),
                  ),
              ],
            ),
            const SizedBox(height: 15),
            StatusBadge(
              data.sample ? 'Guided practice' : data.provider,
              color: Palette.of(context).violet,
            ),
            const SizedBox(height: 24),
            Text(
              data.hasChallenge
                  ? data.challengeTitle
                  : 'Let’s understand your project.',
              style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 17),
            ),
            const SizedBox(height: 10),
            if (!data.hasChallenge) ...[
              Text(
                'Start with the big picture. Explore the analysis, follow a skill to its source files, then investigate a failure.',
                style: TextStyle(color: Palette.of(context).muted),
              ),
              const SizedBox(height: 23),
              GlassPanel(
                padding: const EdgeInsets.all(16),
                tint: Palette.of(context).cyan,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.tips_and_updates_outlined,
                      color: Palette.of(context).cyan,
                      size: 22,
                    ),
                    const SizedBox(height: 12),
                    const Text(
                      'A good first question',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'What does this application expect at its boundaries — and what happens when it receives something else?',
                      style: TextStyle(
                        color: Palette.of(context).muted,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: () {
                    controller.selectTab(WorkspaceTab.skills);
                    onClose?.call();
                  },
                  child: const Text('Explore skill map'),
                ),
              ),
            ] else ...[
              StatusBadge(
                data.ready
                    ? 'Ready for review'
                    : data.canReview
                    ? 'Patch unlocked'
                    : 'Investigating',
                color: data.canReview
                    ? Palette.of(context).mint
                    : Palette.of(context).cyan,
              ),
              const SizedBox(height: 22),
              const Divider(),
              const SizedBox(height: 18),
              SectionTitle(
                'Progressive hints',
                trailing: Text(
                  '${data.hints.length} / 4',
                  style: TextStyle(
                    color: Palette.of(context).muted,
                    fontSize: 11,
                  ),
                ),
              ),
              Text(
                'A little direction, only when you need it.',
                style: TextStyle(
                  color: Palette.of(context).muted,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed:
                      data.phase == 'investigating' &&
                          data.hints.length < 4 &&
                          !controller.busy
                      ? () => controller.act('hint')
                      : null,
                  icon: const Icon(Icons.lightbulb_outline, size: 16),
                  label: Text(
                    data.hints.length < 4 ? 'Get hint' : 'All hints revealed',
                  ),
                ),
              ),
              for (final (index, hint) in data.hints.indexed)
                Padding(
                  padding: const EdgeInsets.only(top: 12),
                  child: GlassPanel(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '0${index + 1}  ${['Direction', 'Component', 'Specific area', 'Near solution'][index]}',
                          style: TextStyle(
                            color: Palette.of(context).cyan,
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 7),
                        Text(hint, style: const TextStyle(fontSize: 12)),
                      ],
                    ),
                  ),
                ),
              const SizedBox(height: 22),
              const Divider(),
              const SizedBox(height: 18),
              if (!data.practice && data.provider == 'Local inspection') ...[
                const Text(
                  'These controlled-fault hints run locally. Enable AI analysis to review your explanation and generate a patch.',
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: controller.busy
                      ? null
                      : () {
                          onClose?.call();
                          onAnalyze?.call();
                        },
                  icon: const Icon(Icons.auto_awesome, size: 16),
                  label: const Text('Enable AI review'),
                ),
                const SizedBox(height: 18),
              ],
              const SectionTitle('Explain before you fix'),
              Text(
                'Describe the cause and the evidence that led you there.',
                style: TextStyle(
                  color: Palette.of(context).muted,
                  fontSize: 12,
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                key: const Key('explanation-field'),
                controller: explanation,
                minLines: 4,
                maxLines: 8,
                maxLength: 8000,
                enabled: !controller.busy && !data.applied,
                decoration: const InputDecoration(
                  hintText: 'I think the request fails because…',
                  counterText: '',
                  labelText: 'Your explanation',
                ),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: PrimaryButton(
                  'Evaluate explanation',
                  icon: Icons.arrow_forward_rounded,
                  onPressed:
                      !controller.busy &&
                          !data.applied &&
                          (data.practice || data.provider != 'Local inspection')
                      ? () async {
                          await controller.act('explanation', {
                            'explanation': explanation.text,
                          });
                          if (controller.data?.canReview == true) {
                            onClose?.call();
                          }
                        }
                      : null,
                ),
              ),
              if (data.evaluation != null)
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: GlassPanel(
                    padding: const EdgeInsets.all(14),
                    tint: data.evaluation!.permitsPatch
                        ? Palette.of(context).mint
                        : Palette.of(context).amber,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${data.evaluation!.label} · ${(data.evaluation!.score * 100).round()}%',
                          style: TextStyle(
                            color: data.evaluation!.permitsPatch
                                ? Palette.of(context).mint
                                : Palette.of(context).amber,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          data.evaluation!.feedback,
                          style: const TextStyle(fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
            const SizedBox(height: 24),
            Text(
              data.sample
                  ? 'Practice coaching uses curated hints and a keyword-based explanation check. It is not an AI assessment.'
                  : data.activeIncident != null
                  ? 'Controlled-fault hints are local. AI review uses the redacted snapshot only after you enable AI analysis.'
                  : 'AI coaching uses your redacted snapshot only after you enable AI analysis.',
              style: TextStyle(
                fontSize: 10,
                color: Palette.of(context).muted,
                height: 1.6,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
