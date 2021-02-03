from typing import Any
from typing import Dict

import pytest

from paasta_tools.setup_prometheus_adapter_config import (
    create_instance_uwsgi_scaling_rule,
)
from paasta_tools.setup_prometheus_adapter_config import (
    should_create_uwsgi_scaling_rule,
)


@pytest.mark.parametrize(
    "instance_name, instance_config,expected",
    [
        ("_not_a_real_instance", {}, False),
        ("not_autoscaled", {}, False),
        (
            "not_uwsgi_autoscaled",
            {"autoscaling": {"decision_policy": "bespoke"}},
            False,
        ),
        (
            "uwsgi_autoscaled_no_prometheus",
            {"autoscaling": {"metrics_provider": "uwsgi"}},
            False,
        ),
        (
            "uwsgi_autoscaled_prometheus",
            {"autoscaling": {"metrics_provider": "uwsgi", "use_prometheus": True}},
            True,
        ),
    ],
)
def test_should_create_uswgi_scaling_rule(
    instance_name: str, instance_config: Dict[str, Any], expected: bool
) -> None:
    should_create, reason = should_create_uwsgi_scaling_rule(
        instance=instance_name, instance_config=instance_config
    )

    assert should_create == expected
    if expected:
        assert reason is None
    else:
        assert reason is not None


def test_create_instance_uwsgi_scaling_rule() -> None:
    service_name = "test_service"
    instance_name = "test_instance"
    paasta_cluster = "test_cluster"
    instance_config = {
        "autoscaling": {
            "setpoint": 0.1234567890,
            "moving_average_window_seconds": 20120302,
        }
    }

    rule = create_instance_uwsgi_scaling_rule(
        service=service_name,
        instance=instance_name,
        paasta_cluster=paasta_cluster,
        instance_config=instance_config,
    )

    # we test that the format of the dictionary is as expected with mypy
    # and we don't want to test the full contents of the retval since then
    # we're basically just writting a change-detector test - instead, we test
    # that we're actually using our inputs
    assert service_name in rule["seriesQuery"]
    assert instance_name in rule["seriesQuery"]
    assert paasta_cluster in rule["seriesQuery"]
    # these two numbers are distinctive and unlikely to be used as constants
    assert str(instance_config["autoscaling"]["setpoint"]) in rule["metricsQuery"]
    assert (
        str(instance_config["autoscaling"]["moving_average_window_seconds"])
        in rule["metricsQuery"]
    )
