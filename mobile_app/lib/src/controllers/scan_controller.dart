import 'dart:io';

import 'package:flutter/material.dart';

import '../models/analysis_result.dart';
import '../models/api_error.dart';
import '../models/scan_submission_state.dart';
import '../services/jobguard_api_client.dart';

class ScanController extends ChangeNotifier {
  ScanController({required JobGuardApiClient apiClient}) : _apiClient = apiClient;

  final JobGuardApiClient _apiClient;

  ScanSubmissionState state = ScanSubmissionState.idle;
  AnalysisResult? latestResult;
  String? latestUrl;
  String? errorMessage;

  Future<AnalysisResult?> submitText(String text) async {
    return _submit(() => _apiClient.analyzeText(text), latestUrlValue: null);
  }

  Future<AnalysisResult?> submitUrl(String url) async {
    return _submit(() => _apiClient.analyzeUrl(url), latestUrlValue: url);
  }

  Future<AnalysisResult?> submitImage(File imageFile) async {
    return _submit(() => _apiClient.analyzeImage(imageFile), latestUrlValue: null);
  }

  Future<bool> reportScam({
    required String url,
    required String reason,
  }) async {
    try {
      await _apiClient.reportScam(url: url, reason: reason);
      return true;
    } on ApiError catch (error) {
      errorMessage = error.message;
      notifyListeners();
      return false;
    } catch (_) {
      errorMessage = 'Could not submit the scam report right now.';
      notifyListeners();
      return false;
    }
  }

  void resetError() {
    errorMessage = null;
    notifyListeners();
  }

  Future<AnalysisResult?> _submit(
    Future<AnalysisResult> Function() action, {
    required String? latestUrlValue,
  }) async {
    state = ScanSubmissionState.submitting;
    errorMessage = null;
    notifyListeners();

    try {
      final result = await action();
      latestResult = result;
      latestUrl = latestUrlValue;
      state = ScanSubmissionState.success;
      notifyListeners();
      return result;
    } on ApiError catch (error) {
      state = ScanSubmissionState.failure;
      errorMessage = error.message;
      notifyListeners();
      return null;
    } catch (_) {
      state = ScanSubmissionState.failure;
      errorMessage = 'Unable to reach the server. Please try again.';
      notifyListeners();
      return null;
    }
  }
}
