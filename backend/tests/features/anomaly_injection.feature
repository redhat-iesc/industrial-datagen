Feature: Anomaly Injection
  As a data engineer
  I want to inject faults into simulations
  So that I can generate labeled anomalous data for training

  Scenario: Inject bearing fault into rotating equipment
    Given a rotating equipment simulator
    When I inject a bearing_fault
    And I execute a step
    Then the output indicates a fault condition
    And the fault type is bearing_fault

  Scenario: Rotating equipment dataset includes fault types
    Given a rotating equipment simulator
    When I generate a rotating dataset with 200 samples including anomalies
    Then some anomaly rows have fault type labels

  Scenario: Anomaly rate is approximately 5 percent for standard simulators
    Given a refinery simulator for anomaly testing
    When I generate a large dataset with 1000 samples including anomalies
    Then the anomaly rate is between 2 and 10 percent

  Scenario: Rotating equipment has higher anomaly rate
    Given a rotating equipment simulator for anomaly testing
    When I generate a large rotating dataset with 1000 samples including anomalies
    Then the anomaly rate is between 15 and 35 percent
