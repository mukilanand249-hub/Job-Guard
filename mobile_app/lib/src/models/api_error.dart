class ApiError implements Exception {
  const ApiError({
    required this.code,
    required this.message,
  });

  final String code;
  final String message;

  factory ApiError.fromJson(Map<String, dynamic> json) {
    final error = json['error'] as Map<String, dynamic>? ?? const {};
    return ApiError(
      code: error['code']?.toString() ?? 'unknown_error',
      message: error['message']?.toString() ?? 'Something went wrong.',
    );
  }

  @override
  String toString() => message;
}
