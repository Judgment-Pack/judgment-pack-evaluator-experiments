"""Public evaluator error types."""


class EvaluationError(Exception):
    """Base class for failures that are explicitly not dispositions."""

    code = "evaluation-error"


class EvaluationInputError(EvaluationError):
    """A supplied pack, facts document, evidence object, or capability list is malformed."""

    code = "invalid-input"


class UnsupportedExtensionError(EvaluationError):
    """The pack requires an extension capability the evaluator was not given."""

    code = "unsupported-required-extension"


class ResourceLimitError(EvaluationError):
    """A documented evaluator resource limit was exceeded."""

    code = "resource-limit"


class PointerError(Exception):
    """Base class for JSON Pointer failures used by the low-level pointer helper."""


class PointerSyntaxError(PointerError):
    """A string is not valid RFC 6901 JSON Pointer syntax."""


class PointerResolutionError(PointerError):
    """A valid JSON Pointer does not resolve against a particular document."""
