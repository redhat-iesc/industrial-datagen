Feature: Industrial Process Simulation
  As a data engineer
  I want to run physics-based industrial simulations
  So that I can generate labeled training data for ML models

  Scenario Outline: Simulator produces valid output
    Given a <process_type> simulator with default parameters
    When I execute a simulation step
    Then the output contains all expected fields
    And all numeric values are within valid ranges

    Examples:
      | process_type |
      | refinery     |
      | chemical     |
      | pulp         |
      | pharma       |
      | rotating     |

  Scenario Outline: Parameter changes affect simulator output
    Given a <process_type> simulator with default parameters
    When I change the <parameter> to <value>
    And I execute a simulation step
    Then the <affected_output> differs from the default output

    Examples:
      | process_type | parameter   | value | affected_output |
      | refinery     | crudeTemp   | 380   | efficiency      |
      | chemical     | temperature | 380   | conversion      |
      | pulp         | temperature | 185   | delignification |
      | pharma       | temperature | 55    | impurityLevel   |
      | rotating     | loadPercent | 95    | vibrationOverall|

  Scenario Outline: Dataset generation produces correct sample count
    Given a <process_type> simulator with default parameters
    When I generate a dataset with <count> samples
    Then the dataset contains exactly <count> rows
    And each row has a timestamp field
    And each row has an anomaly label

    Examples:
      | process_type | count |
      | refinery     | 100   |
      | chemical     | 100   |
      | pulp         | 100   |
      | pharma       | 100   |
      | rotating     | 100   |

  Scenario Outline: Anomaly injection produces labeled anomalies
    Given a <process_type> simulator with default parameters
    When I generate a dataset with 1000 samples including anomalies
    Then the dataset contains some rows labeled as anomalies
    And anomaly rows have parameter values outside normal ranges

    Examples:
      | process_type |
      | refinery     |
      | chemical     |
      | pulp         |
      | pharma       |
      | rotating     |
