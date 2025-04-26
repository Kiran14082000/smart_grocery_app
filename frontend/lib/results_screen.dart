import 'package:flutter/material.dart';
import 'nutrition_screen.dart';
import 'recipe_list_screen.dart';

class ResultsScreen extends StatefulWidget {
  final List<String> detectedItems;
  final String source;

  const ResultsScreen({
    Key? key,
    required this.detectedItems,
    this.source = 'Google Vision',
  }) : super(key: key);

  @override
  State<ResultsScreen> createState() => _ResultsScreenState();
}

class _ResultsScreenState extends State<ResultsScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    )..forward(); // Start animation
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _showOptions(BuildContext context, String itemName) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.food_bank),
              title: const Text('Get Nutritional Facts'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => NutritionScreen(itemName: itemName),
                  ),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.restaurant_menu),
              title: const Text('Get Recipes'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => RecipeListScreen(itemName: itemName),
                  ),
                );
              },
            ),
          ],
        );
      },
    );
  }

  Widget _buildAnimatedItem(String item, int index) {
    final Animation<double> animation = CurvedAnimation(
      parent: _controller,
      curve: Interval(
        (index / widget.detectedItems.length),
        1.0,
        curve: Curves.easeOut,
      ),
    );

    return FadeTransition(
      opacity: animation,
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.2),
          end: Offset.zero,
        ).animate(animation),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: Material(
            elevation: 4,
            borderRadius: BorderRadius.circular(16),
            child: ListTile(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              tileColor: Colors.white,
              leading: const Icon(Icons.check_circle_rounded,
                  color: Colors.green, size: 28),
              title: Text(
                item,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              subtitle: Text(
                'Detected via ${widget.source}',
                style: const TextStyle(fontSize: 14, color: Colors.grey),
              ),
              trailing: const Icon(Icons.arrow_forward_ios,
                  size: 18, color: Colors.grey),
              onTap: () {
                _showOptions(context, item);
              },
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final items = widget.detectedItems;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Detected Items'),
        centerTitle: true,
        backgroundColor: Colors.red,
      ),
      backgroundColor: const Color(0xFFF6F4FA),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: items.length,
        itemBuilder: (context, index) {
          return _buildAnimatedItem(items[index], index);
        },
      ),
    );
  }
}
