import 'package:flutter/material.dart';

class ResultsScreen extends StatelessWidget {
  final List<String> detectedObjects;

  const ResultsScreen({super.key, required this.detectedObjects});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Detected Items')),
      body: ListView.builder(
        itemCount: detectedObjects.length,
        itemBuilder: (context, index) {
          final item = detectedObjects[index];
          return ListTile(
            leading: const Icon(Icons.check_circle_outline),
            title: Text(item, style: const TextStyle(fontSize: 18)),
          );
        },
      ),
    );
  }
}
