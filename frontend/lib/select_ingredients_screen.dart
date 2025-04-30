import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class SelectIngredientsScreen extends StatefulWidget {
  final List<String> ingredients;

  const SelectIngredientsScreen({Key? key, required this.ingredients}) : super(key: key);

  @override
  _SelectIngredientsScreenState createState() => _SelectIngredientsScreenState();
}

class _SelectIngredientsScreenState extends State<SelectIngredientsScreen> {
  final List<String> _selectedIngredients = [];
  bool _isLoading = false;
  Map<String, dynamic>? _recipe;

  void _toggleIngredient(String ingredient) {
    setState(() {
      if (_selectedIngredients.contains(ingredient)) {
        _selectedIngredients.remove(ingredient);
      } else {
        _selectedIngredients.add(ingredient);
      }
    });
  }

  Future<void> _generateRecipe() async {
    if (_selectedIngredients.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Select at least one ingredient')),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final url = Uri.parse('http://192.168.2.102:5050/generate_recipe'); // Your Flask IP
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'ingredients': _selectedIngredients}),
    );

    if (response.statusCode == 200) {
      setState(() {
        _recipe = json.decode(response.body);
        _isLoading = false;
      });
    } else {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to generate recipe')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Select Ingredients'),
        backgroundColor: Colors.green,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _recipe != null
              ? _buildRecipeView()
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    ...widget.ingredients.map((ingredient) => CheckboxListTile(
                          title: Text(ingredient),
                          value: _selectedIngredients.contains(ingredient),
                          onChanged: (selected) => _toggleIngredient(ingredient),
                        )),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _generateRecipe,
                      child: const Text('Generate Recipe'),
                    ),
                  ],
                ),
    );
  }

  Widget _buildRecipeView() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            _recipe!['title'] ?? 'Recipe',
            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          _recipe!['image'] != null
              ? Image.network(_recipe!['image'])
              : const SizedBox(),
          const SizedBox(height: 20),
          Text(
            'Used Ingredients:',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          ...(List<String>.from(_recipe!['usedIngredients'])).map((item) => Text("- $item")),
          const SizedBox(height: 20),
          Text(
            'Missing Ingredients:',
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          ...(List<String>.from(_recipe!['missedIngredients'])).map((item) => Text("- $item")),
        ],
      ),
    );
  }
}
