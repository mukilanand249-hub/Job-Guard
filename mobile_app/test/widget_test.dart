import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:jobguard_mobile/src/controllers/scan_controller.dart';
import 'package:jobguard_mobile/src/services/jobguard_api_client.dart';
import 'package:jobguard_mobile/src/app.dart';

void main() {
  testWidgets('app boots to splash screen', (WidgetTester tester) async {
    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => ScanController(apiClient: JobGuardApiClient()),
        child: const JobGuardApp(),
      ),
    );

    expect(find.text('JobGuard Mobile'), findsOneWidget);
    expect(find.text('AI-powered job fraud scanner'), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 1300));
    await tester.pumpAndSettle();
  });
}
