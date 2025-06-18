#!/usr/bin/env python3
"""
Direct Weather App Creation using FlutterSwarm with simplified workflow.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flutter_swarm import FlutterSwarm
from utils.project_manager import ProjectManager
from config.config_manager import get_config

async def create_weather_app_direct():
    """Create weather app with direct file generation."""
    # Get configuration
    config = get_config()
    messages = config.get_messages_config()
    examples_config = config.get_examples_config()
    weather_config = examples_config.get('weather_app', {})
    
    welcome_msg = messages.get('welcome', '🌤️  Welcome to FlutterSwarm!')
    print(welcome_msg.replace('Welcome to FlutterSwarm!', 'Direct FlutterSwarm Weather App Creation'))
    
    # Get console width from config
    console_width = config.get_cli_setting('console_width') or 60
    print("=" * console_width)
    
    # Initialize project manager
    pm = ProjectManager()
    project_name = "WeatherMaster"
    
    # Create basic Flutter project structure
    print(f"\n📁 Creating Flutter project structure for {project_name}...")
    try:
        if pm.project_exists(project_name):
            print(f"⚠️  Project {project_name} already exists, cleaning up...")
            import shutil
            shutil.rmtree(pm.get_project_path(project_name))
        
        project_path = pm._create_basic_structure(project_name)
        print(f"✅ Project structure created at: {project_path}")
    except Exception as e:
        print(f"❌ Failed to create project structure: {e}")
        return
    
    # Initialize FlutterSwarm for intelligent code generation
    print(f"\n🐝 Initializing FlutterSwarm agents...")
    swarm = FlutterSwarm()
    
    # Get weather app configuration
    api_base_url = weather_config.get('api_base_url', 'https://api.openweathermap.org/data/2.5')
    default_city = weather_config.get('default_city', 'New York')
    forecast_days = weather_config.get('forecast_days', 5)
    
    # Create project in swarm
    project_id = swarm.create_project(
        name=project_name,
        description="A comprehensive weather application with real-time forecasts, location-based weather, and weather alerts",
        requirements=[
            f"Real-time weather data from {api_base_url}",
            "Location-based weather detection using GPS",
            f"{forecast_days}-day weather forecast display",
            "Weather alerts and notifications",
            "Clean, modern UI with weather-appropriate themes",
            "Offline data caching",
            "Dark/light theme support"
        ],
        features=[
            "weather_api", "location_services", "forecasting", 
            "notifications", "offline_sync", "theming"
        ]
    )
    
    print(f"✅ Project registered with ID: {project_id}")
    
    # Start agents briefly to initialize context
    print(f"\n🚀 Starting agent collaboration...")
    swarm_task = asyncio.create_task(swarm.start())
    await asyncio.sleep(3)  # Give agents time to initialize
    
    try:
        # Generate weather app files directly using the implementation agent
        print(f"\n📝 Generating weather app files...")
        
        # Get the implementation agent to generate core files
        impl_agent = swarm.agents["implementation"]
        
        # Generate main app files
        await generate_weather_app_files(impl_agent, project_path, project_id)
        
        print(f"\n✅ Weather app files generated successfully!")
        print(f"📁 Project location: {project_path}")
        print(f"\n🎯 Next steps:")
        print(f"   1. Navigate to: {project_path}")
        print(f"   2. Run: flutter pub get")
        print(f"   3. Add your OpenWeatherMap API key to lib/config/api_config.dart")
        print(f"   4. Run: flutter run")
        
    except Exception as e:
        print(f"❌ Error generating files: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await swarm.stop()
        print(f"\n🛑 FlutterSwarm stopped")

async def generate_weather_app_files(impl_agent, project_path, project_id):
    """Generate the actual Flutter weather app files."""
    
    # Define the files to generate with their content
    files_to_create = {
        "lib/main.dart": await get_main_dart_content(impl_agent),
        "lib/config/api_config.dart": get_api_config_content(),
        "lib/models/weather.dart": await get_weather_model_content(impl_agent),
        "lib/models/forecast.dart": await get_forecast_model_content(impl_agent),
        "lib/services/weather_service.dart": await get_weather_service_content(impl_agent),
        "lib/services/location_service.dart": await get_location_service_content(impl_agent),
        "lib/providers/weather_provider.dart": await get_weather_provider_content(impl_agent),
        "lib/screens/home_screen.dart": await get_home_screen_content(impl_agent),
        "lib/screens/forecast_screen.dart": await get_forecast_screen_content(impl_agent),
        "lib/widgets/weather_card.dart": await get_weather_card_content(impl_agent),
        "lib/widgets/forecast_item.dart": await get_forecast_item_content(impl_agent),
        "lib/theme/app_theme.dart": await get_app_theme_content(impl_agent),
        "pubspec.yaml": get_pubspec_content(),
    }
    
    # Create all files
    for file_path, content in files_to_create.items():
        full_path = os.path.join(project_path, file_path)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Write file content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created: {file_path}")

async def get_main_dart_content(agent):
    """Get main.dart content using the implementation agent."""
    prompt = """
    Generate a main.dart file for a Flutter weather app that:
    1. Sets up the app with proper theming
    2. Uses Provider for state management
    3. Initializes location services
    4. Sets up navigation to home screen
    5. Includes proper error handling
    
    Make it production-ready with proper imports and structure.
    """
    
    try:
        content = await agent.think(prompt)
        # Extract code from the response if it's wrapped in explanation
        if "```dart" in content:
            start = content.find("```dart") + 7
            end = content.find("```", start)
            if end != -1:
                content = content[start:end].strip()
        return content
    except:
        # Fallback content if agent fails
        return get_fallback_main_dart()

def get_fallback_main_dart():
    """Fallback main.dart content."""
    return '''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'providers/weather_provider.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const WeatherApp());
}

class WeatherApp extends StatelessWidget {
  const WeatherApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (context) => WeatherProvider(),
      child: MaterialApp(
        title: 'Weather Master',
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        home: const HomeScreen(),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}'''

def get_api_config_content():
    """Get API configuration content."""
    # Get configuration
    config = get_config()
    examples_config = config.get_examples_config()
    weather_config = examples_config.get('weather_app', {})
    api_base_url = weather_config.get('api_base_url', 'https://api.openweathermap.org/data/2.5')
    
    return f'''class ApiConfig {{
  // Get your API key from https://openweathermap.org/api
  static const String apiKey = 'YOUR_API_KEY_HERE';
  static const String baseUrl = '{api_base_url}';
  
  static const String currentWeatherEndpoint = '/weather';
  static const String forecastEndpoint = '/forecast';
}}'''

# Add more content generation functions...
async def get_weather_model_content(agent):
    """Get weather model content."""
    return '''class Weather {
  final String cityName;
  final double temperature;
  final String description;
  final String iconCode;
  final double humidity;
  final double windSpeed;
  final double pressure;
  final DateTime timestamp;

  Weather({
    required this.cityName,
    required this.temperature,
    required this.description,
    required this.iconCode,
    required this.humidity,
    required this.windSpeed,
    required this.pressure,
    required this.timestamp,
  });

  factory Weather.fromJson(Map<String, dynamic> json) {
    return Weather(
      cityName: json['name'] ?? '',
      temperature: (json['main']['temp'] ?? 0).toDouble(),
      description: json['weather'][0]['description'] ?? '',
      iconCode: json['weather'][0]['icon'] ?? '',
      humidity: (json['main']['humidity'] ?? 0).toDouble(),
      windSpeed: (json['wind']['speed'] ?? 0).toDouble(),
      pressure: (json['main']['pressure'] ?? 0).toDouble(),
      timestamp: DateTime.now(),
    );
  }
}'''

# Continue with more file content generation functions...
async def get_forecast_model_content(agent):
    return '''class Forecast {
  final DateTime dateTime;
  final double temperature;
  final String description;
  final String iconCode;

  Forecast({
    required this.dateTime,
    required this.temperature,
    required this.description,
    required this.iconCode,
  });

  factory Forecast.fromJson(Map<String, dynamic> json) {
    return Forecast(
      dateTime: DateTime.fromMillisecondsSinceEpoch(json['dt'] * 1000),
      temperature: (json['main']['temp'] ?? 0).toDouble(),
      description: json['weather'][0]['description'] ?? '',
      iconCode: json['weather'][0]['icon'] ?? '',
    );
  }
}'''

async def get_weather_service_content(agent):
    return '''import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';
import '../models/weather.dart';
import '../models/forecast.dart';

class WeatherService {
  Future<Weather> getCurrentWeather(double lat, double lon) async {
    final url = Uri.parse(
      '\\${ApiConfig.baseUrl}\\${ApiConfig.currentWeatherEndpoint}?lat=\\$lat&lon=\\$lon&appid=\\${ApiConfig.apiKey}&units=metric'
    );

    final response = await http.get(url);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return Weather.fromJson(data);
    } else {
      throw Exception('Failed to load weather data');
    }
  }

  Future<List<Forecast>> getForecast(double lat, double lon) async {
    final url = Uri.parse(
      '\\${ApiConfig.baseUrl}\\${ApiConfig.forecastEndpoint}?lat=\\$lat&lon=\\$lon&appid=\\${ApiConfig.apiKey}&units=metric'
    );

    final response = await http.get(url);

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final List<dynamic> forecastData = data['list'];
      return forecastData.map((item) => Forecast.fromJson(item)).toList();
    } else {
      throw Exception('Failed to load forecast data');
    }
  }
}'''

async def get_location_service_content(agent):
    return '''import 'package:geolocator/geolocator.dart';

class LocationService {
  Future<Position> getCurrentLocation() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) {
      throw Exception('Location services are disabled.');
    }

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        throw Exception('Location permissions are denied');
      }
    }

    if (permission == LocationPermission.deniedForever) {
      throw Exception('Location permissions are permanently denied');
    }

    return await Geolocator.getCurrentPosition();
  }
}'''

async def get_weather_provider_content(agent):
    return '''import 'package:flutter/material.dart';
import '../models/weather.dart';
import '../models/forecast.dart';
import '../services/weather_service.dart';
import '../services/location_service.dart';

class WeatherProvider with ChangeNotifier {
  final WeatherService _weatherService = WeatherService();
  final LocationService _locationService = LocationService();

  Weather? _currentWeather;
  List<Forecast>? _forecast;
  bool _isLoading = false;
  String? _error;

  Weather? get currentWeather => _currentWeather;
  List<Forecast>? get forecast => _forecast;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchWeatherData() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final position = await _locationService.getCurrentLocation();
      
      _currentWeather = await _weatherService.getCurrentWeather(
        position.latitude,
        position.longitude,
      );
      
      _forecast = await _weatherService.getForecast(
        position.latitude,
        position.longitude,
      );
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}'''

async def get_home_screen_content(agent):
    return '''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/weather_provider.dart';
import '../widgets/weather_card.dart';
import 'forecast_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<WeatherProvider>().fetchWeatherData();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Weather Master'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<WeatherProvider>().fetchWeatherData();
            },
          ),
        ],
      ),
      body: Consumer<WeatherProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading) {
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (provider.error != null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.error,
                    size: 64,
                    color: Theme.of(context).colorScheme.error,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Error: \\${provider.error}',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      provider.fetchWeatherData();
                    },
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          if (provider.currentWeather == null) {
            return const Center(
              child: Text('No weather data available'),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                WeatherCard(weather: provider.currentWeather!),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const ForecastScreen(),
                      ),
                    );
                  },
                  child: const Text('View 5-Day Forecast'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}'''

async def get_forecast_screen_content(agent):
    return '''import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/weather_provider.dart';
import '../widgets/forecast_item.dart';

class ForecastScreen extends StatelessWidget {
  const ForecastScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('5-Day Forecast'),
      ),
      body: Consumer<WeatherProvider>(
        builder: (context, provider, child) {
          if (provider.forecast == null || provider.forecast!.isEmpty) {
            return const Center(
              child: Text('No forecast data available'),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: provider.forecast!.length,
            itemBuilder: (context, index) {
              final forecast = provider.forecast![index];
              return ForecastItem(forecast: forecast);
            },
          );
        },
      ),
    );
  }
}'''

async def get_weather_card_content(agent):
    return '''import 'package:flutter/material.dart';
import '../models/weather.dart';

class WeatherCard extends StatelessWidget {
  final Weather weather;

  const WeatherCard({super.key, required this.weather});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 8,
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Text(
              weather.cityName,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  _getWeatherIcon(weather.iconCode),
                  size: 64,
                  color: Theme.of(context).primaryColor,
                ),
                const SizedBox(width: 16),
                Text(
                  '\\${weather.temperature.round()}°C',
                  style: Theme.of(context).textTheme.displayLarge,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              weather.description.toUpperCase(),
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildInfoColumn(
                  context,
                  'Humidity',
                  '\\${weather.humidity.round()}%',
                  Icons.water_drop,
                ),
                _buildInfoColumn(
                  context,
                  'Wind',
                  '\\${weather.windSpeed.round()} m/s',
                  Icons.air,
                ),
                _buildInfoColumn(
                  context,
                  'Pressure',
                  '\\${weather.pressure.round()} hPa',
                  Icons.compress,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoColumn(BuildContext context, String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Theme.of(context).primaryColor),
        const SizedBox(height: 4),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
        Text(value, style: Theme.of(context).textTheme.bodyLarge),
      ],
    );
  }

  IconData _getWeatherIcon(String iconCode) {
    switch (iconCode) {
      case '01d':
      case '01n':
        return Icons.wb_sunny;
      case '02d':
      case '02n':
        return Icons.cloud;
      case '03d':
      case '03n':
      case '04d':
      case '04n':
        return Icons.cloud;
      case '09d':
      case '09n':
        return Icons.grain;
      case '10d':
      case '10n':
        return Icons.umbrella;
      case '11d':
      case '11n':
        return Icons.flash_on;
      case '13d':
      case '13n':
        return Icons.ac_unit;
      case '50d':
      case '50n':
        return Icons.foggy;
      default:
        return Icons.wb_cloudy;
    }
  }
}'''

async def get_forecast_item_content(agent):
    return '''import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/forecast.dart';

class ForecastItem extends StatelessWidget {
  final Forecast forecast;

  const ForecastItem({super.key, required this.forecast});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(
          _getWeatherIcon(forecast.iconCode),
          color: Theme.of(context).primaryColor,
        ),
        title: Text(
          DateFormat('EEEE, MMM d - HH:mm').format(forecast.dateTime),
        ),
        subtitle: Text(
          forecast.description,
          style: TextStyle(
            color: Theme.of(context).textTheme.bodySmall?.color,
          ),
        ),
        trailing: Text(
          '\\${forecast.temperature.round()}°C',
          style: Theme.of(context).textTheme.titleLarge,
        ),
      ),
    );
  }

  IconData _getWeatherIcon(String iconCode) {
    switch (iconCode) {
      case '01d':
      case '01n':
        return Icons.wb_sunny;
      case '02d':
      case '02n':
        return Icons.cloud;
      case '03d':
      case '03n':
      case '04d':
      case '04n':
        return Icons.cloud;
      case '09d':
      case '09n':
        return Icons.grain;
      case '10d':
      case '10n':
        return Icons.umbrella;
      case '11d':
      case '11n':
        return Icons.flash_on;
      case '13d':
      case '13n':
        return Icons.ac_unit;
      case '50d':
      case '50n':
        return Icons.foggy;
      default:
        return Icons.wb_cloudy;
    }
  }
}'''

async def get_app_theme_content(agent):
    return '''import 'package:flutter/material.dart';

class AppTheme {
  static ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.light,
    ),
    appBarTheme: const AppBarTheme(
      centerTitle: true,
      elevation: 0,
    ),
    cardTheme: CardTheme(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  );

  static ThemeData get darkTheme => ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(
      seedColor: Colors.blue,
      brightness: Brightness.dark,
    ),
    appBarTheme: const AppBarTheme(
      centerTitle: true,
      elevation: 0,
    ),
    cardTheme: CardTheme(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
    ),
  );
}'''

def get_pubspec_content():
    return '''name: weather_master
description: A comprehensive weather application built with FlutterSwarm.

version: 1.0.0+1

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: ">=3.0.0"

dependencies:
  flutter:
    sdk: flutter
  
  # UI
  cupertino_icons: ^1.0.6
  
  # State Management
  provider: ^6.1.1
  
  # HTTP Requests
  http: ^1.2.0
  
  # Location
  geolocator: ^10.1.0
  
  # Date formatting
  intl: ^0.19.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0

flutter:
  uses-material-design: true
'''

if __name__ == "__main__":
    asyncio.run(create_weather_app_direct())
