import 'dart:async';
class NoteStore {
  final List<String> notes = [];
  bool failNext = false;
  int attempts = 0;
  Future<void> save(String text) async {
    attempts++;
    await Future<void>.delayed(const Duration(milliseconds: 300));
    if (failNext) { failNext = false; throw StateError('Save failed. Try again.'); }
    if (text.trim().isEmpty) { throw StateError('Enter a note.'); }
    notes.add(text.trim());
  }
}
