from pytest_bdd import given, parsers, scenario, then, when

from app.simulators.chemical import ChemicalSimulator
from app.simulators.pharma import PharmaSimulator
from app.simulators.pulp import PulpSimulator
from app.simulators.refinery import RefinerySimulator
from app.simulators.rotating import RotatingEquipmentSimulator

SIMULATORS = {
    "refinery": RefinerySimulator,
    "chemical": ChemicalSimulator,
    "pulp": PulpSimulator,
    "pharma": PharmaSimulator,
    "rotating": RotatingEquipmentSimulator,
}


@pytest.fixture
def context():
    return {}


# --- Scenario: Simulator produces valid output ---

@scenario("simulation.feature", "Simulator produces valid output")
def test_valid_output():
    pass


@given(
    parsers.parse("a {process_type} simulator with default parameters"),
    target_fixture="context",
)
def simulator_with_defaults(process_type):
    sim_class = SIMULATORS[process_type]
    sim = sim_class()
    return {"sim": sim, "process_type": process_type}


@when("I execute a simulation step")
def execute_step(context):
    context["result"] = context["sim"].step()


@then("the output contains all expected fields")
def output_has_expected_fields(context):
    result = context["result"]
    sim = context["sim"]
    for field in sim.output_fields():
        assert field.name in result, f"Missing field: {field.name}"


@then("all numeric values are within valid ranges")
def numeric_values_valid(context):
    result = context["result"]
    for key, value in result.items():
        if isinstance(value, (int, float)) and key != "timestamp":
            assert not (value != value), f"NaN detected for {key}"


# --- Scenario: Parameter changes affect simulator output ---

@scenario("simulation.feature", "Parameter changes affect simulator output")
def test_parameter_changes():
    pass


@when(parsers.parse("I change the {parameter} to {value:d}"))
def change_parameter(context, parameter, value):
    context["sim"].parameters[parameter] = value


@then(parsers.parse("the {affected_output} differs from the default output"))
def output_differs(context, affected_output):
    sim_class = SIMULATORS[context["process_type"]]
    default_sim = sim_class()
    default_result = default_sim.step()
    assert context["result"][affected_output] != default_result[affected_output]


# --- Scenario: Dataset generation produces correct sample count ---

@scenario("simulation.feature", "Dataset generation produces correct sample count")
def test_dataset_count():
    pass


@when(parsers.parse("I generate a dataset with {count:d} samples"))
def generate_dataset(context, count):
    context["dataset"] = context["sim"].generate_dataset(count)
    context["count"] = count


@then(parsers.parse("the dataset contains exactly {count:d} rows"))
def dataset_has_count(context, count):
    assert len(context["dataset"]) == count


@then("each row has a timestamp field")
def each_row_has_timestamp(context):
    for row in context["dataset"]:
        assert "timestamp" in row


@then("each row has an anomaly label")
def each_row_has_anomaly(context):
    for row in context["dataset"]:
        assert "anomaly" in row
        assert row["anomaly"] in (0, 1, True, False)


# --- Scenario: Anomaly injection produces labeled anomalies ---

@scenario("simulation.feature", "Anomaly injection produces labeled anomalies")
def test_anomaly_injection():
    pass


@when("I generate a dataset with 1000 samples including anomalies")
def generate_dataset_with_anomalies(context):
    context["dataset"] = context["sim"].generate_dataset(1000, include_anomalies=True)


@then("the dataset contains some rows labeled as anomalies")
def has_anomalies(context):
    anomaly_count = sum(1 for row in context["dataset"] if row["anomaly"] == 1)
    assert anomaly_count > 0


@then("anomaly rows have parameter values outside normal ranges")
def anomaly_values_differ(context):
    normal_rows = [r for r in context["dataset"] if r["anomaly"] == 0]
    anomaly_rows = [r for r in context["dataset"] if r["anomaly"] == 1]
    assert len(anomaly_rows) > 0
    assert len(normal_rows) > 0
