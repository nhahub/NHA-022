import 'package:flutter/material.dart';
import 'package:flutter_application_1/models/settings_model.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({super.key});

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  final _apiController = TextEditingController();

  @override
  void initState() {
    super.initState();
    final settings = Provider.of<SettingsProvider>(context, listen: false);
    _apiController.text = settings.api;
  }

  @override
  void dispose() {
    _apiController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Camera Settings'),
        actions: [
          IconButton(
            icon: const Icon(Icons.restore),
            onPressed: _resetToDefaults,
            tooltip: 'Reset to Defaults',
          ),
        ],
      ),
      body: Consumer<SettingsProvider>(
        builder: (context, settingsProvider, child) {
          final settings = settingsProvider.settings;
          
          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              _buildRunningSwitch(settings, settingsProvider),
              const SizedBox(height: 20),
              _buildPpmSlider(settings, settingsProvider),
              const SizedBox(height: 20),
              _buildRateSlider(settings, settingsProvider),
              const SizedBox(height: 20),
              _buildApiField(settings, settingsProvider),
              const SizedBox(height: 30),
              _buildStatusCard(settings),
            ],
          );
        },
      ),
    );
  }

  Widget _buildRunningSwitch(AppSettings settings, SettingsProvider provider) {
    return Card(
      child: SwitchListTile(
        title: const Text('Camera Running'),
        subtitle: const Text('Enable/disable automatic captures'),
        value: settings.running,
        onChanged: (value) => provider.setRunning(value),
        secondary: Icon(
          settings.running ? Icons.videocam : Icons.videocam_off,
          color: settings.running ? Colors.green : Colors.grey,
        ),
      ),
    );
  }

  Widget _buildPpmSlider(AppSettings settings, SettingsProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.photo_camera, color: Colors.blue),
                const SizedBox(width: 8),
                const Text('Pixels per Meter (PPM)'),
                const Spacer(),
                Chip(
                  label: Text('${settings.ppm.toInt()} PPM'),
                  backgroundColor: Colors.blue.withOpacity(0.1),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Slider(
              value: settings.ppm,
              min: 100,
              max: 10000,
              divisions: 99,
              label: '${settings.ppm.toInt()} PPM',
              onChanged: (value) => provider.setPpm(value),
            ),
            const SizedBox(height: 4),
            const Text(
              'Higher PPM = more detail, larger files',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRateSlider(AppSettings settings, SettingsProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.timer, color: Colors.orange),
                const SizedBox(width: 8),
                const Text('Capture Interval'),
                const Spacer(),
                Chip(
                  label: Text('${settings.rate}s'),
                  backgroundColor: Colors.orange.withOpacity(0.1),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Slider(
              value: settings.rate.toDouble(),
              min: 1,
              max: 60,
              divisions: 59,
              label: '${settings.rate} seconds',
              onChanged: (value) => provider.setRate(value.toInt()),
            ),
            const SizedBox(height: 4),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Interval between captures',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
                Text(
                  '~${(60 / settings.rate).toStringAsFixed(1)} captures/min',
                  style: const TextStyle(
                    color: Colors.green,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildApiField(AppSettings settings, SettingsProvider provider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.api, color: Colors.green),
                const SizedBox(width: 8),
                const Text('API Endpoint'),
              ],
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _apiController,
              decoration: const InputDecoration(
                hintText: 'http://192.168.1.7:5000/upload-image',
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              onChanged: (value) => provider.setApi(value),
            ),
            const SizedBox(height: 4),
            const Text(
              'URL for sending camera data to Flask server',
              style: TextStyle(color: Colors.grey, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusCard(AppSettings settings) {
    return Card(
      color: Colors.blue.withOpacity(0.05),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Current Configuration',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildStatusItem('Status', settings.running ? 'Running' : 'Paused', 
                settings.running ? Colors.green : Colors.red),
            _buildStatusItem('PPM', '${settings.ppm.toInt()} pixels/meter', Colors.blue),
            _buildStatusItem('Interval', '${settings.rate} seconds', Colors.orange),
            _buildStatusItem('API', settings.api.isEmpty ? 'Not set' : 'Configured', 
                settings.api.isEmpty ? Colors.grey : Colors.green),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusItem(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Text('$label: ', style: const TextStyle(fontWeight: FontWeight.w500)),
          Chip(
            label: Text(value),
            backgroundColor: color.withOpacity(0.1),
            labelStyle: TextStyle(color: color, fontSize: 12),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
          ),
        ],
      ),
    );
  }

  void _resetToDefaults() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Reset Settings?'),
        content: const Text('This will restore all settings to their default values.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Provider.of<SettingsProvider>(context, listen: false).resetToDefaults();
              _apiController.text = 'http://192.168.1.7:5000/upload-image';
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Settings reset to defaults')),
              );
            },
            child: const Text('Reset'),
          ),
        ],
      ),
    );
  }
}