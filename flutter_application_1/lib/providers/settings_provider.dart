// lib/providers/settings_provider.dart
import 'package:flutter/foundation.dart';
import '../models/settings_model.dart';
import '../services/settings_service.dart';

class SettingsProvider with ChangeNotifier {
  AppSettings? _settings; // Make it nullable initially
  final SettingsService _settingsService = SettingsService();
  bool _isLoading = true;

  AppSettings get settings {
    if (_settings == null) {
      // Return default settings if not loaded yet
      return AppSettings(
        running: true,
        ppm: 2500,
        rate: 5,
        api: 'http://192.168.1.7:5000/upload-image',
      );
    }
    return _settings!;
  }

  bool get isRunning => settings.running;
  double get ppm => settings.ppm;
  int get rate => settings.rate;
  String get api => settings.api;
  bool get isLoading => _isLoading;

  SettingsProvider() {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      _isLoading = true;
      notifyListeners();
      
      _settings = await _settingsService.getSettings();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      print('Error loading settings: $e');
      // Fallback to default settings
      _settings = AppSettings(
        running: true,
        ppm: 2500,
        rate: 5,
        api: 'http://192.168.1.7:5000/upload-image',
      );
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateSettings(AppSettings newSettings) async {
    _settings = newSettings;
    await _settingsService.saveSettings(newSettings);
    notifyListeners();
  }

  Future<void> setRunning(bool running) async {
    _settings = settings.copyWith(running: running);
    await _settingsService.saveSettings(_settings!);
    notifyListeners();
  }

  Future<void> setPpm(double ppm) async {
    _settings = settings.copyWith(ppm: ppm);
    await _settingsService.saveSettings(_settings!);
    notifyListeners();
  }

  Future<void> setRate(int rate) async {
    _settings = settings.copyWith(rate: rate);
    await _settingsService.saveSettings(_settings!);
    notifyListeners();
  }

  Future<void> setApi(String api) async {
    _settings = settings.copyWith(api: api);
    await _settingsService.saveSettings(_settings!);
    notifyListeners();
  }

  Future<void> resetToDefaults() async {
    _settings = AppSettings(
      running: true,
      ppm: 2500,
      rate: 5,
      api: 'http://192.168.1.7:5000/upload-image',
    );
    await _settingsService.saveSettings(_settings!);
    notifyListeners();
  }
}