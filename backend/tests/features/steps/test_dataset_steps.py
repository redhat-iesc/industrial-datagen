import csv
import io

from pytest_bdd import given, scenario, then, when
from pytest_bdd.parsers import parse

from app.simulators import SIMULATOR_REGISTRY


# --- Scenarios ---

@scenario("dataset_generation.feature", "Generate dataset with correct row count")
def test_correct_row_count():
    pass


@scenario("dataset_generation.feature", "Generate dataset with anomalies included")
def test_anomalies_included():
    pass


@scenario("dataset_generation.feature", "Generate dataset without anomalies")
def test_no_anomalies():
    pass


@scenario("dataset_generation.feature", "Dataset rows contain all output fields")
def test_all_output_fields():
    pass


@scenario("dataset_generation.feature", "CSV format has header plus data rows")
def test_csv_format():
    pass


# --- Given steps ---

@given(parse("a {process_type} simulator"), target_fixture="ctx")
def create_simulator(process_type):
    sim_class = SIMULATOR_REGISTRY[process_type]
    return {"sim": sim_class(), "process_type": process_type}


# --- When steps ---

@when(parse("I generate a dataset with {count:d} samples"))
def generate_dataset(ctx, count):
    ctx["dataset"] = ctx["sim"].generate_dataset(count)


@when(parse("I generate a dataset with {count:d} samples including anomalies"))
def generate_dataset_with_anomalies(ctx, count):
    ctx["dataset"] = ctx["sim"].generate_dataset(count, include_anomalies=True)


@when(parse("I generate a dataset with {count:d} samples without anomalies"))
def generate_dataset_without_anomalies(ctx, count):
    ctx["dataset"] = ctx["sim"].generate_dataset(count, include_anomalies=False)


@when("I convert the dataset to CSV")
def convert_to_csv(ctx):
    dataset = ctx["dataset"]
    if not dataset:
        ctx["csv_text"] = ""
        return
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=dataset[0].keys())
    writer.writeheader()
    writer.writerows(dataset)
    ctx["csv_text"] = output.getvalue()


# --- Then steps ---

@then(parse("the dataset has exactly {count:d} rows"))
def check_row_count(ctx, count):
    assert len(ctx["dataset"]) == count


@then("each row contains a timestamp")
def each_row_has_timestamp(ctx):
    for row in ctx["dataset"]:
        assert "timestamp" in row


@then("each row contains an anomaly label")
def each_row_has_anomaly(ctx):
    for row in ctx["dataset"]:
        assert "anomaly" in row


@then("some rows are labeled as anomalies")
def has_anomalies(ctx):
    anomaly_count = sum(1 for r in ctx["dataset"] if r.get("anomaly") == 1)
    assert anomaly_count > 0


@then(parse("the anomaly rate is between {low:d} and {high:d} percent"))
def check_anomaly_rate(ctx, low, high):
    total = len(ctx["dataset"])
    anomalies = sum(1 for r in ctx["dataset"] if r.get("anomaly") == 1)
    rate = anomalies / total * 100
    assert low <= rate <= high, f"Anomaly rate {rate:.1f}% outside [{low}, {high}]"


@then("no rows are labeled as anomalies")
def no_anomalies(ctx):
    anomaly_count = sum(1 for r in ctx["dataset"] if r.get("anomaly") == 1)
    assert anomaly_count == 0


@then("each row contains all expected output fields")
def all_output_fields(ctx):
    sim = ctx["sim"]
    expected = {f.name for f in sim.output_fields()}
    for row in ctx["dataset"]:
        for field in expected:
            assert field in row, f"Missing field: {field}"


@then(parse("the CSV has {count:d} lines"))
def csv_line_count(ctx, count):
    lines = ctx["csv_text"].strip().split("\n")
    assert len(lines) == count


@then("the first line is a header row")
def csv_has_header(ctx):
    lines = ctx["csv_text"].strip().split("\n")
    header = lines[0]
    assert "timestamp" in header
    assert "anomaly" in header
