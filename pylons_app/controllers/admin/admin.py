#!/usr/bin/env python
# encoding: utf-8
# admin controller for pylons 
# Copyright (C) 2009-2010 Marcin Kuzminski <marcin@python-works.com>
 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2
# of the License or (at your opinion) any later version of the license.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA  02110-1301, USA.
"""
Created on April 7, 2010
admin controller for pylons
@author: marcink
"""
import logging
from pylons import request, response, session, tmpl_context as c
from pylons_app.lib.base import BaseController, render
from pylons_app.model import meta
from pylons_app.model.db import UserLog
from webhelpers.paginate import Page
from pylons_app.lib.auth import LoginRequired, HasPermissionAllDecorator

log = logging.getLogger(__name__)

class AdminController(BaseController):
    
    @LoginRequired()
    def __before__(self):
        super(AdminController, self).__before__()
    
    @HasPermissionAllDecorator('hg.admin')        
    def index(self):
        sa = meta.Session
                         
        users_log = sa.query(UserLog).order_by(UserLog.action_date.desc())
        p = int(request.params.get('page', 1))
        c.users_log = Page(users_log, page=p, items_per_page=10)
        c.log_data = render('admin/admin_log.html')
        if request.params.get('partial'):
            return c.log_data
        return render('admin/admin.html')    
                