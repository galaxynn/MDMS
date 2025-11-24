# mdms/views/admin/__init__.py

from .admin_interface import AdminInterface
from .movie_management import MovieManagementWidget
from .person_management import PersonManagementWidget
from .user_management import UserManagementWidget
from .movie_form_dialog import MovieFormDialog
from .person_form_dialog import PersonFormDialog

__all__ = [
    'AdminInterface',
    'MovieManagementWidget',
    'PersonManagementWidget',
    'UserManagementWidget',
    'MovieFormDialog',
    'PersonFormDialog'
]