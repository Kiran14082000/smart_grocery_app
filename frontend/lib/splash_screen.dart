import 'package:flutter/material.dart';
import 'dart:async';
import 'main.dart'; // Import your main file

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _navigateToHome();
  }

  Future<void> _navigateToHome() async {
    // Simulate model loading (you can replace this with real model load check later)
    await Future.delayed(const Duration(seconds: 3)); // wait for 3 seconds
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const HomeScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white, // or any nice color
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
        
            const SizedBox(height: 20),
            const CircularProgressIndicator(
              color: Colors.deepPurple,
              strokeWidth: 3,
            ),
            const SizedBox(height: 20),
            const Text(
              'Loading Smart Grocery...',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
