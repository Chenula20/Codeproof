import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:codeproof_desktop/services/workspace_service.dart';

const token = 'synthetic-local-pairing-token-1234567890123456789';
void main() {
  test('Invalid token and port fail before networking', () async {
    for (final item in [
      LocalWorkspaceService(token: 'short'),
      LocalWorkspaceService(token: token, port: 0),
      LocalWorkspaceService(token: token, port: 65536),
    ]) {
      await expectLater(item.open(''), throwsA(isA<WorkspaceException>()));
      item.dispose();
    }
  });
  test('Wrong token gets actionable error even for non-JSON 401', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    final subscription = server.listen((r) {
      expect(r.headers.value(HttpHeaders.authorizationHeader), 'Bearer $token');
      r.response.statusCode = 401;
      r.response.write('not JSON');
      r.response.close();
    });
    final service = LocalWorkspaceService(token: token, port: server.port);
    try {
      await expectLater(
        service.open(''),
        throwsA(
          isA<WorkspaceException>().having(
            (e) => e.message,
            'message',
            contains('successfully running CodeProof'),
          ),
        ),
      );
    } finally {
      service.dispose();
      await subscription.cancel();
      await server.close(force: true);
    }
  });
  test('Unavailable backend is reported without private token', () async {
    final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
    final port = server.port;
    await server.close(force: true);
    final service = LocalWorkspaceService(token: token, port: port);
    try {
      await expectLater(
        service.open(''),
        throwsA(
          isA<WorkspaceException>()
              .having((e) => e.message, 'message', contains('Cannot reach'))
              .having((e) => e.message, 'secret', isNot(contains(token))),
        ),
      );
    } finally {
      service.dispose();
    }
  });
  test(
    'Redirects are refused and wrong service payload is unreadable',
    () async {
      final server = await HttpServer.bind(InternetAddress.loopbackIPv4, 0);
      final subscription = server.listen((r) {
        r.response.statusCode = 302;
        r.response.headers.set(
          HttpHeaders.locationHeader,
          'http://example.invalid/',
        );
        r.response.write('[]');
        r.response.close();
      });
      final service = LocalWorkspaceService(token: token, port: server.port);
      try {
        await expectLater(
          service.open(''),
          throwsA(
            isA<WorkspaceException>().having(
              (e) => e.message,
              'message',
              contains('unreadable'),
            ),
          ),
        );
      } finally {
        service.dispose();
        await subscription.cancel();
        await server.close(force: true);
      }
    },
  );
}
