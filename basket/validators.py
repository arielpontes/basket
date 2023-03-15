from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class BaseSchemaValidator:
    def __call__(self, value):
        # import ipdb

        # ipdb.set_trace()
        actual_keys = set(value.keys())
        missing_keys = self.expected_keys - actual_keys
        extra_keys = actual_keys - self.expected_keys
        if missing_keys:
            raise ValidationError(
                f"The following keys are missing: {', '.join(missing_keys)}."
            )
        if extra_keys:
            raise ValidationError(
                f"Invalid keys '{extra_keys}'. "
                f"The accepted keys are: {', '.join(self.expected_keys)}."
            )


class StatusValidator(BaseSchemaValidator):
    expected_keys = {
        "long",
        "short",
        "timer",
    }


class ScoreValidator(BaseSchemaValidator):
    expected_keys = {
        "quarter_1",
        "quarter_2",
        "quarter_3",
        "quarter_4",
        "over_time",
        "total",
    }

    def __call__(self, value):
        super().__call__(value)
        for value in value.values():
            if value:
                try:
                    int(value)
                except Exception:
                    raise ValidationError(f"Couldn't convert {value} to int.")
