"""
Dream Radar — data-build package.

Scaffold status (see docs/dream-radar-spec.md and docs/radar-scoring-handoff.md):

  IMPLEMENTED, real logic:
    - config.py    travel heuristic thresholds (editable, per spec section 6)
    - travel.py    distance / mode / timezone / hotel computation
    - fixtures.py  fixture modelling + certainty tiering

  STUBBED, interface only — needs live data source integration:
    - climate.py
    - load.py
    - player_bio.py
    - international.py

  STUBBED, needs the Opus scoring session (docs/radar-scoring-handoff.md):
    - fuelling_risk.py

  WORKING END TO END on example/mock data:
    - build.py     orchestrates the above into NamedDecision objects
"""
