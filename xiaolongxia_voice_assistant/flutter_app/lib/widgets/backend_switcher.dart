import 'package:flutter/material.dart';
import '../models/backend_mode.dart';

class BackendSwitcher extends StatelessWidget {
  final BackendMode current;
  final Function(BackendMode) onChanged;

  const BackendSwitcher({super.key, required this.current, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return DropdownButton<BackendMode>(
      value: current,
      dropdownColor: const Color(0xFF111827),
      items: BackendMode.values
          .map((mode) => DropdownMenuItem(
                value: mode,
                child: Text(mode.label),
              ))
          .toList(),
      onChanged: (mode) {
        if (mode != null) onChanged(mode);
      },
    );
  }
}
