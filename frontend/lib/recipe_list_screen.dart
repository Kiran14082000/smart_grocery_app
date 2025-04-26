import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart'; // Import the real url_launcher package

class RecipeListScreen extends StatefulWidget {
  final String itemName;

  const RecipeListScreen({Key? key, required this.itemName}) : super(key: key);

  @override
  _RecipeListScreenState createState() => _RecipeListScreenState();
}

class _RecipeListScreenState extends State<RecipeListScreen> {
  List<dynamic>? recipes;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchRecipeData();
  }

  Future<void> fetchRecipeData() async {
    final String url = 'http://192.168.2.102:5050/recipes/${widget.itemName}'; // <-- your Flask backend IP

    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        setState(() {
          recipes = json.decode(response.body);
          isLoading = false;
        });
      } else {
        throw Exception('Failed to load recipes');
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
        title: Text('Recipes: ${widget.itemName}'),
        backgroundColor: Colors.orange,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : recipes == null
              ? const Center(child: Text('No recipes found.'))
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: recipes!.length,
                  itemBuilder: (context, index) {
                    var recipe = recipes![index];
                    return Card(
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(15),
                      ),
                      elevation: 5,
                      margin: const EdgeInsets.symmetric(vertical: 8),
                      child: ListTile(
                        title: Text(
                          recipe['title'] ?? '',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                        subtitle: const Text('Tap to view full recipe'),
                        trailing: const Icon(Icons.arrow_forward_ios),
                        onTap: () async {
                          final String url = recipe['instructions'] ?? '';
                          if (url.isNotEmpty) {
                            final Uri uri = Uri.parse(url);
                            if (await canLaunchUrl(uri)) {
                              await launchUrl(
                                uri,
                                mode: LaunchMode.externalApplication,
                              );
                            } else {
                              print('❌ Could not launch $url');
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Could not open recipe')),
                              );
                            }
                          }
                        },
                      ),
                    );
                  },
                ),
    );
  }
}
