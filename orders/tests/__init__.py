from http import HTTPStatus

USER_EMAIL = 'user@example.com'
FROM_EMAIL = 'from@example.com'


def assert_success_response(response, status=HTTPStatus.OK):
    assert response.status_code == status
    return response.json()


def assert_success_status(response, status=HTTPStatus.OK):
    data = assert_success_response(response, status)
    assert data['Status']
    return data


def assert_fault_status(response, status=HTTPStatus.OK):
    data = assert_success_response(response, status)
    assert not data['Status']
    return data
