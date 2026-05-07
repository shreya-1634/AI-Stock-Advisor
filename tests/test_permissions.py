# your_project/tests/test_permissions.py

import pytest
from auths.permissions import Permissions

def test_guest_permissions():
    assert not Permissions.check_permission("guest", "view_charts_basic")
    assert not Permissions.check_permission("guest", "get_predictions")

def test_free_user_permissions():
    assert Permissions.check_permission("free", "view_charts_basic")
    assert Permissions.check_permission("free", "view_news_headlines")
    assert not Permissions.check_permission("free", "get_predictions")
    assert not Permissions.check_permission("free", "view_charts_advanced")

def test_premium_user_permissions():
    assert Permissions.check_permission("premium", "view_charts_basic")
    assert Permissions.check_permission("premium", "view_charts_advanced")
    assert Permissions.check_permission("premium", "get_predictions")
    assert Permissions.check_permission("premium", "get_recommendations")
    assert not Permissions.check_permission("premium", "manage_users")

def test_admin_user_permissions():
    assert Permissions.check_permission("admin", "view_charts_basic")
    assert Permissions.check_permission("admin", "manage_users")