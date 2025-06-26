# View module imports for Oreon Build System (formerly COPR)

# Import all blueprint modules
from coprs.views import admin_ns
from coprs.views.admin_ns import admin_general

from coprs.views import api_ns
from coprs.views.api_ns import api_general

from coprs.views import apiv3_ns
from coprs.views.apiv3_ns import (
    apiv3_general, apiv3_builds, apiv3_packages, apiv3_projects,
    apiv3_project_chroots, apiv3_modules, apiv3_build_chroots,
    apiv3_mock_chroots, apiv3_permissions, apiv3_webhooks, apiv3_monitor,
    apiv3_rpmrepo,
)

from coprs.views import batches_ns
from coprs.views.batches_ns import coprs_batches

from coprs.views import coprs_ns
from coprs.views.coprs_ns import coprs_builds
from coprs.views.coprs_ns import coprs_general
from coprs.views.coprs_ns import coprs_chroots
from coprs.views.coprs_ns import coprs_packages
from coprs.views.coprs_ns import pagination_redirect

from coprs.views import backend_ns
from coprs.views.backend_ns import backend_general

from coprs.views import misc

from coprs.views import status_ns
from coprs.views.status_ns import status_general

from coprs.views import recent_ns
from coprs.views.recent_ns import recent_general

from coprs.views.stats_ns import stats_receiver

from coprs.views import tmp_ns
from coprs.views.tmp_ns import tmp_general

from coprs.views.groups_ns import groups_ns
from coprs.views.groups_ns import groups_general

from coprs.views.user_ns import user_ns
from coprs.views.user_ns import user_general

from coprs.views.webhooks_ns import webhooks_ns
from coprs.views.webhooks_ns import webhooks_general

from coprs.views.rss_ns import rss_ns
from coprs.views.rss_ns import rss_general

from coprs.views.explore_ns import explore_ns

# Import the new ISO builder views
from coprs.views.iso_ns import iso_ns

# All blueprints that need to be registered are listed here
# They will be imported by the main application
__all__ = [
    'admin_ns',
    'api_ns', 
    'apiv3_ns',
    'batches_ns',
    'coprs_ns',
    'backend_ns',
    'misc',
    'status_ns',
    'recent_ns',
    'stats_receiver',
    'tmp_ns',
    'groups_ns',
    'user_ns',
    'webhooks_ns',
    'rss_ns',
    'explore_ns',
    'iso_ns',  # New ISO builder module
]
