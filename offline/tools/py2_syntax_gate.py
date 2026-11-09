"""Reject Python 3-only syntax in sources embedded into the NeoX 2.7 loader.

The startup overlay runs its embedded `project7_*.py` sources through the
game's own Python 2.7 `compile()`.  A source that parses under the host's
Python 3 but not under 2.7 stops the whole overlay at import time, which looks
like a dead panel rather than a build failure.  `offline/current/runtime/
project7_inventory_editor_ui.py` shipped `_text(cc, pool, u'1/1', *xy, A, B)`
that way: legal in Python 3 (PEP 448) and a hard `SyntaxError: only named
arguments may follow *expression` on device.

No 2.7 interpreter is available here and `lib2to3`'s grammar accepts most of
these constructs, so the check is a Python 3 AST walk plus a tokenize pass over
the constructs 2.7 rejects.  It fails closed on anything it cannot parse.
"""
import ast
import io
import tokenize

# Literals 2.7's parser rejects (`1_000`, `0b102`, `1j` is fine, `1_0` is not).
_UNDERSCORE_DIGITS = 'numeric literals with digit separators are Python 3.6+'


class Py2SyntaxError(Exception):
    """A source cannot be compiled by the embedded Python 2.7 runtime."""


def _node_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return type(node).__name__


def _check_call(node, problems):
    """2.7 allows only `name=value` after `*expr`, and nothing after `**expr`."""
    star = None
    for index, argument in enumerate(node.args):
        if isinstance(argument, ast.Starred):
            if star is not None:
                problems.append((node.lineno,
                                 'multiple *unpacking in a call is Python 3.5+'))
                return
            star = index
    if star is not None and star != len(node.args) - 1:
        problems.append((node.lineno,
                         'positional argument after *unpacking '
                         '(Python 2: only named arguments may follow *expression)'))
    double_star = None
    for index, keyword in enumerate(node.keywords):
        if keyword.arg is None:
            if double_star is not None:
                problems.append((node.lineno,
                                 'multiple **unpacking in a call is Python 3.5+'))
                return
            double_star = index
    if double_star is not None and double_star != len(node.keywords) - 1:
        problems.append((node.lineno,
                         'arguments after **unpacking are Python 3.5+'))


def _check_sequence_display(node, problems):
    """`[*a]` / `f(*a)` in a tuple, list or set display is Python 3.5+."""
    for value in node.elts:
        if isinstance(value, ast.Starred):
            problems.append((node.lineno,
                             '%s unpacking is Python 3.5+'
                             % type(node).__name__))
            return


def _check_dict_display(node, problems):
    """`{**a}` is Python 3.5+; its unpacked key is a `None` placeholder."""
    for key in node.keys:
        if key is None:
            problems.append((node.lineno, 'dict **unpacking is Python 3.5+'))
            return


def _check_function(node, problems):
    arguments = node.args
    if arguments.kwonlyargs:
        problems.append((node.lineno,
                         'keyword-only parameters are Python 3'))
    if arguments.vararg is not None and arguments.vararg.annotation is not None:
        problems.append((node.lineno, 'annotations are Python 3'))
    if arguments.kwarg is not None and arguments.kwarg.annotation is not None:
        problems.append((node.lineno, 'annotations are Python 3'))
    for argument in list(arguments.posonlyargs) + list(arguments.args):
        if argument.annotation is not None:
            problems.append((node.lineno, 'annotations are Python 3'))
            break
    if getattr(node, 'returns', None) is not None:
        problems.append((node.lineno, 'return annotations are Python 3'))


def _check_class(node, problems):
    if node.keywords:
        problems.append((node.lineno,
                         'class keyword arguments (e.g. metaclass=) are Python 3'))


def _scan_tokens(text, problems):
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for token in tokens:
            if token.type == tokenize.NUMBER and '_' in token.string:
                problems.append((token.start[0], _UNDERSCORE_DIGITS))
    except (tokenize.TokenError, IndentationError):
        # The AST parse already succeeded, so this is a tokenizer quirk in an
        # already parsed file; nothing more to learn from the token stream.
        return


def find_py2_violations(text, filename='<source>'):
    """Return `[(lineno, reason)]` for constructs the 2.7 loader cannot compile."""
    try:
        tree = ast.parse(text, filename=filename)
    except SyntaxError as error:
        return [(error.lineno or 0, 'Python 3 cannot parse this source: %s'
                 % (error.msg,))]
    problems = []
    _scan_tokens(text, problems)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            _check_call(node, problems)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _check_function(node, problems)
            if isinstance(node, ast.AsyncFunctionDef):
                problems.append((node.lineno, 'async def is Python 3.5+'))
        elif isinstance(node, ast.ClassDef):
            _check_class(node, problems)
        elif isinstance(node, ast.JoinedStr):
            problems.append((node.lineno, 'f-strings are Python 3.6+'))
        elif isinstance(node, ast.NamedExpr):
            problems.append((node.lineno, 'assignment expressions are Python 3.8+'))
        elif isinstance(node, ast.AnnAssign):
            problems.append((node.lineno, 'variable annotations are Python 3.6+'))
        elif isinstance(node, ast.YieldFrom):
            problems.append((node.lineno, 'yield from is Python 3.3+'))
        elif isinstance(node, ast.Await):
            problems.append((node.lineno, 'await is Python 3.5+'))
        elif isinstance(node, (ast.AsyncFor, ast.AsyncWith)):
            problems.append((node.lineno,
                             'async for/with is Python 3.5+'))
        elif isinstance(node, ast.MatMult):
            problems.append((getattr(node, 'lineno', 0),
                             '@ operator is Python 3.5+'))
        elif isinstance(node, ast.Nonlocal):
            problems.append((node.lineno, 'nonlocal is Python 3'))
        elif isinstance(node, ast.Raise):
            if getattr(node, 'cause', None) is not None:
                problems.append((node.lineno, 'raise ... from ... is Python 3'))
        elif isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            _check_sequence_display(node, problems)
        elif isinstance(node, ast.Dict):
            _check_dict_display(node, problems)
    problems.sort()
    return problems


def decode_source(raw, name='<source>'):
    """Embedded sources are read with `.decode('ascii')`; enforce that here.

    A non-ASCII comment or identifier raises at load, before any of the
    overlay runs, which is indistinguishable from a missing panel on device.
    """
    try:
        return raw.decode('ascii')
    except UnicodeDecodeError as error:
        line = raw.count(b'\n', 0, error.start) + 1
        raise Py2SyntaxError(
            '%s line %d: non-ASCII byte 0x%02x; embedded sources must be ASCII '
            '(write strings as u\'\\uXXXX\' escapes)'
            % (name, line, raw[error.start]))


def check_source_file(path):
    """Raise `Py2SyntaxError` when `path` cannot run on the 2.7 loader."""
    text = decode_source(path.read_bytes(), str(path))
    problems = find_py2_violations(text, path.name)
    if problems:
        detail = '; '.join('line %d: %s' % item for item in problems[:8])
        raise Py2SyntaxError('%s is not valid Python 2.7: %s' % (path, detail))


def check_sources(sources):
    """Check a `{name: bytes-or-text}` mapping; name every offending source."""
    failures = []
    for name in sorted(sources):
        value = sources[name]
        raw = value.encode('utf-8') if isinstance(value, str) else value
        try:
            text = decode_source(raw, name)
        except Py2SyntaxError as error:
            failures.append(str(error))
            continue
        problems = find_py2_violations(text, name)
        if problems:
            failures.append('%s: %s' % (
                name, '; '.join('line %d: %s' % item for item in problems[:8])))
    if failures:
        raise Py2SyntaxError('Embedded sources are not valid Python 2.7: '
                             + ' | '.join(failures))
