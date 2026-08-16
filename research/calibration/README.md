# Watchdog Calibration Evidence

This directory contains privacy-safe watchdog reports and complete human-review labels derived from real live trajectories. Raw agent messages, command output, prompts, and private workspaces remain under ignored `.agentic-runs/` storage.

Each calibration manifest binds labels to exact watchdog report fingerprints. Cases are evidence for calibration only: they cannot enable advice or intervention, and eligibility still requires the declared minimum support, precision, and recall.

Current datasets:

- [`representative-sentinel-001/`](representative-sentinel-001/): two real multi-file sentinel cases plus their deterministic calibration report. Both `premature_patching` alerts are contextually labelled false positives because the declared workflows test after implementation and independent evaluation passed every required and protected check.
