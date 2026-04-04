import 'package:flutter/material.dart';

Future<String?> showApiKeyDialog(BuildContext context, String title) async {
  final controller = TextEditingController();

  return showDialog<String>(
    context: context,
    builder: (context) {
      return AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: '输入 API Key'),
          obscureText: true,
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('取消')),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, controller.text),
            child: const Text('保存'),
          ),
        ],
      );
    },
  );
}
