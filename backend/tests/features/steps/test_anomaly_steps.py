from pytest_bdd import given, scenario, then, when
from pytest_bdd.parsers import parse

from app.simulators.refinery import RefinerySimulator
from app.simulators.rotating import RotatingEquipmentSimulator


# --- Scenarios ---

@scenario("anomaly_injection.feature", "Inject bearing fault into rotating equipment")
def test_bearing_fault():
    pass


@scenario("anomaly_injection.feature", "Rotating equipment dataset includes fault types")
def test_rotating_fault_types():
    pass


@scenario(
    "anomaly_injection.feature",
    "Anomaly rate is approximately 5 percent for standard simulators",
)
def test_standard_anomaly_rate():
    pass


@scenario("anomaly_injection.feature", "Rotating equipment has higher anomaly rate")
def test_rotating_anomaly_rate():
    pass


# --- Given steps ---

@given("a rotating equipment simulator", target_fixture="ctx")
def rotating_sim():
    return {"sim": RotatingEquipmentSimulator()}


@given("a refinery simulator for anomaly testing", target_fixture="ctx")
def refinery_sim():
    return {"sim": RefinerySimulator()}


@given("a rotating equipment simulator for anomaly testing", target_fixture="ctx")
def rotating_sim_anomaly():
    return {"sim": RotatingEquipmentSimulator()}


# --- When steps ---

@when(parse("I inject a {fault_type}"))
def inject_fault(ctx, fault_type):
    ctx["sim"].inject_fault(fault_type)


@when("I execute a step")
def execute_step(ctx):
    ctx["result"] = ctx["sim"].step()


@when(parse("I generate a rotating dataset with {count:d} samples including anomalies"))
def gen_rotating_dataset(ctx, count):
    ctx["dataset"] = ctx["sim"].generate_dataset(count, include_anomalies=True)


@when(parse("I generate a large dataset with {count:d} samples including anomalies"))
def gen_large_dataset(ctx, count):
    ctx["dataset"] = ctx["sim"].generate_dataset(count, include_anomalies=True)


@when(parse("I generate a large rotating dataset with {count:d} samples including anomalies"))
def gen_large_rotating_dataset(ctx, count):
    ctx["dataset"] = ctx["sim"].generate_dataset(count, include_anomalies=True)


# --- Then steps ---

@then("the output indicates a fault condition")
def check_fault_condition(ctx):
    result = ctx["result"]
    assert result["faultType"] != "no_fault" or result["faultSeverity"] > 0


@then(parse("the fault type is {fault_type}"))
def check_fault_type(ctx, fault_type):
    assert ctx["result"]["faultType"] == fault_type


@then("some anomaly rows have fault type labels")
def anomaly_has_fault_types(ctx):
    anomaly_rows = [r for r in ctx["dataset"] if r.get("anomaly") == 1]
    assert len(anomaly_rows) > 0
    fault_rows = [r for r in anomaly_rows if r.get("faultType") and r["faultType"] != "none"]
    assert len(fault_rows) > 0


@then(parse("the anomaly rate is between {low:d} and {high:d} percent"))
def check_anomaly_rate(ctx, low, high):
    total = len(ctx["dataset"])
    anomalies = sum(1 for r in ctx["dataset"] if r.get("anomaly") == 1)
    rate = anomalies / total * 100
    assert low <= rate <= high, f"Anomaly rate {rate:.1f}% outside [{low}, {high}]"
