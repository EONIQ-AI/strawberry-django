from django.core.exceptions import ImproperlyConfigured


def import_geodjango():
    """Import GeoDjango, unless this project does not use it.

    Importing ``django.contrib.gis`` is not free: it ``dlopen``s libgdal and its whole
    transitive shared-library closure and pulls numpy into the interpreter -- around 39 MiB
    of RSS, roughly 12 MiB of which is private per process. Attempting it unconditionally
    charged that to *every* project on any machine where libgdal merely happened to be
    installed (a base image, an unrelated apt dependency), including projects with no
    geometry fields at all. The ``except ImproperlyConfigured`` below only backs off when
    GDAL is *absent* -- which is a fact about the machine, not about the project.

    So decide from settings first, which costs nothing. A geometry column requires a spatial
    database backend, and projects using GEOS objects without one have ``django.contrib.gis``
    in ``INSTALLED_APPS``; either signal means GeoDjango is in use.

    This stays an *eager* import rather than being deferred until the first geometry field is
    seen, because ``GraphQLCoreConverter`` snapshots ``DEFAULT_SCALAR_REGISTRY`` when the
    schema is constructed -- scalars registered after that point would never reach the schema.

    Raises ImproperlyConfigured when GeoDjango is not in use, so the caller can treat it the
    same way it already treats an unavailable GDAL. Reading settings raises the very same
    exception when they are not configured, which is likewise the right outcome here.
    """
    from django.conf import settings

    if "django.contrib.gis" not in settings.INSTALLED_APPS and not any(
        "gis" in (db.get("ENGINE") or "") for db in settings.DATABASES.values()
    ):
        raise ImproperlyConfigured("GeoDjango is not enabled for this project")

    from django.contrib.gis import geos
    from django.contrib.gis.db import models as geos_fields

    return geos, geos_fields
