from hatchling.plugin import hookimpl

from .build_hook import GradlePropertiesBuildHook
from .version_scheme import GradleVersionScheme
from .version_source import PropertiesVersionSource


@hookimpl
def hatch_register_version_source():
    return PropertiesVersionSource


@hookimpl
def hatch_register_version_scheme():
    return GradleVersionScheme


@hookimpl
def hatch_register_build_hook():
    return GradlePropertiesBuildHook
