"""Base template class"""
from abc import ABC, abstractmethod
from PIL import ImageDraw


class BaseTemplate(ABC):
    """A slide template that renders a PIL Image from scene data."""

    name: str = ""

    @abstractmethod
    def render(self, draw: ImageDraw, scene: dict, idx: int):
        """Render the scene onto the draw context."""
        ...
