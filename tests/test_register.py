"""
test.test_register
~~~

    - build a Docker image from a latch package
    - serialize latch package within said image
    - retrieve federated credentials + login to latch's container registry
    - upload image to latch's container registry
    - register serialized package with latch api

"""

import tempfile
from pathlib import Path

import pytest
from latch.services.init import _gen__init__
from latch.services.register import register
from latch.services.register.models import RegisterCtx
from latch.services.register.register import (_build_image,
                                              _register_serialized_pkg,
                                              _serialize_pkg,
                                              _upload_pkg_image)


@pytest.fixture(scope="session")
def test_account_jwt():
    tmp_token = ""
    return tmp_token


_VERSION_0 = "0.0.0"
_VERSION_1 = "0.0.1"


def _validate_stream(stream, pkg_name, version):

    lines = []
    for chunk in stream:
        print(chunk)
        lines.append(chunk)

    last_line = lines[-1]["stream"]

    # https://github.com/docker/docker-py/blob/master/tests/ssh/api_build_test.py#L570
    # Sufficient for moby's official api, suff. for us...
    assert "Successfully tagged" in last_line
    assert pkg_name in last_line
    assert version in last_line


def _setup_and_build_wo_dockerfile(jwt, pkg_name, requirements=None):

    with tempfile.TemporaryDirectory() as tmpdir:

        pkg_dir = Path(tmpdir).joinpath(pkg_name)
        pkg_dir.mkdir()

        with open(pkg_dir.joinpath("__init__.py"), "w") as f:
            f.write(_gen__init__(pkg_name))

        with open(pkg_dir.joinpath("version"), "w") as f:
            f.write(_VERSION_0)

        ctx = RegisterCtx(pkg_root=pkg_dir, token=jwt)
        stream = _build_image(ctx, requirements=requirements)
        _validate_stream(stream, pkg_name, _VERSION_0)


def _setup_and_build_w_dockerfile(jwt, pkg_name):

    with tempfile.TemporaryDirectory() as tmpdir:

        pkg_dir = Path(tmpdir).joinpath(pkg_name)
        pkg_dir.mkdir()

        with open(pkg_dir.joinpath("__init__.py"), "w") as f:
            f.write(_gen__init__(pkg_name))

        with open(pkg_dir.joinpath("version"), "w") as f:
            f.write(_VERSION_0)

        dockerfile = Path(tmpdir).joinpath("Dockerfile")
        with open(dockerfile, "w") as df:
            df.write(
                "\n".join(
                    [
                        "FROM busybox",
                        f"COPY {pkg_name} /src/{pkg_name}",
                        "WORKDIR /src",
                    ]
                )
            )

        ctx = RegisterCtx(pkg_root=pkg_dir, token=jwt)
        stream = _build_image(ctx, dockerfile=dockerfile)
        _validate_stream(stream, pkg_name, _VERSION_0)


def test_build_image_wo_dockerfile(test_account_jwt):

    _setup_and_build_wo_dockerfile(test_account_jwt, "foo")
    _setup_and_build_wo_dockerfile(test_account_jwt, "foo-bar")


def test_build_image_w_dockerfile(test_account_jwt):

    _setup_and_build_w_dockerfile(test_account_jwt, "foo")
    _setup_and_build_w_dockerfile(test_account_jwt, "foo-bar")


def test_serialize_pkg():
    ...


def test_registry_login():
    ...


def test_image_upload():
    ...


def test_pkg_register():
    ...