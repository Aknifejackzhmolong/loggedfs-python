# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/lib/__init__.py: Test library module init

	Copyright (C) 2017-2020 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the Apache License
Version 2 ("License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.apache.org/licenses/LICENSE-2.0
https://github.com/pleiszenburg/loggedfs-python/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .climount import (
	quick_cli_cleanup,
	quick_cli_init,
	quick_cli_init_parentfs,
	quick_cli_init_childfs,
	quick_cli_destroy,
	quick_cli_destroy_parentfs,
	quick_cli_destroy_childfs,
	)
from .const import (
	TEST_ROOT_PATH,
	TEST_FSTEST_PATH,
	TEST_FSTEST_TESTS_SUBPATH,
	)
from .install import (
	install_fstest,
	install_fsx,
	)
from .procio import run_command
from .param import fstest_parameters
from .scope import fstest_scope
