"""Knowledge base domain contracts and interfaces."""

from .events import EventInterface, EventDispatcherInterface
from .secret_provider import SecretProviderInterface
from .code_runner import CodeRunnerInterface, ExecutionResult
from .document_repository import DocumentMetadata, DocumentRepositoryInterface
from .schema_validator import SchemaValidatorInterface, ValidationIssue
from .asset_storage import AssetDescriptor, AssetStorageInterface

__all__ = [
    "EventInterface",
    "EventDispatcherInterface",
    "SecretProviderInterface",
    "CodeRunnerInterface",
    "ExecutionResult",
    "DocumentMetadata",
    "DocumentRepositoryInterface",
    "SchemaValidatorInterface",
    "ValidationIssue",
    "AssetDescriptor",
    "AssetStorageInterface",
]

