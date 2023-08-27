from hatchling.plugin import hookimpl

from .version_source import PropertiesVersionSource


@hookimpl
def hatch_register_version_source():
    return [PropertiesVersionSource]
