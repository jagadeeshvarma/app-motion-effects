// Supplementary event-controlled native evidence. Not a replacement for frozen graders.
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:field_sync/main.dart';
import 'package:field_sync/sync_store.dart';

class EventSyncStore extends SyncStore {
  final List<_SyncRequest> requests = [];
  int _eventGeneration = 0;
  @override
  void cancel() { _eventGeneration++; }
  @override
  Future<String> sync() {
    attempts++;
    final request = _SyncRequest(++_eventGeneration);
    requests.add(request);
    return request.result.future;
  }
  void complete(int index) {
    final request = requests[index];
    if (request.result.isCompleted) throw StateError('Request already completed');
    if (request.generation != _eventGeneration) {
      request.result.complete('Cancelled');
    } else if (!permitted) {
      request.result.complete('Permission required');
    } else if (!online) {
      request.result.complete('Offline. Try again when connected.');
    } else {
      completed++;
      request.result.complete('Synced');
    }
  }
}
class _SyncRequest {
  _SyncRequest(this.generation);
  final int generation;
  final Completer<String> result = Completer<String>();
}

void main() {
  testWidgets('event backend: offline, permission and retry preserve note', (tester) async {
    final store = EventSyncStore();
    await tester.pumpWidget(FieldSyncApp(store: store));
    await tester.enterText(find.byKey(const Key('draft')), 'Preserved note');
    store.online = false;
    await tester.tap(find.byKey(const Key('sync')));
    await tester.pump();
    expect(store.requests.length, 1);
    expect(store.completed, 0);
    store.complete(0);
    await tester.pumpAndSettle();
    expect(find.textContaining('Offline'), findsWidgets);
    expect(store.completed, 0);
    store.online = true;
    store.permitted = false;
    await tester.tap(find.byKey(const Key('sync')));
    await tester.pump();
    expect(store.requests.length, 2);
    store.complete(1);
    await tester.pumpAndSettle();
    expect(find.textContaining('Permission'), findsWidgets);
    expect(store.completed, 0);
    store.permitted = true;
    await tester.tap(find.byKey(const Key('sync')));
    await tester.pump();
    expect(store.requests.length, 3);
    expect(store.completed, 0);
    store.complete(2);
    await tester.pumpAndSettle();
    expect(store.completed, 1);
    expect(find.text('Preserved note'), findsOneWidget);
    expect(find.text('Synced'), findsOneWidget);
  });

  testWidgets('event backend: cancelled completion cannot unlock a newer request', (tester) async {
    final store = EventSyncStore();
    await tester.pumpWidget(FieldSyncApp(store: store));
    await tester.tap(find.byKey(const Key('sync')));
    await tester.pump();
    expect(store.requests.length, 1);
    await tester.tap(find.byKey(const Key('cancel')));
    await tester.pump();
    await tester.tap(find.byKey(const Key('sync')));
    await tester.pump();
    expect(store.requests.length, 2);
    expect(store.completed, 0);
    // Resolve the older cancelled request while the newer one stays unresolved.
    store.complete(0);
    await tester.pump();
    expect(store.completed, 0);
    expect(find.byKey(const Key('cancel')), findsOneWidget);
    await tester.tap(find.byKey(const Key('sync')), warnIfMissed: false);
    await tester.pump();
    expect(store.attempts, 2);
    expect(store.requests.length, 2);
    store.complete(1);
    await tester.pumpAndSettle();
    expect(store.completed, 1);
    expect(find.text('Synced'), findsOneWidget);
  });

  testWidgets('event backend: disposal cancels pending work with reduced preference', (tester) async {
    final store = EventSyncStore();
    tester.binding.platformDispatcher.accessibilityFeaturesTestValue = const FakeAccessibilityFeatures(disableAnimations: true);
    addTearDown(tester.binding.platformDispatcher.clearAccessibilityFeaturesTestValue);
    await tester.pumpWidget(FieldSyncApp(store: store));
    await tester.tap(find.byKey(const Key('sync')));
    await tester.pump();
    expect(store.requests.length, 1);
    await tester.pumpWidget(const SizedBox());
    store.complete(0);
    await tester.pumpAndSettle();
    expect(store.completed, 0);
    expect(tester.takeException(), isNull);
  });
}
