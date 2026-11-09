# -*- coding: ascii -*-
"""Versioned local progress storage, compatible with Python 2.7 and Python 3.

The last valid save is retained separately. A broken save never silently starts
a new game. This stores explicit gateway state, not inferred avatar snapshots.
"""
import hashlib
import json
import os


class OfflineSaveError(Exception):
    pass


class OfflineSaveVersionError(OfflineSaveError):
    pass


class OfflineSaveStore(object):
    FORMAT = 1
    # Collection + lossless compressed multi-week history can exceed 1MiB.
    # Format1/checksums remain compatible; both read and write stay bounded.
    MAX_BYTES = 16 * 1024 * 1024

    def __init__(self, path, validate):
        self.path = path
        self.validate = validate
        self.revision = 0
        self.recovered = False
        self._last_good = None

    def _encode_payload(self, payload):
        self.validate(payload)
        return json.dumps(payload, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=True, allow_nan=False).encode('ascii')

    @staticmethod
    def _raw_payload_bytes(document):
        """Extract one unambiguous top-level payload, preserving number spelling.

        Python 2's embedded JSON encoder can emit 0.59999999999999998 where
        Python 3 emits 0.6. Both decode to the same double, but re-encoding is
        not a portable checksum input. The writer hashes compact JSON and
        then writes it with whitespace, so remove only whitespace outside
        strings from the exact payload token. json.loads has already checked
        the entire document's syntax; raw_decode locates actual field bounds.
        """
        decoder = json.JSONDecoder()
        length = len(document)
        position = 0

        def skip_space(index):
            while index < length and document[index] in ' \t\r\n':
                index += 1
            return index

        position = skip_space(position)
        if position >= length or document[position] != '{':
            raise OfflineSaveError('Invalid save envelope')
        position += 1
        fields = set()
        payload_token = None
        while True:
            position = skip_space(position)
            if position < length and document[position] == '}':
                position += 1
                break
            key, position = decoder.raw_decode(document, position)
            if key in fields:
                raise OfflineSaveError('Ambiguous save envelope')
            fields.add(key)
            position = skip_space(position)
            if position >= length or document[position] != ':':
                raise OfflineSaveError('Invalid save envelope')
            position = skip_space(position + 1)
            start = position
            _, position = decoder.raw_decode(document, position)
            if key == 'payload':
                payload_token = document[start:position]
            position = skip_space(position)
            if position < length and document[position] == ',':
                position += 1
                continue
            if position < length and document[position] == '}':
                position += 1
                break
            raise OfflineSaveError('Invalid save envelope')
        if skip_space(position) != length or payload_token is None:
            raise OfflineSaveError('Invalid save envelope')

        # Work in slices rather than appending every character of large saves.
        parts = []
        start = 0
        quoted = escaped = False
        for index, character in enumerate(payload_token):
            if quoted:
                if escaped:
                    escaped = False
                elif character == '\\':
                    escaped = True
                elif character == '"':
                    quoted = False
            elif character == '"':
                quoted = True
            elif character in ' \t\r\n':
                if start < index:
                    parts.append(payload_token[start:index])
                start = index + 1
        parts.append(payload_token[start:])
        return ''.join(parts).encode('ascii')

    def _decode(self, raw):
        if len(raw) > self.MAX_BYTES:
            raise OfflineSaveError('Save exceeds the size limit')
        document = raw.decode('ascii')
        envelope = json.loads(document)
        if not isinstance(envelope, dict):
            raise OfflineSaveError('Invalid save envelope')
        if envelope.get('format') != self.FORMAT:
            raise OfflineSaveVersionError('Unsupported save format')
        revision = envelope.get('revision')
        if isinstance(revision, bool) or not isinstance(revision, int) or revision < 1:
            raise OfflineSaveError('Invalid save revision')
        payload = envelope['payload']
        digest = hashlib.sha256(self._encode_payload(payload)).hexdigest()
        if digest != envelope.get('sha256'):
            raw_digest = hashlib.sha256(self._raw_payload_bytes(document)).hexdigest()
            if raw_digest != envelope.get('sha256'):
                raise OfflineSaveError('Save checksum mismatch')
        return revision, payload

    def load(self):
        found = False
        for candidate in (self.path, self.path + '.previous'):
            if not os.path.exists(candidate):
                continue
            found = True
            try:
                with open(candidate, 'rb') as handle:
                    raw = handle.read(self.MAX_BYTES + 1)
                revision, payload = self._decode(raw)
            except OfflineSaveVersionError:
                # A newer version may contain valid progress unknown to this
                # client. Never fall back and overwrite it with an older save.
                raise
            except (ValueError, KeyError, TypeError, OfflineSaveError):
                continue
            self.revision = revision
            self._last_good = raw
            self.recovered = candidate != self.path
            return payload
        if found:
            raise OfflineSaveError('No valid save; existing files were preserved')
        return None

    def _atomic_write(self, destination, raw):
        temporary = destination + '.tmp'
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            with os.fdopen(descriptor, 'wb') as handle:
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
            os.rename(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def write(self, payload):
        encoded = self._encode_payload(payload)
        revision = self.revision + 1
        raw = json.dumps({'format': self.FORMAT, 'revision': revision,
                          'sha256': hashlib.sha256(encoded).hexdigest(),
                          'payload': payload}, sort_keys=True, ensure_ascii=True,
                         allow_nan=False).encode('ascii')
        if len(raw) > self.MAX_BYTES:
            raise OfflineSaveError('Save exceeds the size limit')
        if self._last_good is not None:
            self._atomic_write(self.path + '.previous', self._last_good)
        self._atomic_write(self.path, raw)
        self._last_good, self.revision, self.recovered = raw, revision, False
