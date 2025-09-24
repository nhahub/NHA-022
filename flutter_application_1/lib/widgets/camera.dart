import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:flutter_application_1/widgets/settings.dart';
import 'package:http/http.dart' as http;
import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';

class CameraCapturePage extends StatefulWidget {
  @override
  _CameraCapturePageState createState() => _CameraCapturePageState();
}

class _CameraCapturePageState extends State<CameraCapturePage> with WidgetsBindingObserver {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  Timer? _timer;
  bool _noCameraAvailable = false;
  bool _isTimerRunning = false;

  // ✅ State variables
  String _uploadStatus = "Waiting...";
  String _imageName = "";
  List<String> _labels = [];
  File? _latestImageFile;
  int _captureCount = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _initialize();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _stopTimer();
    _controller?.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Listen to settings changes
    final settingsProvider = Provider.of<SettingsProvider>(context, listen: true);
    _handleSettingsChange(settingsProvider);
  }

  void _handleSettingsChange(SettingsProvider settingsProvider) {
    if (settingsProvider.isRunning && !_isTimerRunning) {
      // Start timer if it's not running but should be
      _startCaptureTimer();
    } else if (!settingsProvider.isRunning && _isTimerRunning) {
      // Stop timer if it's running but shouldn't be
      _stopTimer();
    } else if (_isTimerRunning && _timer != null) {
      // Restart timer if rate changed
      _restartTimerWithNewRate();
    }
  }

  void _restartTimerWithNewRate() {
    final settingsProvider = Provider.of<SettingsProvider>(context, listen: false);
    print('🔄 Restarting timer with new rate: ${settingsProvider.rate}s');
    _stopTimer();
    _startCaptureTimer();
  }

  void _stopTimer() {
    if (_timer != null) {
      _timer!.cancel();
      _timer = null;
      _isTimerRunning = false;
      print('⏹️ Timer stopped');
    }
  }

  void _startCaptureTimer() {
    if (_isTimerRunning) {
      _stopTimer();
    }

    final settingsProvider = Provider.of<SettingsProvider>(context, listen: false);
    
    if (!settingsProvider.isRunning) {
      print('⏸️ Camera not running - not starting timer');
      return;
    }

    if (_controller == null || !_controller!.value.isInitialized) {
      print('📷 Camera not ready - not starting timer');
      return;
    }

    print('🔄 Starting capture timer with interval: ${settingsProvider.rate}s');
    
    // Don't capture immediately - wait for the first interval
    _timer = Timer.periodic(
      Duration(seconds: settingsProvider.rate),
      (timer) {
        _takePictureAndSendMultipart();
      },
    );
    
    _isTimerRunning = true;
    
    // Take first picture after a short delay instead of immediately
    Future.delayed(Duration(milliseconds: 500), () {
      if (_isTimerRunning) {
        _takePictureAndSendMultipart();
      }
    });
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

      // Start the capture timer after camera is ready
      final settingsProvider = Provider.of<SettingsProvider>(context, listen: false);
      if (settingsProvider.isRunning) {
        _startCaptureTimer();
      }

    } catch (e) {
      print('Error initializing camera: $e');
      setState(() {
        _noCameraAvailable = true;
      });
    }
  }

  Future<void> _takePictureAndSendMultipart() async {
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
        _latestImageFile = imageFile;
        _captureCount++;
      });

      print('✅ Image captured: ${file.path}');

      // 📍 Get location
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      print('📍 Location: ${position.latitude}, ${position.longitude}');

      // Get current settings
      final settingsProvider = Provider.of<SettingsProvider>(context, listen: false);

      // 🌐 Prepare multipart request
      var uri = Uri.parse(settingsProvider.api);

      var request = http.MultipartRequest('POST', uri);
      request.files.add(
        await http.MultipartFile.fromPath('image', imageFile.path),
      );
      request.fields['lon'] = position.longitude.toString();
      request.fields['lat'] = position.latitude.toString();
      request.fields['ppm'] = settingsProvider.ppm.toString();

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
  Widget build(BuildContext context) {
    return Consumer<SettingsProvider>(
      builder: (context, settingsProvider, child) {
        if (settingsProvider.isLoading) {
          return Scaffold(
            appBar: AppBar(title: Text('Camera Multipart Upload')),
            body: Center(child: CircularProgressIndicator()),
          );
        }

        return Scaffold(
          appBar: AppBar(
            title: Text('Camera Multipart Upload'),
            actions: [
              IconButton(
                icon: Icon(Icons.settings),
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => SettingsPage()),
                  );
                },
              ),
            ],
          ),
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

                        // Settings Status Bar
                        Container(
                          padding: EdgeInsets.all(8),
                          color: Colors.grey[100],
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _buildStatusItem('Status', settingsProvider.isRunning ? 'Running' : 'Paused', 
                                  settingsProvider.isRunning ? Icons.check_circle : Icons.pause_circle,
                                  settingsProvider.isRunning ? Colors.green : Colors.orange),
                              _buildStatusItem('PPM', '${settingsProvider.ppm.toInt()}', 
                                  Icons.photo_camera, Colors.blue),
                              _buildStatusItem('Interval', '${settingsProvider.rate}s', 
                                  Icons.timer, Colors.purple),
                              _buildStatusItem('Captures', '$_captureCount', 
                                  Icons.camera_alt, Colors.red),
                            ],
                          ),
                        ),

                        // 🖼️ Preview the last captured image
                        if (_latestImageFile != null)
                          Container(
                            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
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
      },
    );
  }

  Widget _buildStatusItem(String label, String value, IconData icon, Color color) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 16),
        SizedBox(height: 2),
        Text(value, style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
        Text(label, style: TextStyle(fontSize: 10, color: Colors.grey)),
      ],
    );
  }
}