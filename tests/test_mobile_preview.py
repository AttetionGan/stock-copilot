from pathlib import Path
import runpy
from types import SimpleNamespace

import pytest


preview = runpy.run_path(str(Path(__file__).resolve().parents[1] / "scripts" / "mobile_preview.py"))


def runner(route="en0", addresses=None):
    addresses = addresses or {}
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(stdout=f"interface: {route}" if args[0] == "/sbin/route" else addresses.get(args[-1], ""))

    return run, calls


def test_preview_uses_physical_lan_instead_of_vpn():
    # These addresses are synthetic fixtures, not machine connection settings.
    run, calls = runner("utun9", {"en0": "192.168.50.20", "utun9": "10.0.0.2"})
    assert preview["private_lan_address"](run) == "192.168.50.20"
    assert not any(args[-1] == "utun9" for args in calls)


def test_preview_supports_other_active_ethernet_interfaces():
    run, _ = runner("en3", {"en3": "172.20.1.20"})
    assert preview["private_lan_address"](run) == "172.20.1.20"


@pytest.mark.parametrize("address", ["8.8.8.8", "127.0.0.1", "169.254.1.20", "", "not-an-address"])
def test_preview_refuses_non_lan_or_invalid_addresses(address):
    run, _ = runner(addresses={"en0": address, "en1": address})
    with pytest.raises(RuntimeError):
        preview["private_lan_address"](run)
