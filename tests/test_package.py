"""The package as it is installed: what a type checker and a user of it see."""
import importlib.metadata
import importlib.resources
import re

import wavin_sentio_connect


def test_it_ships_its_types() -> None:
    """PEP 561: without py.typed, a type checker treats every import of the package as untyped."""
    assert importlib.resources.files(wavin_sentio_connect).joinpath("py.typed").is_file()


def test_its_version_is_the_one_it_was_installed_as() -> None:
    assert wavin_sentio_connect.__version__ == importlib.metadata.version("wavin_sentio_connect")


def test_every_link_in_its_description_works_where_the_description_is_shown() -> None:
    """PyPI shows the README without the repository's files, so a relative link there is dead."""
    description = importlib.metadata.metadata("wavin_sentio_connect").json["description"]
    assert isinstance(description, str) and description
    links = re.findall(r"\]\(([^)]+)\)", description)
    assert links and all(link.startswith(("https://", "#")) for link in links), links


def test_what_it_passes_on_from_modbus_event_connect_is_that_packages_own() -> None:
    """What the package passes on is modbus_event_connect's own, not a copy that could drift."""
    import modbus_event_connect
    import modbus_event_connect.modbus
    import modbus_event_connect.testing

    import wavin_sentio_connect.testing

    for package, sources in (
        (wavin_sentio_connect, (modbus_event_connect, modbus_event_connect.modbus)),
        (wavin_sentio_connect.testing, (modbus_event_connect.modbus, modbus_event_connect.testing)),
    ):
        for name in package.__all__:
            source = next((s for s in sources if name in getattr(s, "__all__", ())), None)
            if source is not None:
                assert getattr(package, name) is getattr(source, name), name
    assert "Client" in wavin_sentio_connect.__all__
    assert "SimulatedModbusDevice" in wavin_sentio_connect.testing.__all__


SHARED = (
    "AuthenticationError", "CannotConnectError", "Certainty", "Change", "ClientError", "Clock", "DataValue",
    "DeviceClient", "Identity", "InvalidValueError", "Key", "Labels", "Limits", "ModelError", "NotConnectedError",
    "PointsCallback", "PollRate", "Quality", "ReadOnlyError", "Selector", "Status", "StatusCallback", "Unit",
    "UnsupportedDeviceError", "ValueCallback", "Write", "WriteKind", "WriteRange", "Level", "Candidate",
)
"""The names every library built on event_connect passes on, so that each is used alike."""


def test_it_passes_on_every_shared_name_as_event_connects_own() -> None:
    import event_connect

    for name in SHARED:
        assert name in wavin_sentio_connect.__all__, name
        assert getattr(wavin_sentio_connect, name) is getattr(event_connect, name), name


def test_it_passes_on_the_type_of_its_model() -> None:
    assert "ModbusModel" in wavin_sentio_connect.__all__
    assert isinstance(wavin_sentio_connect.SENTIO, wavin_sentio_connect.ModbusModel)
