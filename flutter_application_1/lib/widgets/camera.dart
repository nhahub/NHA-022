import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:path/path.dart' show join;
import 'package:path_provider/path_provider.dart';

class CameraCapturePage extends StatefulWidget {
  @override
  _CameraCapturePageState createState() => _CameraCapturePageState();
}

class _CameraCapturePageState extends State<CameraCapturePage> {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  Timer? _timer;
  bool _noCameraAvailable = false;

  @override
  void initState() {
    super.initState();
    initializeCamera();
  }

  Future<void> initializeCamera() async {
    try {
      _cameras = await availableCameras();

      if (_cameras == null || _cameras!.isEmpty) {
        setState(() {
          _noCameraAvailable = true;
        });
        showNoCameraDialog();
        return;
      }

      _controller = CameraController(
        _cameras![0],
        ResolutionPreset.medium,
      );

      await _controller!.initialize();
      setState(() {});
      startCapturing();
    } catch (e) {
      print('Error initializing camera: $e');
      setState(() {
        _noCameraAvailable = true;
      });
      showNoCameraDialog();
    }
  }

  void showNoCameraDialog() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: Text('No Camera Found'),
          content: Text('This device does not have a camera or it cannot be accessed.'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                Navigator.of(context).maybePop(); // Go back if possible
              },
              child: Text('OK'),
            ),
          ],
        ),
      );
    });
  }

  void startCapturing() {
    _timer = Timer.periodic(Duration(seconds: 10), (timer) {
      takePicture();
    });
  }

  Future<void> takePicture() async {
    if (_controller == null || !_controller!.value.isInitialized || _controller!.value.isTakingPicture) {
      return;
    }

    try {
      final directory = await getTemporaryDirectory();
      final filePath = join(directory.path, '${DateTime.now().millisecondsSinceEpoch}.jpg');

      XFile file = await _controller!.takePicture();
      final imageFile = File(file.path);
      await imageFile.copy(filePath);

      print('Image saved to $filePath');
    } catch (e) {
      print('Error taking picture: $e');
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
      appBar: AppBar(title: Text('Camera Capture Every Second')),
      body: _noCameraAvailable
          ? Center(child: Text('No camera available on this device.'))
          : (_controller == null || !_controller!.value.isInitialized)
              ? Center(child: CircularProgressIndicator())
              : CameraPreview(_controller!),
    );
  }
}
