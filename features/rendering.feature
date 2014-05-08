Feature: graph rendering

  Scenario: Render a graph
    Given I run the command "cat test/data/*.ttl | static-ld -f turtle -t test/templates -o test/output"
    Then the rendered files at "test/output" should match the files at "test/fixture"

