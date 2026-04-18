Feature: Simulation Dashboard
  As a data engineer
  I want to run industrial process simulations
  So that I can generate realistic sensor data for AI/ML training

  Scenario: User selects a simulator and starts a simulation
    Given I am on the dashboard page
    When I select the "Chemical Reactor" simulator
    And I click the "Start" button
    Then the simulation should be running
    And live chart data should appear
    When I click the "Stop" button
    Then the simulation should be stopped

  Scenario: User selects each simulator type
    Given I am on the dashboard page
    Then I should see all 5 simulator cards
    When I select the "Refinery Distillation" simulator
    Then the parameter panel should show refinery parameters
    When I select the "Pulp Digester" simulator
    Then the parameter panel should show pulp parameters
    When I select the "Rotating Equipment" simulator
    Then the anomaly panel should be visible

  Scenario: Real-time chart updates with simulation data
    Given I am on the dashboard page
    When I click the "Start" button
    And I wait for simulation data
    Then the statistics panel should show computed values
    When I click the "Stop" button
    Then the chart data should be preserved

  Scenario: User resets the simulation
    Given I am on the dashboard page
    When I click the "Start" button
    And I wait for simulation data
    And I click the "Stop" button
    And I click the "Reset" button
    Then the chart should show no data
    And the statistics should show no data
