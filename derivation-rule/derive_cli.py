"""Agreement interface for the reference implementation (SPEC.md).

Reads one JSON object {"rule", "artifact", "params"} on stdin. On success writes
the derived claim's canonical bytes to stdout and exits 0; on a rejected rule or
artifact writes nothing to stdout and exits 1.
"""

import json
import sys

import derive


def _reject_lone_surrogates(value):
    """A lone surrogate anywhere in the request is a well-formedness failure
    (invalid Unicode) and rejects the request, matching the canon string rule.
    This is separate from the number domain: an artifact may hold a float, but
    no string in the request may hold a lone surrogate."""
    if isinstance(value, str):
        try:
            value.encode("utf-8")
        except UnicodeEncodeError:
            raise derive.RuleError("request string contains a lone surrogate")
    elif isinstance(value, dict):
        for key, item in value.items():
            _reject_lone_surrogates(key)
            _reject_lone_surrogates(item)
    elif isinstance(value, list):
        for item in value:
            _reject_lone_surrogates(item)


def main():
    try:
        request = json.load(sys.stdin)
        if not isinstance(request, dict) or "rule" not in request or "artifact" not in request:
            raise derive.RuleError("request needs rule and artifact")
        _reject_lone_surrogates(request)
        params = request.get("params", {})  # params optional, defaults to {}
        claim = derive.derive(request["rule"], request["artifact"], params)
        sys.stdout.buffer.write(derive.canon(claim))
        return 0
    except derive.RuleError:
        return 1
    except Exception as error:  # any other malformed request is also a rejection
        sys.stderr.write("derive_cli: %s\n" % error)
        return 1


if __name__ == "__main__":
    sys.exit(main())
