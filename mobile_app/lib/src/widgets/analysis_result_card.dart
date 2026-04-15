import 'package:flutter/material.dart';

import '../models/analysis_result.dart';

class AnalysisResultCard extends StatelessWidget {
  const AnalysisResultCard({super.key, required this.result});

  final AnalysisResult result;

  Color get _accentColor {
    switch (result.verdict) {
      case 'LEGIT':
        return const Color(0xFF15803D);
      case 'SCAM':
        return const Color(0xFFB91C1C);
      default:
        return const Color(0xFFD97706);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Trust Score: ${result.trustScore}/100',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                ),
                Chip(
                  backgroundColor: _accentColor.withOpacity(0.15),
                  label: Text(
                    result.verdict,
                    style: TextStyle(
                      color: _accentColor,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              result.recommendation,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: _accentColor,
                    fontWeight: FontWeight.w600,
                  ),
            ),
            const SizedBox(height: 16),
            Text(result.analysisSummary),
            const SizedBox(height: 16),
            _FlagSection(
              title: 'Red Flags',
              items: result.redFlags,
              emptyLabel: 'None detected',
              color: const Color(0xFFB91C1C),
            ),
            const SizedBox(height: 12),
            _FlagSection(
              title: 'Green Flags',
              items: result.greenFlags,
              emptyLabel: 'None detected',
              color: const Color(0xFF15803D),
            ),
          ],
        ),
      ),
    );
  }
}

class _FlagSection extends StatelessWidget {
  const _FlagSection({
    required this.title,
    required this.items,
    required this.emptyLabel,
    required this.color,
  });

  final String title;
  final List<String> items;
  final String emptyLabel;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final visibleItems = items.isEmpty ? [emptyLabel] : items;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: color,
                fontWeight: FontWeight.w700,
              ),
        ),
        const SizedBox(height: 8),
        ...visibleItems.map(
          (item) => Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('• ', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
                Expanded(child: Text(item)),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
