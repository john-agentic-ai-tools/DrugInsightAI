---
name: "User Story"
description: "Create a new user story to describe a feature or enhancement"
title: "[User Story] <short summary>"
labels: ["user story", "enhancement"]
assignees: []
---

body:

- type: textarea
    id: description
    attributes:
      label: User Story
      description: As a [type of user], I want [some goal], so that [some reason].
      placeholder: |
        Example:
        As a researcher,
        I want to export drug interaction data,
        So that I can run offline analysis in R.
    validations:
      required: true

- type: textarea
    id: acceptance-criteria
    attributes:
      label: Acceptance Criteria
      description: Conditions that must be met for this story to be considered complete.
      placeholder: |
        - [ ] Data export works in CSV format
        - [ ] API endpoint documented
        - [ ] Unit tests cover at least 80% of code
    validations:
      required: true

- type: textarea
    id: notes
    attributes:
      label: Additional Notes
      description: Any design considerations, dependencies, or related issues.
      placeholder: |
        - Relates to #42
        - Requires authentication
