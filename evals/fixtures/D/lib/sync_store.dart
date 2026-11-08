import 'dart:async';
class SyncStore {
  bool online = true;
  bool permitted = true;
  int attempts = 0;
  int completed = 0;
  int _generation = 0;
  void cancel() { _generation++; }
  Future<String> sync() async {
    final generation = ++_generation;
    attempts++;
    await Future<void>.delayed(const Duration(milliseconds: 400));
    if (generation != _generation) { return 'Cancelled'; }
    if (!permitted) { return 'Permission required'; }
    if (!online) { return 'Offline. Try again when connected.'; }
    completed++;
    return 'Synced';
  }
}
