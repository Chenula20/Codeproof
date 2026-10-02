import ast
import re
from pathlib import Path
from typing import List, Pattern, Set


class SecretFilter:
    """Filters out files and content that may contain secrets."""

    # File patterns that commonly contain secrets
    SECRET_FILE_PATTERNS = [
        r"\.env(\..*)?$",
        r"\.env\.",
        r"credentials?\.",
        r"service-account",
        r"secret",
        r"private[_-]?key",
        r"\.pem$",
        r"\.key$",
        r"\.p12$",
        r"\.pfx$",
        r"\.cer$",
        r"\.crt$",
        r"id_rsa",
        r"id_ed25519",
        r"known_hosts",
        r"authorized_keys",
        r"\.kube/config",
        r"\.aws/credentials",
        r"\.docker/config\.json",
        r"\.npmrc",
        r"\.pypirc",
        r"\.gemrc",
        r"secrets?\.ya?ml",
        r"vault",
    ]

    # Content patterns that may indicate secrets
    SECRET_CONTENT_PATTERNS = [
        # API keys
        # AWS
        (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key"),
        # Generic secrets
        # Private keys
        (re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"), "Private key"),
        # Database URLs
        (re.compile(r"(postgres|mysql|mongodb|redis)://[^:\s]+:[^@\s]+@"), "Database URL with credentials"),
    ]

    # Explicit signing-secret names; lexical filtering, not whole-program analysis.
    SIGNING_ASSIGNMENT = re.compile(
        r"""(?<![\w-])(?P<key>["']?(?:
            (?:[a-z][a-z0-9]*[_-])*secret[_-]?key
            |jwt[_-]?secret(?:[_-]?key)?
            |jwt[_-]?signing[_-]?key
            |signing[_-]?(?:secret|key)
            |(?:token|session|app|application)[_-]?secret
        )["']?)(?![\w-])[ \t]*(?:\])?
        (?:[ \t]*:[ \t]*[A-Za-z_][\w.\[\], |]*(?=[ \t]*=))?
        [ \t]*(?P<separator>=(?![=>])|:)[ \t]*""",
        re.IGNORECASE | re.VERBOSE,
    )
    SIGNING_MARKER = "[REDACTED SIGNING SECRET]"
    CREDENTIAL_ASSIGNMENT = re.compile(
        r"""(?<![\w-])(?P<key>["']?(?:[a-z][a-z0-9]*[_-])*(?:
            password|passwd|pwd|api[_-]?key|api[_-]?secret|aws[_-]?secret(?:[_-]?(?:access[_-]?)?key)?|secret|token
        )["']?)(?![\w-])[ \t]*(?:\])?
        (?:[ \t]*:[ \t]*[A-Za-z_][\w.\[\], |]*(?=[ \t]*=))?
        [ \t]*(?P<separator>=(?![=>])|:)[ \t]*""",
        re.IGNORECASE | re.VERBOSE,
    )


    @staticmethod
    def _value_end(content: str, start: int, *, yaml_plain: bool = False) -> int:
        """Bound a source/config RHS, including quoted and balanced continuations."""
        # YAML literal/folded block: consume its indented payload, not following keys.
        if re.match(r"(?:[|>](?:[1-9][+-]?|[+-][1-9]?)?[ \t]*(?:#[^\r\n]*)?)?\r?\n", content[start:]) or yaml_plain:
            line_start = content.rfind("\n", 0, start) + 1
            line_prefix = content[line_start:start]
            indent = len(line_prefix) - len(line_prefix.lstrip(" \t"))
            newline = content.find("\n", start)
            # Inline comments are not part of a YAML plain scalar.
            inline_comment = re.search(r"[ \t]+#", content[start:newline if newline >= 0 else len(content)])
            if yaml_plain and inline_comment:
                return start + inline_comment.start()
            end = len(content) if newline < 0 else newline
            cursor = end + 1
            while cursor < len(content):
                next_newline = content.find("\n", cursor)
                line_end = len(content) if next_newline < 0 else next_newline
                line = content[cursor:line_end]
                if line.strip() and len(line) - len(line.lstrip(" \t")) <= indent:
                    break
                end = line_end
                cursor = line_end + 1
            return end

        cursor = start
        closing = []
        while cursor < len(content):
            char = content[cursor]
            if char in "\"'" or char == chr(96):
                quote = char * 3 if content.startswith(char * 3, cursor) else char
                cursor += len(quote)
                while cursor < len(content):
                    if content[cursor] == "\\":
                        cursor += 2
                    elif content.startswith(quote, cursor):
                        cursor += len(quote)
                        break
                    else:
                        cursor += 1
                continue
            if char in "([{":
                closing.append({"(": ")", "[": "]", "{": "}"}[char])
            elif char in ")]}":
                if not closing:
                    break
                if char == closing[-1]:
                    closing.pop()
            elif not closing:
                if char in ",;\r\n" or ((char == "#" or content.startswith("//", cursor)) and (cursor == start or content[cursor - 1].isspace())):
                    break
                if char == "\\" and cursor + 1 < len(content) and content[cursor + 1] in "\r\n":
                    cursor += 2
                    if cursor < len(content) and content[cursor] == "\n":
                        cursor += 1
                    continue
            cursor += 1
        return cursor

    @staticmethod
    def _environment_reference(value: str) -> bool:
        """Keep simple lookups without embedded fallback values as useful context."""
        return bool(re.fullmatch(
            r"""(?:os\.getenv|os\.environ\.get)\(\s*(["'])[\w-]+\1\s*\)
                |os\.environ\[\s*(["'])[\w-]+\2\s*\]
                |process\.env\.[A-Za-z_]\w*""",
            value.strip(), re.VERBOSE,
        ))

    @staticmethod
    def _nonsensitive_python_expression(value: str) -> bool:
        """Preserve Python plumbing; do not evaluate or resolve its values.

        Names/member lookups and calls without embedded credential literals are
        context, not source credentials. Dictionary keys and subscript labels
        describe public fields. Dynamic/computed secrets remain unsupported.
        """
        try:
            expression = ast.parse(value.strip(), mode="eval").body
        except (SyntaxError, ValueError, RecursionError):
            return False
        if isinstance(expression, ast.Constant):
            return False  # A scalar value, including numeric passwords, is data.
        if isinstance(expression, ast.Name):
            # Bare INI/environment-style scalar values also parse as names.
            # Preserve only conventional credential parameter references.
            return expression.id in {"password", "plain_password", "hashed_password",
                                     "token", "access_token", "api_key"}
        labels = set()
        for node in ast.walk(expression):
            if isinstance(node, ast.Dict):
                labels.update(id(key) for key in node.keys if key is not None)
            elif isinstance(node, ast.Subscript):
                labels.add(id(node.slice))
        return not any(
            isinstance(node, (ast.JoinedStr, ast.FormattedValue)) or
            (isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes))
             and id(node) not in labels)
            for node in ast.walk(expression)
        )

    @staticmethod
    def _quoted_spans(content: str):
        """Recognize lexical strings so documentation is not an assignment."""
        cursor = 0
        while cursor < len(content):
            char = content[cursor]
            if char not in "\"'" and char != chr(96):
                cursor += 1
                continue
            start = cursor
            quote = char * 3 if content.startswith(char * 3, cursor) else char
            cursor += len(quote)
            while cursor < len(content):
                if content[cursor] == "\\":
                    cursor += 2
                elif content.startswith(quote, cursor):
                    cursor += len(quote)
                    break
                elif content[cursor] in "\r\n" and len(quote) == 1 and char != chr(96):
                    break
                else:
                    cursor += 1
            yield start, cursor

    def _signing_values(self, content: str, assignment_pattern=None):
        """Yield disjoint signing-value spans so partial literals cannot remain."""
        strings = iter(self._quoted_spans(content))
        string = next(strings, None)
        consumed = 0
        for match in (assignment_pattern or self.SIGNING_ASSIGNMENT).finditer(content):
            if match.start() < consumed:
                continue
            while string is not None and string[1] <= match.start():
                string = next(strings, None)
            if string is not None and string[0] <= match.start() < string[1]:
                # JSON/dictionary property names are strings themselves; a name
                # embedded in a larger documentation string is not a property.
                if not (match.start() == string[0]
                        and match.end("key") == string[1]):
                    continue
            start = match.end()
            following = start
            while following < len(content) and content[following].isspace():
                following += 1
            if following < len(content) and (content[following] in "\"'([{" or content[following] == chr(96)):
                # Newlines before JSON/JS/Python quoted or balanced values are
                # whitespace, not a YAML block. Keep delimiters after the value.
                start = following
            line_start = content.rfind("\n", 0, match.start()) + 1
            prefix = content[line_start:match.start()].strip()
            yaml_plain = (match.group("separator") == ":"
                          and prefix in ("", "-")
                          and start < len(content)
                          and content[start] not in "\"'([{|\r\n>"
                          and content[start] != chr(96))
            end = self._value_end(content, start, yaml_plain=yaml_plain)
            while end > start and content[end - 1] in " \t":
                end -= 1
            consumed = end
            value = content[start:end]
            if (match.group("separator") == ":" and
                    re.fullmatch(r"(?:str|bytes|int|float|bool|Final|Optional)(?:\[[\w. |]+\])?", value.strip())):
                continue
            if (assignment_pattern is self.CREDENTIAL_ASSIGNMENT
                    and not yaml_plain
                    and self._nonsensitive_python_expression(value)):
                continue
            if end > start and not self._environment_reference(value):
                yield start, end

    def _credential_label(self, content: str, start: int) -> str:
        key = ''
        for match in self.CREDENTIAL_ASSIGNMENT.finditer(content):
            if match.end() > start:
                break
            key = re.sub(r'[^a-z]', '', match.group('key').lower())
        if 'password' in key or key.endswith(('passwd', 'pwd')):
            return 'Password'
        if key.endswith('apikey'):
            return 'API key'
        if key.endswith('apisecret'):
            return 'API secret'
        if 'awssecret' in key:
            return 'AWS secret key'
        if key.endswith('token'):
            return 'Token'
        return 'Secret'

    def __init__(self, custom_file_patterns: List[str] = None, custom_content_patterns: List[tuple] = None):
        self.file_patterns: List[Pattern] = [re.compile(p) for p in self.SECRET_FILE_PATTERNS]
        if custom_file_patterns:
            self.file_patterns.extend([re.compile(p) for p in custom_file_patterns])

        self.content_patterns: List[tuple] = self.SECRET_CONTENT_PATTERNS.copy()
        if custom_content_patterns:
            self.content_patterns.extend(custom_content_patterns)

    def is_secret_file(self, file_path: Path) -> bool:
        """Check if a file path matches secret file patterns."""
        name = file_path.name
        relative = str(file_path)

        for pattern in self.file_patterns:
            if pattern.search(name) or pattern.search(relative):
                return True
        return False

    def scan_content(self, content: str) -> List[dict]:
        """Scan content for potential secrets."""
        findings = [
            {"type": "Signing secret", "match": self.SIGNING_MARKER, "position": start}
            for start, _ in self._signing_values(content)
        ]
        findings.extend({"type": self._credential_label(content, start), "match": "[REDACTED CREDENTIAL]", "position": start}
                        for start, _ in self._signing_values(content, self.CREDENTIAL_ASSIGNMENT))
        for pattern, description in self.content_patterns:
            matches = pattern.finditer(content)
            for match in matches:
                findings.append({
                    "type": description,
                    "match": match.group()[:50],  # Truncate for safety
                    "position": match.start(),
                })
        return findings

    def filter_file_list(self, files: List[Path]) -> List[Path]:
        """Filter out files that match secret patterns."""
        return [f for f in files if not self.is_secret_file(f)]

    def redact_content(self, content: str) -> str:
        """Redact potential secrets from content."""
        redacted = content
        # Preserve keys/separators and surrounding code/config while dropping the
        # complete RHS, including multiline and concatenated literal fragments.
        for start, end in reversed(list(self._signing_values(content))):
            redacted = redacted[:start] + '"' + self.SIGNING_MARKER + '"' + redacted[end:]
        for start, end in reversed(list(self._signing_values(redacted, self.CREDENTIAL_ASSIGNMENT))):
            value = redacted[start:end]
            if self.SIGNING_MARKER in value:
                continue  # Already covered by the stronger signing-secret rule.
            marker = '"[REDACTED ' + self._credential_label(redacted, start).upper() + ']"'
            # Preserve this common hashing call as useful nonsensitive context.
            # Other complex RHSs are replaced completely, never partly truncated.
            call = re.fullmatch(r"(?P<name>(?:get_password_hash|hash_password))\(\s*(?:[br])?(?P<quote>['\"])(?:\\.|(?!['\"]).)*['\"]\s*\)", value, re.DOTALL)
            replacement = call.group('name') + '(' + marker + ')' if call else marker
            redacted = redacted[:start] + replacement + redacted[end:]
        for pattern, description in self.content_patterns:
            redacted = pattern.sub(f"[REDACTED {description.upper()}]", redacted)
        return redacted
