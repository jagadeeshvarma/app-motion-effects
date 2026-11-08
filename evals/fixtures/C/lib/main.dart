import 'package:flutter/material.dart';
import 'store.dart';
void main() => runApp(RouteNotesApp(store: NoteStore()));
class RouteNotesApp extends StatelessWidget {
  const RouteNotesApp({super.key, required this.store});
  final NoteStore store;
  @override Widget build(BuildContext context) => MaterialApp(theme: ThemeData(colorSchemeSeed: const Color(0xff245a41)), home: NotesPage(store: store));
}
class NotesPage extends StatelessWidget {
  const NotesPage({super.key, required this.store});
  final NoteStore store;
  @override Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('Route notes')), body: ListView(children: [const Text('Local demonstration. Synthetic records. Nothing is sent.'), for(final note in store.notes) Text(note), const Text('Note creation is not implemented yet.') ]));
}
