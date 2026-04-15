import 'package:flutter_test/flutter_test.dart';
import 'package:jobguard_mobile/src/models/analysis_result.dart';
import 'package:jobguard_mobile/src/widgets/analysis_result_card.dart';
import 'package:flutter/material.dart';

void main() {
  testWidgets('result card shows verdict and recommendation', (tester) async {
    const result = AnalysisResult(
      scanId: 1,
      trustScore: 32,
      verdict: 'SCAM',
      recommendation: 'Do Not Apply',
      analysisSummary: 'Multiple high-risk indicators were detected.',
      redFlags: ['Listed in Community Blacklist'],
      greenFlags: [],
    );

    await tester.pumpWidget(
      const MaterialApp(
        home: Scaffold(
          body: AnalysisResultCard(result: result),
        ),
      ),
    );

    expect(find.text('SCAM'), findsOneWidget);
    expect(find.text('Do Not Apply'), findsOneWidget);
  });
}
