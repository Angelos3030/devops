"""Lead Scoring pilot — real (non-mocked) staging-track implementation.

Builds on the isolated pilot in research/langgraph-poc/lead-scoring/ (see
docs/adr/0002-lead-scoring-langgraph-pilot.md, Accepted). This package uses
real DeepSeek/Claude calls and the real Agency Kernel registry tables in
staging, but deliberately does NOT enable an installation (see
kernel_registry.py) and does NOT connect a real CRM — those remain separate,
explicitly-approved steps.

Every entrypoint in this package calls `src.env.require(env.DEV, env.STAGING)`
before touching the database, using the project's own existing environment
guard rather than a bespoke one.
"""
