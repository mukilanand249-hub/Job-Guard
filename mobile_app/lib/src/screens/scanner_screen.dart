import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';

import '../controllers/scan_controller.dart';
import '../models/scan_submission_state.dart';
import 'result_screen.dart';

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  static const routeName = '/scanner';

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  final TextEditingController _textController = TextEditingController();
  final TextEditingController _urlController = TextEditingController();
  final ImagePicker _imagePicker = ImagePicker();
  File? _selectedImage;

  @override
  void dispose() {
    _textController.dispose();
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final file = await _imagePicker.pickImage(
      source: source,
      imageQuality: 85,
      maxWidth: 1800,
    );

    if (file == null) {
      return;
    }

    setState(() {
      _selectedImage = File(file.path);
    });
  }

  Future<void> _submitText(ScanController controller) async {
    if (_textController.text.trim().isEmpty) {
      _showSnackBar('Paste the job description first.');
      return;
    }

    final result = await controller.submitText(_textController.text);
    if (!mounted || result == null) {
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ResultScreen(result: result),
      ),
    );
  }

  Future<void> _submitUrl(ScanController controller) async {
    if (_urlController.text.trim().isEmpty) {
      _showSnackBar('Enter a job URL first.');
      return;
    }

    final result = await controller.submitUrl(_urlController.text.trim());
    if (!mounted || result == null) {
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ResultScreen(
          result: result,
          sourceUrl: _urlController.text.trim(),
        ),
      ),
    );
  }

  Future<void> _submitImage(ScanController controller) async {
    if (_selectedImage == null) {
      _showSnackBar('Pick an image from the camera or gallery first.');
      return;
    }

    final result = await controller.submitImage(_selectedImage!);
    if (!mounted || result == null) {
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ResultScreen(result: result),
      ),
    );
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('JobGuard Scanner'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Text'),
              Tab(text: 'URL'),
              Tab(text: 'Image'),
            ],
          ),
        ),
        body: Consumer<ScanController>(
          builder: (context, controller, _) {
            final isLoading = controller.state == ScanSubmissionState.submitting;
            final errorMessage = controller.errorMessage;

            return Stack(
              children: [
                TabBarView(
                  children: [
                    _buildTextTab(controller, isLoading),
                    _buildUrlTab(controller, isLoading),
                    _buildImageTab(controller, isLoading),
                  ],
                ),
                if (isLoading)
                  const ColoredBox(
                    color: Color(0x88000000),
                    child: Center(child: CircularProgressIndicator()),
                  ),
                if (errorMessage != null && errorMessage.isNotEmpty)
                  Positioned(
                    left: 16,
                    right: 16,
                    bottom: 16,
                    child: Material(
                      borderRadius: BorderRadius.circular(16),
                      color: Theme.of(context).colorScheme.errorContainer,
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            const Icon(Icons.error_outline),
                            const SizedBox(width: 12),
                            Expanded(child: Text(errorMessage)),
                            IconButton(
                              onPressed: controller.resetError,
                              icon: const Icon(Icons.close),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _buildTextTab(ScanController controller, bool isLoading) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Paste a job description to score it for fraud risk.',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _textController,
          minLines: 10,
          maxLines: 14,
          decoration: const InputDecoration(
            hintText: 'Paste the full job description here',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 16),
        FilledButton.icon(
          onPressed: isLoading ? null : () => _submitText(controller),
          icon: const Icon(Icons.search),
          label: const Text('Analyze Text'),
        ),
      ],
    );
  }

  Widget _buildUrlTab(ScanController controller, bool isLoading) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Paste a job posting URL. The backend will fetch and analyze it.',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _urlController,
          keyboardType: TextInputType.url,
          decoration: const InputDecoration(
            hintText: 'https://example.com/job-posting',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 16),
        FilledButton.icon(
          onPressed: isLoading ? null : () => _submitUrl(controller),
          icon: const Icon(Icons.link),
          label: const Text('Analyze URL'),
        ),
      ],
    );
  }

  Widget _buildImageTab(ScanController controller, bool isLoading) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(
          'Upload a screenshot or offer letter image for OCR-based scanning.',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        const SizedBox(height: 12),
        DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: Theme.of(context).colorScheme.outline),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                if (_selectedImage == null)
                  const Icon(Icons.image_outlined, size: 72)
                else
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12),
                    child: Image.file(_selectedImage!, height: 220, fit: BoxFit.cover),
                  ),
                const SizedBox(height: 12),
                Text(
                  _selectedImage == null ? 'No image selected yet.' : _selectedImage!.path.split(Platform.pathSeparator).last,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    OutlinedButton.icon(
                      onPressed: isLoading ? null : () => _pickImage(ImageSource.camera),
                      icon: const Icon(Icons.camera_alt_outlined),
                      label: const Text('Camera'),
                    ),
                    OutlinedButton.icon(
                      onPressed: isLoading ? null : () => _pickImage(ImageSource.gallery),
                      icon: const Icon(Icons.photo_library_outlined),
                      label: const Text('Gallery'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        FilledButton.icon(
          onPressed: isLoading ? null : () => _submitImage(controller),
          icon: const Icon(Icons.document_scanner_outlined),
          label: const Text('Analyze Image'),
        ),
      ],
    );
  }
}
