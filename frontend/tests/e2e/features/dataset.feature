Feature: Dataset Management
  As a data engineer
  I want to generate and manage datasets
  So that I can download simulation data for ML training

  Scenario: User navigates to datasets page
    Given I am on the dashboard page
    When I click the "Datasets" navigation link
    Then I should see the datasets page title
    And I should see the generate dataset form

  Scenario: Navigation between pages
    Given I am on the dashboard page
    When I click the "Datasets" navigation link
    Then I should see the datasets page title
    When I click the "Dashboard" navigation link
    Then I should see the simulation dashboard
