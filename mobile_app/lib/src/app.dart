import 'package:flutter/material.dart';

import 'screens/scanner_screen.dart';
import 'screens/splash_screen.dart';

class JobGuardApp extends StatelessWidget {
  const JobGuardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'JobGuard Mobile',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0F766E),
          brightness: Brightness.light,
        ),
        useMaterial3: true,
      ),
      routes: {
        SplashScreen.routeName: (_) => const SplashScreen(),
        ScannerScreen.routeName: (_) => const ScannerScreen(),
      },
      initialRoute: SplashScreen.routeName,
    );
  }
}
