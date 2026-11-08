import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:field_sync/main.dart';
import 'package:field_sync/sync_store.dart';
void main() {
  testWidgets('offline, permission, retry preserve editable note', (tester) async {
    final store=SyncStore();await tester.pumpWidget(FieldSyncApp(store:store));
    await tester.enterText(find.byKey(const Key('draft')),'Preserved note');
    store.online=false;await tester.tap(find.byKey(const Key('sync')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(find.textContaining('Offline'),findsWidgets);expect(store.completed,0);
    store.online=true;store.permitted=false;await tester.tap(find.byKey(const Key('sync')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(find.textContaining('Permission'),findsWidgets);expect(store.completed,0);
    store.permitted=true;await tester.tap(find.byKey(const Key('sync')));await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(store.completed,1);expect(find.text('Preserved note'),findsOneWidget);expect(find.text('Synced'),findsOneWidget);
  });
  testWidgets('cancelled completion cannot replace the retried pending state', (tester) async {
    final store=SyncStore();await tester.pumpWidget(FieldSyncApp(store:store));
    await tester.tap(find.byKey(const Key('sync')));await tester.pump(const Duration(milliseconds:100));
    await tester.tap(find.byKey(const Key('cancel')));await tester.pump();
    await tester.tap(find.byKey(const Key('sync')));await tester.pump(const Duration(milliseconds:310));
    expect(find.text('Syncing'),findsWidgets);expect(store.completed,0);
    await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(store.completed,1);expect(find.text('Synced'),findsOneWidget);
  });
  testWidgets('interrupted widget and reduced preference do not throw', (tester) async {
    final store=SyncStore();tester.binding.platformDispatcher.accessibilityFeaturesTestValue=const FakeAccessibilityFeatures(disableAnimations:true);
    addTearDown(tester.binding.platformDispatcher.clearAccessibilityFeaturesTestValue);
    await tester.pumpWidget(FieldSyncApp(store:store));
    await tester.tap(find.byKey(const Key('sync')));await tester.pump(const Duration(milliseconds:60));await tester.pumpWidget(const SizedBox());await tester.pump(const Duration(milliseconds:500));await tester.pumpAndSettle();expect(store.completed,0);expect(tester.takeException(),isNull);
  });
}
