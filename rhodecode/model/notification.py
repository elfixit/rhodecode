# -*- coding: utf-8 -*-
"""
    rhodecode.model.notification
    ~~~~~~~~~~~~~~

    Model for notifications
    
    
    :created_on: Nov 20, 2011
    :author: marcink
    :copyright: (C) 2009-2011 Marcin Kuzminski <marcin@python-works.com>
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
import traceback

from pylons.i18n.translation import _

from rhodecode.lib.helpers import age

from rhodecode.model import BaseModel
from rhodecode.model.db import Notification, User, UserNotification

log = logging.getLogger(__name__)

class NotificationModel(BaseModel):


    def __get_user(self, user):
        if isinstance(user, User):
            return user
        elif isinstance(user, basestring):
            return User.get_by_username(username=user)
        elif isinstance(user, int):
            return User.get(user)
        else:
            raise Exception('Unsupported user must be one of int,'
                            'str or User object')

    def __get_notification(self, notification):
        if isinstance(notification, Notification):
            return notification
        elif isinstance(notification, int):
            return Notification.get(notification)
        else:
            if notification:
                raise Exception('notification must be int or Instance'
                                ' of Notification got %s' % type(notification))


    def create(self, created_by, subject, body, recipients,
               type_=Notification.TYPE_MESSAGE):
        """
        
        Creates notification of given type
        
        :param created_by: int, str or User instance. User who created this
            notification
        :param subject:
        :param body:
        :param recipients: list of int, str or User objects
        :param type_: type of notification
        """

        if not getattr(recipients, '__iter__', False):
            raise Exception('recipients must be a list of iterable')

        created_by_obj = self.__get_user(created_by)

        recipients_objs = []
        for u in recipients:
            recipients_objs.append(self.__get_user(u))
        recipients_objs = set(recipients_objs)
        return Notification.create(created_by=created_by_obj, subject=subject,
                            body=body, recipients=recipients_objs,
                            type_=type_)

    def delete(self, notification_id):
        # we don't want to remove actuall notification just the assignment
        try:
            notification_id = int(notification_id)
            no = self.__get_notification(notification_id)
            if no:
                UserNotification.delete(no.notifications_to_users.user_to_notification_id)
                return True
        except Exception:
            log.error(traceback.format_exc())
            raise

    def get_for_user(self, user_id):
        return User.get(user_id).notifications

    def get_unread_cnt_for_user(self, user_id):
        return UserNotification.query()\
                .filter(UserNotification.read == False)\
                .filter(UserNotification.user_id == user_id).count()

    def get_unread_for_user(self, user_id):
        return [x.notification for x in UserNotification.query()\
                .filter(UserNotification.read == False)\
                .filter(UserNotification.user_id == user_id).all()]

    def get_user_notification(self, user, notification):
        user = self.__get_user(user)
        notification = self.__get_notification(notification)

        return UserNotification.query()\
            .filter(UserNotification.notification == notification)\
            .filter(UserNotification.user == user).scalar()

    def make_description(self, notification):
        """
        Creates a human readable description based on properties
        of notification object
        """

        _map = {notification.TYPE_CHANGESET_COMMENT:_('commented on commit'),
                notification.TYPE_MESSAGE:_('sent message'),
                notification.TYPE_MENTION:_('mentioned you')}

        tmpl = "%(user)s %(action)s %(when)s"
        data = dict(user=notification.created_by_user.username,
                    action=_map[notification.type_],
                    when=age(notification.created_on))
        return tmpl % data
