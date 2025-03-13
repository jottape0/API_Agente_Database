from typing import ClassVar, List


class ModelProvider:
    AVAILABLE_MODELS: ClassVar[List[str]] = [
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo"
    ]

    @classmethod
    def get_available_models(cls) -> List[str]:
        return cls.AVAILABLE_MODELS