import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' as path;
import 'results_screen.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  CameraController? _cameraController;
  Future<void>? _initializeControllerFuture;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    try {
      final cameras = await availableCameras();

      if (cameras.isEmpty) {
        throw Exception("No cameras available on this device.");
      }

      final rearCamera = cameras.firstWhere(
        (camera) => camera.lensDirection == CameraLensDirection.back,
        orElse: () => cameras.first,
      );

      _cameraController = CameraController(
        rearCamera,
        ResolutionPreset.medium,
        enableAudio: false,
      );

      _initializeControllerFuture = _cameraController!.initialize();
      setState(() {});
    } catch (e) {
      print('Camera init error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Camera not available: $e')),
        );
      }
    }
  }

  Future<void> _capturePhoto() async {
    try {
      await _initializeControllerFuture;
      final image = await _cameraController!.takePicture();
      print('📸 Captured image path: ${image.path}');

      final uri = Uri.parse('http://192.168.2.102:5050/upload'); // 🔥 Mac IP

      final request = http.MultipartRequest('POST', uri);
      request.files.add(await http.MultipartFile.fromPath(
        'image',
        image.path,
        filename: path.basename(image.path),
      ));

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final detectedObjects = data['detected_objects'];
        final objectsList = (detectedObjects as List<dynamic>).join(', ');
        print('🧠 Detected objects: $objectsList');
        if (mounted) {
          Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ResultsScreen(
              detectedObjects: List<String>.from(detectedObjects),
            ),
          ),
        );
        }
      } else {
        print('❌ Upload failed with status: ${response.statusCode}');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Upload failed ❌ ${response.statusCode}')),
          );
        }
      }
    } catch (e) {
      print('❌ Upload error: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Upload error: $e')),
        );
      }
    }
  }

  @override
  void dispose() {
    _cameraController?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Scan Grocery Item")),
      body: _initializeControllerFuture == null
          ? const Center(child: CircularProgressIndicator())
          : Stack(
              children: [
                FutureBuilder(
                  future: _initializeControllerFuture,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.done) {
                      return CameraPreview(_cameraController!);
                    } else {
                      return const Center(child: CircularProgressIndicator());
                    }
                  },
                ),
                Positioned(
                  bottom: 30,
                  left: MediaQuery.of(context).size.width / 2 - 30,
                  child: FloatingActionButton(
                    onPressed: _capturePhoto,
                    child: const Icon(Icons.camera),
                  ),
                ),
              ],
            ),
    );
  }
}
