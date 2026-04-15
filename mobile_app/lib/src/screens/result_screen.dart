import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../controllers/scan_controller.dart';
import '../models/analysis_result.dart';
import '../widgets/analysis_result_card.dart';

class ResultScreen extends StatelessWidget {
  const ResultScreen({
    super.key,
    required this.result,
    this.sourceUrl,
  });

  final AnalysisResult result;
  final String? sourceUrl;

  @override
  Widget build(BuildContext context) {
    final controller = context.read<ScanController>();

    return Scaffold(
      appBar: AppBar(title: const Text('Analysis Result')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          AnalysisResultCard(result: result),
          if (sourceUrl != null && sourceUrl!.isNotEmpty) ...[
            const SizedBox(height: 16),
            FilledButton.tonalIcon(
              onPressed: () async {
                final messenger = ScaffoldMessenger.of(context);
                final success = await controller.reportScam(
                  url: sourceUrl!,
                  reason: 'Reported from Android app after scan',
                );
                if (!context.mounted) {
                  return;
                }
                messenger.showSnackBar(
                  SnackBar(
                    content: Text(
                      success
                          ? 'Scam report submitted successfully.'
                          : controller.errorMessage ?? 'Could not submit report.',
                    ),
                  ),
                );
              },
              icon: const Icon(Icons.flag_outlined),
              label: const Text('Report As Scam'),
            ),
          ],
        ],
      ),
    );
  }
}
