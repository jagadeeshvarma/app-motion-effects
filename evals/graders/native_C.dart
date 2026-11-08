import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:route_notes/main.dart';
import 'package:route_notes/store.dart';
void main() {
  testWidgets('confirmed note, retained failure draft, retry, duplicate guard', (tester) async {
    final store=NoteStore();
    await tester.pumpWidget(RouteNotesApp(store:store));
    await tester.tap(find.byKey(const Key('add')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('draft')),'Read the meter');
    await tester.tap(find.byKey(const Key('save')));await tester.pump(const Duration(milliseconds:40));
    expect(store.notes,isEmpty);expect(store.attempts,1);
    await tester.tap(find.byKey(const Key('save')), warnIfMissed:false);
    await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(store.attempts,1);expect(store.notes,['Read the meter']);expect(find.text('Read the meter'),findsOneWidget);
    store.failNext=true;await tester.tap(find.byKey(const Key('add')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('draft')),'Keep this draft');await tester.tap(find.byKey(const Key('save')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();
    expect(find.text('Keep this draft'),findsOneWidget);expect(find.textContaining('fail',findRichText:true),findsWidgets);expect(store.notes.length,1);
    await tester.tap(find.byKey(const Key('save')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(store.notes.length,2);
  });
  testWidgets('cancel and reduced motion remain usable', (tester) async {
    final store=NoteStore();
    tester.binding.platformDispatcher.accessibilityFeaturesTestValue=const FakeAccessibilityFeatures(disableAnimations:true);
    addTearDown(tester.binding.platformDispatcher.clearAccessibilityFeaturesTestValue);
    await tester.pumpWidget(RouteNotesApp(store:store));
    await tester.tap(find.byKey(const Key('add')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();
    await tester.enterText(find.byKey(const Key('draft')),'Cancelled draft');
    await tester.tap(find.byKey(const Key('cancel')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(store.notes,isEmpty);
    await tester.tap(find.byKey(const Key('add')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(find.byKey(const Key('draft')),findsOneWidget);
    expect(tester.takeException(),isNull);
  });
}
