Feature: graph rendering

  Scenario: Render a graph
    Given I run the command "cat test/data/*.ttl | staticld -f turtle test/templates test/output"
    Then the rendered files at "test/output" should match the files at "test/fixture"

