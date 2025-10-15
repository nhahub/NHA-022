import 'package:socket_io_client/socket_io_client.dart' as IO;
import 'dart:async';

class SocketService {
  IO.Socket? _socket;
  bool isConnected = false;
  String? _currentUrl;

  final StreamController<Map<String, dynamic>> _responseController = 
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<bool> _connectionController = 
      StreamController<bool>.broadcast();

  Stream<Map<String, dynamic>> get responseStream => _responseController.stream;
  Stream<bool> get connectionStream => _connectionController.stream;

  void connect(String url) {
    try {
      disconnect();
      
      _currentUrl = url;
      
      print('🔗 Attempting to connect to: $url');
      
      _socket = IO.io(
        url,
        IO.OptionBuilder()
          .setTransports(['websocket', 'polling']) // ✅ Add polling as fallback
          .enableAutoConnect()
          .setTimeout(10000)
          .build(),
      );

      _setupSocketListeners();

    } catch (e) {
      print('❌ Connection error: $e');
      isConnected = false;
      _connectionController.add(false);
    }
  }

  void _setupSocketListeners() {
    _socket!.onConnect((_) {
      print('✅ Connected to WebSocket server');
      isConnected = true;
      _connectionController.add(true);
    });

    _socket!.onDisconnect((_) {
      print('❌ Disconnected from server');
      isConnected = false;
      _connectionController.add(false);
    });

    _socket!.onError((error) {
      print('❌ Socket error: $error');
      isConnected = false;
      _connectionController.add(false);
    });

    // ✅ FIXED: Handle both String and Map error responses
    _socket!.on('error', (data) {
      print('🚨 Server error: $data');
      
      Map<String, dynamic> errorData;
      if (data is String) {
        errorData = {'error': data, 'message': data};
      } else if (data is Map) {
        errorData = Map<String, dynamic>.from(data);
      } else {
        errorData = {'error': data.toString()};
      }
      
      _responseController.add(errorData);
    });

    // ✅ FIXED: Handle both String and Map responses
    _socket!.on('processing_result', (data) {
      print('📨 Server processing result: $data');
      
      Map<String, dynamic> responseData;
      if (data is String) {
        responseData = {'message': data, 'status': 'success'};
      } else if (data is Map) {
        responseData = Map<String, dynamic>.from(data);
      } else {
        responseData = {'data': data.toString()};
      }
      
      _responseController.add(responseData);
    });

    _socket!.on('response', (data) {
      print('📨 Server response: $data');
      
      Map<String, dynamic> responseData;
      if (data is String) {
        responseData = {'message': data};
      } else if (data is Map) {
        responseData = Map<String, dynamic>.from(data);
      } else {
        responseData = {'data': data.toString()};
      }
      
      _responseController.add(responseData);
    });
  }

  // Send image and data via WebSocket
  void sendImageData(String base64Image, double lon, double lat, double ppm) {
    if (!isConnected || _socket == null) {
      print('Not connected to server');
      return;
    }

    try {
      Map<String, dynamic> data = {
        'img': base64Image,
        'lon': lon,
        'lat': lat,
        'ppm': ppm,
      };

      _socket!.emit('stream_image', data);
      print('📤 Sent image data: ${base64Image.length} bytes');

    } catch (e) {
      print('Error sending image: $e');
    }
  }

  void disconnect() {
    _socket?.disconnect();
    _socket = null;
    isConnected = false;
    _currentUrl = null;
    _connectionController.add(false);
  }

  void dispose() {
    _responseController.close();
    _connectionController.close();
    disconnect();
  }
}