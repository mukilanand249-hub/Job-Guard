import 'package:flutter_test/flutter_test.dart';
import 'package:jobguard_mobile/src/models/analysis_result.dart';

void main() {
  test('analysis result parses API payload', () {
    final result = AnalysisResult.fromJson({
      'scan_id': 21,
      'trust_score': 77,
      'verdict': 'SUSPICIOUS',
      'recommendation': 'Proceed with Caution',
      'analysis_summary': 'There are a few warning signs.',
      'red_flags': ['Telegram contact only'],
      'green_flags': ['Detailed description'],
    });

    expect(result.scanId, 21);
    expect(result.verdict, 'SUSPICIOUS');
    expect(result.redFlags, ['Telegram contact only']);
  });
}
