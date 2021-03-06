# -*- coding: utf-8 -*-
"""
    rhodecode.websetup
    ~~~~~~~~~~~~~~~~~~

    Weboperations and setup for rhodecode

    :created_on: Dec 11, 2010
    :author: marcink
    :copyright: (C) 2010-2012 Marcin Kuzminski <marcin@python-works.com>
    :license: GPLv3, see COPYING for more details.
"""
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from rhodecode.config.environment import load_environment
from rhodecode.lib.db_manage import DbManage
from rhodecode.model.meta import Session


log = logging.getLogger(__name__)


def setup_app(command, conf, vars):
    """Place any commands to setup rhodecode here"""
    dbconf = conf['sqlalchemy.db1.url']
    dbmanage = DbManage(log_sql=True, dbconf=dbconf, root=conf['here'],
                        tests=False)
    dbmanage.create_tables(override=True)
    dbmanage.set_db_version()
    opts = dbmanage.config_prompt(None, defaults=command.options.__dict__)
    dbmanage.create_settings(opts)
    dbmanage.create_default_user()
    dbmanage.admin_prompt(defaults=command.options.__dict__)
    dbmanage.create_permissions()
    dbmanage.populate_default_permissions()
    Session.commit()
    load_environment(conf.global_conf, conf.local_conf, initial=True)
