RESULTS = []


def pytest_runtest_logreport(report):
    if report.when == "call":
        RESULTS.append((report.nodeid.split("::")[-1], report.outcome, round(report.duration, 2)))


def pytest_sessionfinish(session, exitstatus):
    passed = sum(1 for r in RESULTS if r[1] == "passed")
    lines = [
        "# MedAssist AI - Test and Performance Report",
        "",
        f"Total: {len(RESULTS)} | Passed: {passed} | Failed: {len(RESULTS) - passed}",
        "",
        "| Test | Result | Time (s) |",
        "|---|---|---|",
    ]
    for name, outcome, secs in RESULTS:
        lines.append(f"| {name} | {outcome.upper()} | {secs} |")
    with open("test_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))