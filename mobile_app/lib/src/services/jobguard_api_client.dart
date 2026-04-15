import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../models/analysis_result.dart';
import '../models/api_error.dart';

class JobGuardApiClient {
  JobGuardApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  static const String _defaultBaseUrl = String.fromEnvironment(
    'JOBGUARD_API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );

  Uri _uri(String path) => Uri.parse('$_defaultBaseUrl$path');

  Future<void> healthCheck() async {
    final response = await _client.get(_uri('/health')).timeout(const Duration(seconds: 10));
    if (response.statusCode != 200) {
      throw const ApiError(code: 'server_unavailable', message: 'Backend health check failed.');
    }
  }

  Future<AnalysisResult> analyzeText(String text) async {
    final response = await _client
        .post(
          _uri('/analyze-text'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'text': text}),
        )
        .timeout(const Duration(seconds: 45));
    return _parseAnalysisResponse(response);
  }

  Future<AnalysisResult> analyzeUrl(String url) async {
    final response = await _client
        .post(
          _uri('/analyze-url'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'url': url}),
        )
        .timeout(const Duration(seconds: 60));
    return _parseAnalysisResponse(response);
  }

  Future<AnalysisResult> analyzeImage(File imageFile) async {
    final request = http.MultipartRequest('POST', _uri('/analyze-image'))
      ..files.add(await http.MultipartFile.fromPath('image', imageFile.path));

    final streamedResponse = await request.send().timeout(const Duration(seconds: 60));
    final response = await http.Response.fromStream(streamedResponse);
    return _parseAnalysisResponse(response);
  }

  Future<void> reportScam({
    required String url,
    required String reason,
  }) async {
    final response = await _client
        .post(
          _uri('/report-scam'),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode({'url': url, 'reason': reason}),
        )
        .timeout(const Duration(seconds: 20));

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw _parseApiError(response);
    }
  }

  AnalysisResult _parseAnalysisResponse(http.Response response) {
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw _parseApiError(response);
    }

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return AnalysisResult.fromJson(body);
  }

  ApiError _parseApiError(http.Response response) {
    try {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return ApiError.fromJson(body);
    } catch (_) {
      return ApiError(
        code: 'server_unavailable',
        message: 'The server returned an unexpected response (${response.statusCode}).',
      );
    }
  }
}
