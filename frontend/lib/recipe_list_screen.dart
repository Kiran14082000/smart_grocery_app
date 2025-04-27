import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';

class RecipeListScreen extends StatefulWidget {
  final String itemName;

  const RecipeListScreen({Key? key, required this.itemName}) : super(key: key);

  @override
  _RecipeListScreenState createState() => _RecipeListScreenState();
}

class _RecipeListScreenState extends State<RecipeListScreen> {
  List<dynamic>? recipes;
  bool isLoading = true;
  bool noRecipesFound = false;

  @override
  void initState() {
    super.initState();
    fetchRecipeData(widget.itemName);
  }

  Future<void> fetchRecipeData(String itemName) async {
    final String url = 'http://192.168.2.102:5050/recipes/$itemName';

    try {
      final response = await http.get(Uri.parse(url));

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);

        if (data.isEmpty || data.first is Map && data.first.containsKey('error')) {
          // Try fallback
          if (itemName.contains(' ')) {
            String fallback = itemName.split(' ').last;
            await fetchRecipeData(fallback);
          } else {
            setState(() {
              noRecipesFound = true;
              isLoading = false;
            });
          }
        } else {
          setState(() {
            recipes = data;
            isLoading = false;
          });
        }
      } else {
        throw Exception('Failed to load recipes');
      }
    } catch (e) {
      print('❌ Recipe Error: $e');
      setState(() {
        noRecipesFound = true;
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
          : noRecipesFound
              ? const Center(child: Text('❌ No recipes found.\nYou can enjoy it fresh!', textAlign: TextAlign.center,))
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
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('❌ Could not open recipe')),
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
