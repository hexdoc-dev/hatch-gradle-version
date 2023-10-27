from hatchling.plugin import hookimpl

from .plugins.metadata_hook.gradle_properties import GradlePropertiesMetadataHook
from .plugins.version_scheme import GradleVersionScheme
from .plugins.version_source.gradle_properties import GradlePropertiesVersionSource


@hookimpl
def hatch_register_version_source():
    return GradlePropertiesVersionSource


@hookimpl
def hatch_register_version_scheme():
    return GradleVersionScheme


@hookimpl
def hatch_register_metadata_hook():
    return GradlePropertiesMetadataHook
