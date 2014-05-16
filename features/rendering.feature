Feature: graph rendering

  Scenario: Render a graph
    Given I have an empty directory at "test/output"
    When I run the command "cat test/data/*.ttl | staticld -f turtle test/templates/ test/output/"
    Then the rendered files at "test/output" should match the files at "test/expected"

  Scenario: Template detection
    Given I have an empty directory at "test/output"
    When I run the command "cat test/data/withoutTemplateClass/*.ttl | staticld -f turtle test/templates/ test/output/"
    Then the rendered files at "test/output" should match the files at "test/expected"

