# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	tests/lib/climount.py: Quick mount from CLI for tests

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

from .base import fstest_base_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def quick_cli_cleanup():

	fs = fstest_base_class()
	fs.init_a_members()
	fs.init_b_cleanup()


def quick_cli_init():

	fs = fstest_base_class()
	fs.init_a_members()
	fs.init_b_cleanup()
	fs.init_c_parentfs()
	fs.init_d_childfs()


def quick_cli_init_parentfs():

	fs = fstest_base_class()
	fs.init_a_members()
	fs.init_c_parentfs()


def quick_cli_init_childfs():

	fs = fstest_base_class()
	fs.init_a_members()
	fs.init_d_childfs()


def quick_cli_destroy():

	fs = fstest_base_class()
	fs.init_a_members()
	fs.destroy_a_childfs()
	fs.destroy_b_parentfs()


def quick_cli_destroy_parentfs():

	fs = fstest_base_class()
	fs.init_a_members()
	fs.assert_parentfs_mountpoint()
	fs.destroy_b_parentfs()


def quick_cli_destroy_childfs():

	fs = fstest_base_class()
	fs.init_a_members()
	fs.assert_childfs_mountpoint()
	fs.destroy_a_childfs()
