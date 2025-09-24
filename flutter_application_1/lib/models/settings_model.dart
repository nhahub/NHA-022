class AppSettings {
  final bool running;
  final double ppm;
  final int rate; // Rate in seconds (interval between captures)
  final String api;

  AppSettings({
    required this.running,
    required this.ppm,
    required this.rate,
    required this.api,
  });

  AppSettings copyWith({bool? running, double? ppm, int? rate, String? api}) {
    return AppSettings(
      running: running ?? this.running,
      ppm: ppm ?? this.ppm,
      rate: rate ?? this.rate,
      api: api ?? this.api,
    );
  }

  Map<String, dynamic> toMap() {
    return {'running': running, 'ppm': ppm, 'rate': rate, 'api': api};
  }

  factory AppSettings.fromMap(Map<String, dynamic> map) {
    return AppSettings(
      running: map['running'] ?? true,
      ppm: map['ppm'] ?? 2500,
      rate: map['rate'] ?? 5, // Default: 5 seconds interval
      api: map['api'] ?? '',
    );
  }
}