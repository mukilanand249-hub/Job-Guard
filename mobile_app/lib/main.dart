import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'src/app.dart';
import 'src/controllers/scan_controller.dart';
import 'src/services/jobguard_api_client.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  runApp(
    ChangeNotifierProvider(
      create: (_) => ScanController(apiClient: JobGuardApiClient()),
      child: const JobGuardApp(),
    ),
  );
}
