import 'package:flutter/material.dart';
import 'sync_store.dart';
void main() => runApp(FieldSyncApp(store: SyncStore()));
class FieldSyncApp extends StatelessWidget {
  const FieldSyncApp({super.key, required this.store});
  final SyncStore store;
  @override Widget build(BuildContext context) => MaterialApp(theme: ThemeData(colorSchemeSeed: const Color(0xff245a41)), home: SyncPage(store: store));
}
class SyncPage extends StatefulWidget {
  const SyncPage({super.key, required this.store});
  final SyncStore store;
  @override State<SyncPage> createState()=>_SyncPageState();
}
class _SyncPageState extends State<SyncPage> {
  bool pending=false;
  String status='Ready';
  final draft=TextEditingController(text:'Check cabinet 4');
  Future<void> start() async { if(pending)return;setState(() {pending=true;status='Syncing';});final result=await widget.store.sync();if(!mounted)return;setState(() {pending=false;status=result;}); }
  @override void dispose(){widget.store.cancel();draft.dispose();super.dispose();}
  @override Widget build(BuildContext context)=>Scaffold(appBar:AppBar(title:const Text('Field sync')),body:ListView(children:[const Text('Local demonstration. Synthetic records. Nothing is sent.'),TextField(key:const Key('draft'),controller:draft,decoration:const InputDecoration(labelText:'Field note')),SwitchListTile(key:const Key('online'),title:const Text('Online'),value:widget.store.online,onChanged:(value)=>setState(()=>widget.store.online=value)),SwitchListTile(key:const Key('permission'),title:const Text('Permission granted'),value:widget.store.permitted,onChanged:(value)=>setState(()=>widget.store.permitted=value)),ElevatedButton(key:const Key('sync'),onPressed:pending?null:start,child:const Text('Sync note')),Text(status,key:const Key('status')),if(pending) TextButton(key:const Key('cancel'),onPressed:(){widget.store.cancel();setState(() {pending=false;status='Cancelled';});},child:const Text('Cancel sync'))]));
}
