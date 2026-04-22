Feature: Dataset Generation
  As a data engineer
  I want to generate industrial datasets in various formats
  So that I can use them for ML model training

  Scenario: Generate dataset with correct row count
    Given a refinery simulator
    When I generate a dataset with 20 samples
    Then the dataset has exactly 20 rows
    And each row contains a timestamp
    And each row contains an anomaly label

  Scenario: Generate dataset with anomalies included
    Given a chemical simulator
    When I generate a dataset with 200 samples including anomalies
    Then some rows are labeled as anomalies
    And the anomaly rate is between 1 and 20 percent

  Scenario: Generate dataset without anomalies
    Given a pharma simulator
    When I generate a dataset with 100 samples without anomalies
    Then no rows are labeled as anomalies

  Scenario: Dataset rows contain all output fields
    Given a pulp simulator
    When I generate a dataset with 5 samples
    Then each row contains all expected output fields

  Scenario: CSV format has header plus data rows
    Given a rotating simulator
    When I generate a dataset with 10 samples
    And I convert the dataset to CSV
    Then the CSV has 11 lines
    And the first line is a header row

  Scenario: Dataset shows cumulative degradation on refinery
    Given a refinery simulator
    When I generate a dataset with 10 samples
    Then catalystLevel decreases progressively across rows

  Scenario: Dataset totalProcessed accumulates across rows
    Given a refinery simulator
    When I generate a dataset with 5 samples
    Then totalProcessed increases across all rows

  Scenario: Dataset timestamps are sequential
    Given a chemical simulator
    When I generate a dataset with 10 samples
    Then timestamps increment by exactly 1 each row
