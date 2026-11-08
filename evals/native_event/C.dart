// Supplementary event-controlled native evidence. Not a replacement for frozen graders.
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:route_notes/main.dart';
import 'package:route_notes/store.dart';

class EventNoteStore extends NoteStore {
  final List<_NoteRequest> requests = [];
  @override
  Future<void> save(String text) {
    attempts++;
    final request = _NoteRequest(text);
    requests.add(request);
    return request.result.future;
  }
  void complete(int index) {
    final request = requests[index];
    if (request.result.isCompleted) throw StateError('Request already completed');
    if (failNext) {
      failNext = false;
      request.result.completeError(StateError('Save failed. Try again.'));
    } else if (request.text.trim().isEmpty) {
      request.result.completeError(StateError('Enter a note.'));
    } else {
      notes.add(request.text.trim());
      request.result.complete();
    }
  }
}
class _NoteRequest {
  _NoteRequest(this.text);
  final String text;
  final Completer<void> result = Completer<void>();
}

void main() {
  testWidgets('event backend: confirmation, duplicate guard, failure draft and retry', (tester) async {
    final store = EventNoteStore();
    await tester.pumpWidget(RouteNotesApp(store: store));
    await tester.tap(find.byKey(const Key('add')));
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('draft')), 'Read the meter');
    await tester.tap(find.byKey(const Key('save')));
    await tester.pump();
    expect(store.attempts, 1);
    expect(store.requests.length, 1);
    expect(store.notes, isEmpty);
    await tester.tap(find.byKey(const Key('save')), warnIfMissed: false);
    await tester.pump();
    expect(store.attempts, 1);
    store.complete(0);
    await tester.pumpAndSettle();
    expect(store.notes, ['Read the meter']);
    expect(find.text('Read the meter'), findsOneWidget);

    await tester.tap(find.byKey(const Key('add')));
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('draft')), 'Keep this draft');
    store.failNext = true;
    await tester.tap(find.byKey(const Key('save')));
    await tester.pump();
    expect(store.attempts, 2);
    expect(store.requests.length, 2);
    store.complete(1);
    await tester.pumpAndSettle();
    expect(store.notes.length, 1);
    expect(find.text('Keep this draft'), findsOneWidget);
    expect(find.textContaining(RegExp('fail', caseSensitive: false), findRichText: true), findsWidgets);
    await tester.tap(find.byKey(const Key('save')));
    await tester.pump();
    expect(store.attempts, 3);
    expect(store.requests.length, 3);
    store.complete(2);
    await tester.pumpAndSettle();
    expect(store.notes, ['Read the meter', 'Keep this draft']);
  });

  testWidgets('event backend: unsent cancel and reduced preference stay usable', (tester) async {
    final store = EventNoteStore();
    tester.binding.platformDispatcher.accessibilityFeaturesTestValue = const FakeAccessibilityFeatures(disableAnimations: true);
    addTearDown(tester.binding.platformDispatcher.clearAccessibilityFeaturesTestValue);
    await tester.pumpWidget(RouteNotesApp(store: store));
    await tester.tap(find.byKey(const Key('add')));
    await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('draft')), 'Cancelled draft');
    await tester.tap(find.byKey(const Key('cancel')));
    await tester.pumpAndSettle();
    expect(store.attempts, 0);
    expect(store.requests, isEmpty);
    expect(store.notes, isEmpty);
    await tester.tap(find.byKey(const Key('add')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('draft')), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
