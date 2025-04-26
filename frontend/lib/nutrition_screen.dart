import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class NutritionScreen extends StatefulWidget {
  final String itemName;

  const NutritionScreen({Key? key, required this.itemName}) : super(key: key);

  @override
  _NutritionScreenState createState() => _NutritionScreenState();
}

class _NutritionScreenState extends State<NutritionScreen> {
  Map<String, dynamic>? nutritionData;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchNutritionData();
  }

  Future<void> fetchNutritionData() async {
    final String url = 'http://192.168.2.102:5050/nutrition/${widget.itemName}'; // <-- your Flask server IP

    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        setState(() {
          nutritionData = json.decode(response.body);
          isLoading = false;
        });
      } else {
        throw Exception('Failed to load nutrition data');
      }
    } catch (e) {
      print('❌ Error: $e');
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Nutrition: ${widget.itemName}'),
        backgroundColor: Colors.green,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : nutritionData == null
              ? const Center(child: Text('No data available.'))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: nutritionData!.length,
                  itemBuilder: (context, index) {
                    String key = nutritionData!.keys.elementAt(index);
                    return Card(
                      child: ListTile(
                        title: Text(key),
                        trailing: Text(nutritionData![key].toString()),
                      ),
                    );
                  },
                ),
    );
  }
}
