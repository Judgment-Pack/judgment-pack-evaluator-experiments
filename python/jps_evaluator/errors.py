"""Public evaluator errors implementing Core §8.4's class and phase contract."""


class EvaluationError(Exception):
    """Base class for failures that are explicitly not dispositions."""

    code = "org.judgmentpack.python.evaluation-error"
    phase = "evaluation"

    @property
    def error_class(self) -> str:
        """Return the machine-readable Core or implementation-defined class."""

        return self.code


class PackNotConformantError(EvaluationError):
    """The pack failed carrier, structural, or semantic conformance."""

    code = "pack-not-conformant"
    phase = "preflight"


class EvaluationInputError(EvaluationError):
    """A non-pack input failed Core §8.2 preflight.

    The historical public name is retained for API compatibility. Its class is
    the Core ``malformed-input`` class.
    """

    code = "malformed-input"
    phase = "preflight"


# A descriptive spelling for new callers; both names denote the same class.
MalformedInputError = EvaluationInputError


class UnsupportedExtensionError(EvaluationError):
    """The pack requires an extension capability the evaluator was not given."""

    code = "unsupported-required-extension"
    phase = "preflight"


class ResourceLimitError(EvaluationError):
    """A documented collection or work limit was reached during evaluation."""

    code = "resource-exhaustion"
    phase = "evaluation"


class PointerError(Exception):
    """Base class for JSON Pointer failures used by the low-level pointer helper."""


class PointerSyntaxError(PointerError):
    """A string is not valid RFC 6901 JSON Pointer syntax."""


class PointerResolutionError(PointerError):
    """A valid JSON Pointer does not resolve against a particular document."""
