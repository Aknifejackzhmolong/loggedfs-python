# -*- coding: utf-8 -*-

"""

LoggedFS-python
Filesystem monitoring with Fuse and Python
https://github.com/pleiszenburg/loggedfs-python

	src/loggedfs/filter.py: Filtering events by criteria

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

import re


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def compile_filters(include_list, exclude_list):

	if len(include_list) == 0:
		include_list.append({
			'extension': '.*',
			'uid': '*',
			'action': '.*',
			'retname': '.*'
			})

	return tuple(
		[_compile_filter_item_(item) for item in in_list]
		for in_list in (include_list, exclude_list)
		)


def _compile_filter_item_(in_item):

	return (
		re.compile(in_item['extension']),
		int(in_item['uid']) if in_item['uid'].isnumeric() else None,
		re.compile(in_item['action']),
		re.compile(in_item['retname'])
		)


def match_filters(
	abs_path, uid, action, ret_status,
	incl_filter_list, excl_filter_list
	):

	if len(incl_filter_list) != 0:
		included = False
		for filter_tuple in incl_filter_list:
			if _match_filter_item_(abs_path, uid, action, ret_status, *filter_tuple):
				included = True
				break
		if not included:
			return False

	for filter_tuple in excl_filter_list:
		if _match_filter_item_(abs_path, uid, action, ret_status, *filter_tuple):
			return False

	return True


def _match_filter_item_(
	abs_path, uid, action, ret_status,
	f_path, f_uid, f_action, f_status
	):

	return all((
		bool(f_path.match(abs_path)),
		(uid == f_uid) if isinstance(f_uid, int) else True,
		bool(f_action.match(action)),
		bool(f_status.match(ret_status))
		))
