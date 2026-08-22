// Run a student's Dart under the VM service and print JSON snapshots.
//
// Python has sys.settrace and JavaScript has Node's inspector. Dart has the
// VM service: the same protocol DevTools speaks, reachable over a WebSocket
// that `dart:io` can open without a single package. So the shape here is the
// same as the JavaScript runner — put a breakpoint on every line, and each
// time it stops, read the frame and resume.
//
// Resuming from one breakpoint runs to the next, which is by construction the
// next line of their code that executes, so the SDK's own frames are skipped
// without having to detect them.
//
// Output matches _trace_runner.py exactly, so one set of diagrams draws all
// three languages.

import 'dart:async';
import 'dart:convert';
import 'dart:io';

const sentinel = '<<<CODE_COACH_TRACE>>>';

// Set CODE_COACH_TRACE_TIMING=1 to print milestone timings to stderr.
final _timing = Platform.environment['CODE_COACH_TRACE_TIMING'] == '1';
final _clock = Stopwatch()..start();
void _mark(String what) {
  if (_timing) stderr.writeln('[${_clock.elapsedMilliseconds}ms] $what');
}

// Same ceilings as the other two runners: a readable picture, not a memory
// dump.
const maxSteps = 400;
const maxItems = 60;
const maxFields = 12;
const maxDepth = 8;
const maxString = 120;

late final String targetPath;

Future<void> main(List<String> args) async {
  targetPath = args[0];
  final source = File(targetPath).readAsStringSync();
  final tracer = _Tracer(source);
  await tracer.run();
}

class _Tracer {
  _Tracer(this.source);

  final String source;
  final List<Map<String, dynamic>> steps = [];
  final List<String> output = [];
  final List<String> errors = [];

  bool truncated = false;
  bool emitted = false;
  Map<String, dynamic>? error;

  WebSocket? _socket;
  int _nextId = 0;
  final Map<String, Completer<Map<String, dynamic>>> _pending = {};
  String _isolateId = '';

  Future<void> run() async {
    // The VM itself, not the `run` subcommand: `run` adds a layer we don't
    // need. Pausing on exit as well as on start is what tells us the program
    // has finished — with the service enabled the process stays alive for its
    // client, so waiting for it to exit waits forever.
    final proc = await Process.start('dart', [
      '--enable-vm-service=0',
      '--pause-isolates-on-start',
      '--pause-isolates-on-exit',
      '--disable-service-auth-codes',
      targetPath,
    ]);

    final uri = Completer<String>();
    proc.stdout.transform(utf8.decoder).listen((chunk) {
      for (final line in const LineSplitter().convert(chunk)) {
        // The service banner is ours, not theirs — it must not appear in the
        // program's output.
        if (line.startsWith('The Dart VM service is listening on') ||
            line.startsWith('The Dart DevTools')) {
          final match = RegExp(r'(http://127\.0\.0\.1:\d+/)').firstMatch(line);
          if (match != null && !uri.isCompleted) {
            uri.complete('${match.group(1)!.replaceFirst('http://', 'ws://')}ws');
          }
          continue;
        }
        output.add(line);
      }
    });
    proc.stderr.transform(utf8.decoder).listen(errors.add);

    // If the program never starts a service, there is nothing to trace. A
    // program that doesn't compile is the common case, and it exits rather
    // than hanging — so race the exit, or every typo costs a full timeout
    // and reports it as one.
    _mark('process started');
    final wsUri = await Future.any([
      uri.future,
      proc.exitCode.then((_) async {
        // Give the last of stderr a moment to arrive before reading it.
        await Future.delayed(const Duration(milliseconds: 150));
        return '';
      }),
      Future.delayed(const Duration(seconds: 20), () => ''),
    ]);
    if (wsUri.isEmpty) {
      final detail = errors.join().trim();
      error = {
        // Dart's own compiler message is more use than anything we'd write.
        'type': detail.contains('Error:') ? 'CompileError' : 'Error',
        'message': detail.isEmpty
            ? 'Dart did not start a debugger for this program.'
            : _firstError(detail),
        'line': _lineFromDartError(detail),
      };
      proc.kill();
      _emit();
      return;
    }

    try {
      await _trace(wsUri, proc);
    } catch (e) {
      // The compiler's own message beats ours whenever there is one.
      final detail = errors.join().trim();
      error ??= detail.contains('Error:')
          ? {
              'type': 'CompileError',
              'message': _firstError(detail),
              'line': _lineFromDartError(detail),
            }
          : {'type': 'Error', 'message': '$e', 'line': null};
    }

    proc.kill();
    await _socket?.close();
    _emit();
    // The traced program is paused on exit and its service socket holds the
    // process open, so nothing here ends on its own. The trace itself takes
    // about a second; the rest was spent waiting for something that was never
    // going to close.
    exit(0);
  }

  Future<void> _trace(String wsUri, Process proc) async {
    final socket = await WebSocket.connect(wsUri);
    _socket = socket;

    final finished = Completer<void>();
    socket.listen((raw) {
      final msg = jsonDecode(raw as String) as Map<String, dynamic>;
      if (msg.containsKey('id')) {
        _pending.remove(msg['id'].toString())?.complete(msg);
        return;
      }
      final event = (msg['params'] as Map?)?['event'] as Map<String, dynamic>?;
      if (event == null) return;
      final kind = event['kind'] as String?;
      if (kind == 'PauseBreakpoint') {
        _onPause().catchError((_) {});
      } else if (kind == 'IsolateExit' || kind == 'PauseExit') {
        if (!finished.isCompleted) finished.complete();
      }
    }, onDone: () {
      if (!finished.isCompleted) finished.complete();
      _abandonPending('the program stopped before it could be traced');
    });

    // A program that fails to compile starts the service and then dies. Any
    // request already in flight would otherwise sit until its own timeout and
    // report that instead of the compiler's message.
    unawaited(proc.exitCode.then((_) {
      _abandonPending('the program exited');
    }));

    _mark('websocket connected');
    final vm = await _call('getVM');
    final isolates = (vm['isolates'] as List).cast<Map<String, dynamic>>();
    if (isolates.isEmpty) throw StateError('no isolate to trace');
    _isolateId = isolates.first['id'] as String;

    await _call('streamListen', {'streamId': 'Debug'});
    await _call('streamListen', {'streamId': 'Isolate'});

    // An isolate exists before it can be asked about. Between "paused on
    // start" and "runnable" there is a window where getScripts fails with
    // "Isolate must be runnable" — which showed up as a trace that worked
    // most of the time and returned nothing the rest.
    await _waitUntilRunnable();

    // A breakpoint on every line of the student's file. Lines with nothing
    // executable on them simply fail to resolve, which is fine.
    final scripts = (await _call('getScripts', {'isolateId': _isolateId}))['scripts'] as List;
    final ours = scripts.cast<Map<String, dynamic>>().where((s) {
      final uri = (s['uri'] as String? ?? '').toLowerCase();
      return uri.endsWith(_fileName().toLowerCase());
    }).toList();
    if (ours.isEmpty) throw StateError('the program under trace was not loaded');
    final scriptId = ours.first['id'] as String;

    // All at once rather than one round-trip per line: a hundred-line file
    // would otherwise spend a hundred waits before it started running.
    final lineCount = const LineSplitter().convert(source).length;
    await Future.wait([
      for (var line = 1; line <= lineCount; line++)
        _call('addBreakpoint', {
          'isolateId': _isolateId,
          'scriptId': scriptId,
          'line': line,
          // Nothing executable on that line is not an error worth raising.
        }).catchError((_) => <String, dynamic>{}),
    ]);

    _mark('breakpoints set');
    await _call('resume', {'isolateId': _isolateId});

    // Either the program ends or the process does.
    await Future.any([
      finished.future,
      proc.exitCode.then((_) {}),
      Future.delayed(const Duration(seconds: 15)),
    ]);
    _mark('run finished, ${steps.length} steps');
  }

  /// Wait for the isolate to be ready to answer questions about itself.
  Future<void> _waitUntilRunnable() async {
    // Bounded by the clock rather than by a number of attempts, so a slow
    // reply can't multiply into a much longer wait than intended.
    final deadline = DateTime.now().add(const Duration(seconds: 8));
    while (DateTime.now().isBefore(deadline)) {
      if (_gone) throw StateError('the program stopped before it could run');
      try {
        final isolate = await _call('getIsolate', {'isolateId': _isolateId});
        if (isolate['runnable'] == true) return;
      } catch (_) {
        if (_gone) rethrow;
      }
      await Future.delayed(const Duration(milliseconds: 25));
    }
    throw StateError('the program never became ready to trace');
  }

  bool _gone = false;

  void _abandonPending(String why) {
    _gone = true;
    if (_pending.isEmpty) return;
    final waiting = List.of(_pending.values);
    _pending.clear();
    for (final completer in waiting) {
      if (!completer.isCompleted) {
        completer.completeError(StateError(why));
      }
    }
  }

  String _fileName() => targetPath.split(Platform.pathSeparator).last;

  Future<Map<String, dynamic>> _call(String method,
      [Map<String, dynamic>? params]) async {
    final socket = _socket;
    if (socket == null) throw StateError('not connected');
    // Once the connection is gone it stays gone. Without this, every later
    // call waited out its own ten-second timeout with nothing on the other
    // end — a retry loop then took half an hour instead of failing at once.
    if (_gone) throw StateError('the program is no longer running');
    final id = (++_nextId).toString();
    final completer = Completer<Map<String, dynamic>>();
    _pending[id] = completer;
    socket.add(jsonEncode({
      'jsonrpc': '2.0',
      'id': id,
      'method': method,
      'params': params ?? {},
    }));
    final reply = await completer.future.timeout(const Duration(seconds: 10));
    if (reply.containsKey('error')) {
      throw StateError('${reply['error']}');
    }
    return reply['result'] as Map<String, dynamic>;
  }

  bool _stepping = false;

  Future<void> _onPause() async {
    // Pauses arrive as events; without this two could be handled at once and
    // interleave their reads of the same frame.
    if (_stepping) return;
    _stepping = true;
    try {
      if (steps.length >= maxSteps) {
        // Hand back what we have. Resuming a loop that never ends would spin
        // until the timeout and lose four hundred good steps.
        truncated = true;
        _emit();
        exit(0);
      }
      final stack = await _call('getStack', {'isolateId': _isolateId});
      final frames = (stack['frames'] as List?)?.cast<Map<String, dynamic>>();
      if (frames != null && frames.isNotEmpty) {
        final snap = await _snapshot(frames.first);
        if (snap != null) steps.add(snap);
      }
      await _call('resume', {'isolateId': _isolateId});
    } finally {
      _stepping = false;
    }
  }

  Future<Map<String, dynamic>?> _snapshot(Map<String, dynamic> frame) async {
    final location = frame['location'] as Map<String, dynamic>?;
    if (location == null) return null;
    // The VM reports a token position; the line comes back with the script.
    final line = location['line'] as int? ?? await _lineOf(location);

    final heap = <String, dynamic>{};
    final seen = <String, int>{};
    final vars = <String, dynamic>{};

    for (final raw in (frame['vars'] as List? ?? [])) {
      final entry = raw as Map<String, dynamic>;
      final name = entry['name'] as String? ?? '';
      // `:async_op` and friends are the compiler's, not the student's.
      if (name.isEmpty || name.startsWith(':')) continue;
      if (vars.length >= 40) break;
      vars[name] = await _encode(entry['value'], heap, seen, 0);
    }

    return {
      'line': line,
      'func': (frame['function'] as Map?)?['name'] ?? '<module>',
      'vars': vars,
      'heap': heap,
    };
  }

  Future<int> _lineOf(Map<String, dynamic> location) async {
    return location['line'] as int? ?? 0;
  }

  /// Mirrors _encode in the Python runner: primitives inline, containers into
  /// a heap keyed by reference so shared and cyclic structures terminate.
  Future<Map<String, dynamic>> _encode(
      dynamic value, Map<String, dynamic> heap, Map<String, int> seen, int depth) async {
    if (value == null) return {'k': 'prim', 't': 'none', 'v': null};
    final ref = value as Map<String, dynamic>;
    final kind = ref['kind'] as String?;
    final text = ref['valueAsString'] as String?;

    switch (kind) {
      case 'Null':
        return {'k': 'prim', 't': 'none', 'v': null};
      case 'Bool':
        return {'k': 'prim', 't': 'bool', 'v': text == 'true'};
      case 'Int':
        return {'k': 'prim', 't': 'int', 'v': int.tryParse(text ?? '0') ?? 0};
      case 'Double':
        return {
          'k': 'prim',
          't': 'float',
          'v': double.tryParse(text ?? '0') ?? 0,
        };
      case 'String':
        final s = text ?? '';
        return {
          'k': 'prim',
          't': 'str',
          'v': s.length > maxString ? s.substring(0, maxString) : s,
          'clipped': s.length > maxString ||
              (ref['valueAsStringIsTruncated'] as bool? ?? false),
        };
      case 'Closure':
        return {'k': 'prim', 't': 'str', 'v': 'function'};
    }

    if (depth >= maxDepth) {
      return {'k': 'prim', 't': 'str', 'v': '…', 'clipped': true};
    }

    final id = ref['id'] as String?;
    if (id == null) {
      return {'k': 'prim', 't': 'str', 'v': text ?? kind ?? '?'};
    }
    if (seen.containsKey(id)) return {'k': 'ref', 'id': seen[id]};

    final slot = seen.length + 1;
    seen[id] = slot;
    final entry = <String, dynamic>{};
    heap['$slot'] = entry;

    Map<String, dynamic> full;
    try {
      full = await _call('getObject', {'isolateId': _isolateId, 'objectId': id});
    } catch (_) {
      entry.addAll({'k': 'opaque', 'cls': kind ?? '?', 'v': text ?? ''});
      return {'k': 'ref', 'id': slot};
    }

    final className = ((full['class'] as Map?)?['name'] ??
        (ref['class'] as Map?)?['name'] ??
        kind ??
        'Object') as String;

    if (kind == 'List') {
      final elements = (full['elements'] as List? ?? []).take(maxItems);
      final items = <Map<String, dynamic>>[];
      for (final element in elements) {
        items.add(await _encode(element, heap, seen, depth + 1));
      }
      entry.addAll({
        'k': 'list',
        'tuple': false,
        'n': full['length'] ?? items.length,
        'items': items,
      });
    } else if (kind == 'Map') {
      final pairs = <List<Map<String, dynamic>>>[];
      for (final assoc in (full['associations'] as List? ?? []).take(maxItems)) {
        final a = assoc as Map<String, dynamic>;
        pairs.add([
          await _encode(a['key'], heap, seen, depth + 1),
          await _encode(a['value'], heap, seen, depth + 1),
        ]);
      }
      entry.addAll({'k': 'dict', 'n': full['length'] ?? pairs.length, 'pairs': pairs});
    } else if (kind == 'Set') {
      final items = <Map<String, dynamic>>[];
      for (final element in (full['elements'] as List? ?? []).take(maxItems)) {
        items.add(await _encode(element, heap, seen, depth + 1));
      }
      entry.addAll({'k': 'set', 'n': full['length'] ?? items.length, 'items': items});
    } else {
      final fields = <String, dynamic>{};
      for (final raw in (full['fields'] as List? ?? []).take(maxFields)) {
        final field = raw as Map<String, dynamic>;
        final name = (field['decl'] as Map?)?['name'] as String? ??
            field['name'] as String? ??
            '?';
        fields[name] = await _encode(field['value'], heap, seen, depth + 1);
      }
      entry.addAll({'k': 'obj', 'cls': className, 'fields': fields});
    }
    return {'k': 'ref', 'id': slot};
  }

  /// The first compiler complaint, without the file path or the caret art.
  String _firstError(String text) {
    for (final line in const LineSplitter().convert(text)) {
      final match = RegExp(r'Error:\s*(.+)$').firstMatch(line);
      if (match != null) return match.group(1)!.trim();
    }
    return const LineSplitter().convert(text).first;
  }

  int? _lineFromDartError(String text) {
    final match = RegExp('${RegExp.escape(_fileName())}:(\\d+)').firstMatch(text);
    return match == null ? null : int.tryParse(match.group(1)!);
  }

  void _emit() {
    if (emitted) return;
    emitted = true;
    stdout.write(sentinel +
        jsonEncode({
          'steps': steps,
          'truncated': truncated,
          'stdout': output.join('\n'),
          'stderr': errors.join(),
          'error': error,
          'source': source,
        }));
  }
}
