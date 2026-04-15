class AnalysisResult {
  const AnalysisResult({
    required this.scanId,
    required this.trustScore,
    required this.verdict,
    required this.recommendation,
    required this.analysisSummary,
    required this.redFlags,
    required this.greenFlags,
  });

  final int? scanId;
  final int trustScore;
  final String verdict;
  final String recommendation;
  final String analysisSummary;
  final List<String> redFlags;
  final List<String> greenFlags;

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    return AnalysisResult(
      scanId: json['scan_id'] as int?,
      trustScore: json['trust_score'] as int? ?? 0,
      verdict: json['verdict'] as String? ?? 'UNKNOWN',
      recommendation: json['recommendation'] as String? ?? '',
      analysisSummary: json['analysis_summary'] as String? ?? '',
      redFlags: (json['red_flags'] as List<dynamic>? ?? const [])
          .map((item) => item.toString())
          .toList(),
      greenFlags: (json['green_flags'] as List<dynamic>? ?? const [])
          .map((item) => item.toString())
          .toList(),
    );
  }
}
