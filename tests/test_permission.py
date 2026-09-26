from bianque.core import permission


def test_check_camera_permission_returns_int():
    status = permission.check_camera_permission()
    assert isinstance(status, int)
    assert 0 <= status <= 3


def test_check_microphone_permission_returns_int():
    status = permission.check_microphone_permission()
    assert isinstance(status, int)
    assert 0 <= status <= 3


def test_status_label():
    assert permission.permission_status_label(permission.STATUS_AUTHORIZED) == "authorized"
    assert permission.permission_status_label(permission.STATUS_DENIED) == "denied"
    assert permission.permission_status_label(999) == "unknown"


def test_non_mac_returns_authorized(mocker):
    mocker.patch.object(permission, "IS_MAC", False)
    assert permission.check_camera_permission() == permission.STATUS_AUTHORIZED
    assert permission.check_microphone_permission() == permission.STATUS_AUTHORIZED
    assert permission.request_camera_permission() is True
    assert permission.request_microphone_permission() is True
