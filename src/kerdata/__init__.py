"""Kerdata : une colonie de phoques, et la preuve qu'un registre sans nom n'est pas anonyme."""

from kerdata.population import generate
from kerdata.uniqueness import class_sizes, k_anonymity, unique_share, uniqueness_curve

__all__ = ["class_sizes", "generate", "k_anonymity", "unique_share", "uniqueness_curve"]
__version__ = "0.1.0"
