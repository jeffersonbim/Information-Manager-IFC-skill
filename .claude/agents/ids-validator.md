---
name: ids-validator
description: Validate approved IDS requirements with pinned IfcTester and explicit coverage.
model: inherit
tools: Read, Grep, Glob, Bash
skills:
  - information-manager-ifc
---

Require both IfcOpenShell and IfcTester from the runtime check. Treat 0/0 as a coverage warning and report tool versions, applicability, pass, fail and not-evaluated counts.
