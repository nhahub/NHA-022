// lib/services/settings_service.dart
import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';
import '../models/settings_model.dart';

class SettingsService {
  static const String _settingsKey = 'app_settings';

  Future<AppSettings> getSettings() async {
    final prefs = await SharedPreferences.getInstance();
    final settingsJson = prefs.getString(_settingsKey);
    
    if (settingsJson != null) {
      try {
        final settingsMap = Map<String, dynamic>.from(json.decode(settingsJson));
        return AppSettings.fromMap(settingsMap);
      } catch (e) {
        print('Error loading settings: $e');
      }
    }
    
    // Return default settings
    return AppSettings(
      running: true,
      ppm: 2500,
      rate: 5,
      api: '',
    );
  }

  Future<void> saveSettings(AppSettings settings) async {
    final prefs = await SharedPreferences.getInstance();
    final settingsJson = json.encode(settings.toMap());
    await prefs.setString(_settingsKey, settingsJson);
  }
}