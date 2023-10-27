from hatchling.plugin import hookimpl

from .metadata_hook.gradle_properties import GradlePropertiesMetadataHook
from .version_scheme import GradleVersionScheme
from .version_source.gradle_properties import PropertiesVersionSource


@hookimpl
def hatch_register_version_source():
    return PropertiesVersionSource


@hookimpl
def hatch_register_version_scheme():
    return GradleVersionScheme


@hookimpl
def hatch_register_metadata_hook():
    return GradlePropertiesMetadataHook
