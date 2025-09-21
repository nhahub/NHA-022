import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'package:path/path.dart' show join;
import 'package:path_provider/path_provider.dart';
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';

class CameraCapturePage extends StatefulWidget {
  @override
  _CameraCapturePageState createState() => _CameraCapturePageState();
}

class _CameraCapturePageState extends State<CameraCapturePage> {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  Timer? _timer;
  bool _noCameraAvailable = false;

  // ✅ State variables
  String _uploadStatus = "Waiting...";
  String _imageName = "";
  List<String> _labels = [];
  File? _latestImageFile; // ✅ For image preview

  @override
  void initState() {
    super.initState();
    _initialize();
  }

  Future<void> _initialize() async {
    await _requestPermissions();
    await initializeCamera();
  }

  Future<void> _requestPermissions() async {
    await [
      Permission.camera,
      Permission.locationWhenInUse,
    ].request();
  }

  Future<void> initializeCamera() async {
    try {
      _cameras = await availableCameras();

      if (_cameras == null || _cameras!.isEmpty) {
        setState(() {
          _noCameraAvailable = true;
        });
        return;
      }

      _controller = CameraController(_cameras![0], ResolutionPreset.medium);
      await _controller!.initialize();
      setState(() {});

      // 📸 Take first picture immediately
      await takePictureAndSendMultipart();

      // 🔁 Then start timer to capture every 10 seconds
      _timer = Timer.periodic(Duration(seconds: 10), (timer) async {
        await takePictureAndSendMultipart();
      });
    } catch (e) {
      print('Error initializing camera: $e');
      setState(() {
        _noCameraAvailable = true;
      });
    }
  }

  Future<void> takePictureAndSendMultipart() async {
    if (_controller == null ||
        !_controller!.value.isInitialized ||
        _controller!.value.isTakingPicture) {
      return;
    }

    try {
      setState(() {
        _uploadStatus = "📸 Capturing image...";
      });

      // 📸 Capture image
      XFile file = await _controller!.takePicture();
      final imageFile = File(file.path);
      setState(() {
        _latestImageFile = imageFile; // ✅ Store for preview
      });

      print('✅ Image captured: ${file.path}');

      // 📍 Get location
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      print('📍 Location: ${position.latitude}, ${position.longitude}');

      // 🌐 Prepare multipart request
      var uri = Uri.parse("http://192.168.1.7:5000/upload-image"); // Change to your Flask IP

      var request = http.MultipartRequest('POST', uri);
      request.files.add(
        await http.MultipartFile.fromPath('image', imageFile.path),
      );
      request.fields['lon'] = position.longitude.toString();
      request.fields['lat'] = position.latitude.toString();
      request.fields['ppm'] = '200.0'; // You can make this dynamic if needed

      setState(() {
        _uploadStatus = "🔄 Uploading image...";
      });

      var response = await request.send();
      String respStr = await response.stream.bytesToString();
      print('📥 Response status: ${response.statusCode}');
      print('📥 Response body: $respStr');

      if (response.statusCode == 200) {
        final decoded = jsonDecode(respStr);
        setState(() {
          _uploadStatus = "✅ Upload successful!";
          _imageName = decoded['image'] ?? '';
          _labels = List<String>.from(decoded['labels'] ?? []);
        });
      } else {
        setState(() {
          _uploadStatus = "❌ Upload failed (${response.statusCode})";
          _imageName = '';
          _labels = [];
        });
      }
    } catch (e) {
      print('❌ Error: $e');
      setState(() {
        _uploadStatus = "❌ Error: $e";
        _imageName = '';
        _labels = [];
      });
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Camera Multipart Upload')),
      body: _noCameraAvailable
          ? Center(child: Text('No camera available on this device.'))
          : (_controller == null || !_controller!.value.isInitialized)
              ? Center(child: CircularProgressIndicator())
              : Column(
                  children: [
                    // 🖼️ Logo at the top
                    Padding(
                      padding: const EdgeInsets.all(8.0),
                      child: Image.asset(
                        'assets/images/logo.png',
                        height: 80,
                      ),
                    ),

                    // 🖼️ Preview the last captured image
                    if (_latestImageFile != null)
                      Container(
                        margin:
                            const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        height: 150,
                        decoration: BoxDecoration(
                          border: Border.all(color: Colors.blueGrey),
                        ),
                        child: Image.file(
                          _latestImageFile!,
                          fit: BoxFit.cover,
                          width: double.infinity,
                        ),
                      ),

                    // 📷 Camera Preview
                    Expanded(
                      flex: 3,
                      child: CameraPreview(_controller!),
                    ),

                    // ℹ️ Upload Status + Info
                    Expanded(
                      flex: 2,
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        width: double.infinity,
                        color: Colors.grey.shade100,
                        child: SingleChildScrollView(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text("Status: $_uploadStatus",
                                  style: TextStyle(fontSize: 16)),
                              SizedBox(height: 10),
                              Text("Image Name: $_imageName",
                                  style: TextStyle(fontSize: 14)),
                              SizedBox(height: 10),
                              Text("Detected Labels:",
                                  style:
                                      TextStyle(fontWeight: FontWeight.bold)),
                              SizedBox(height: 5),
                              Wrap(
                                spacing: 8,
                                children: _labels.isEmpty
                                    ? [Text("No cracks detected.")]
                                    : _labels
                                        .map((label) => Chip(label: Text(label)))
                                        .toList(),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
    );
  }
}
