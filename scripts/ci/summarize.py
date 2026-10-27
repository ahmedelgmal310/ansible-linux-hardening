#!/usr/bin/env python3
"""Turn Molecule logs and Lynis reports into CI evidence.

summarize.py distro <name> <results-dir>
    Parse converge/idempotence/verify logs and the before/after Lynis reports
    of one matrix job, write <results-dir>/<name>.json and print a Markdown
    section for the job summary.

summarize.py fleet <results-dir>
    Combine every <name>.json into one Markdown table.
"""

import json
import re
import sys
from pathlib import Path

RECAP = re.compile(
    r"^instance\s*:\s*ok=(?P<ok>\d+)\s+changed=(?P<changed>\d+)\s+unreachable=(?P<unreachable>\d+)"
    r"\s+failed=(?P<failed>\d+)\s+skipped=(?P<skipped>\d+)",
    re.MULTILINE,
)
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def recap(path: Path) -> dict:
    """Return the last PLAY RECAP line for the instance."""
    text = ANSI.sub("", path.read_text(errors="replace"))
    matches = list(RECAP.finditer(text))
    if matches:
        return {k: int(v) for k, v in matches[-1].groupdict().items()}
    # `molecule idempotence` only prints the play output when it fails; this
    # script runs after that step succeeded, so a clean log means 0 changes.
    if "idempotence" in path.name and "Idempotence completed successfully" in text:
        return {"ok": 0, "changed": 0, "unreachable": 0, "failed": 0, "skipped": 0}
    raise SystemExit(f"no PLAY RECAP for 'instance' in {path}")


def lynis(path: Path) -> dict:
    data = {"warnings": 0, "suggestions": 0}
    for line in path.read_text(errors="replace").splitlines():
        key, _, value = line.partition("=")
        if key == "hardening_index":
            data["hardening_index"] = int(value)
        elif key == "lynis_tests_done":
            data["tests"] = int(value)
        elif key == "warning[]":
            data["warnings"] += 1
        elif key == "suggestion[]":
            data["suggestions"] += 1
        elif key == "os_fullname":
            data["os"] = value
    return data


def distro(name: str, results: Path) -> None:
    converge = recap(results / "converge.log")
    idempotence = recap(results / "idempotence.log")
    verify = recap(results / "verify.log")
    before = lynis(results / "lynis-before.dat")
    after = lynis(results / "lynis-after.dat")
    summary = {
        "distro": name,
        "os": after.get("os", name),
        "converge": converge,
        "idempotence": idempotence,
        "verify": verify,
        "lynis_before": before,
        "lynis_after": after,
    }
    (results / f"{name}.json").write_text(json.dumps(summary, indent=2) + "\n")

    delta = after["hardening_index"] - before["hardening_index"]
    print(f"### {summary['os']} ({name})\n")
    print("| Check | Result |")
    print("| --- | --- |")
    print(f"| Converge | {converge['ok']} tasks ok, {converge['changed']} changed, {converge['failed']} failed |")
    print(f"| Idempotence (second run) | **{idempotence['changed']} changed**, {idempotence['failed']} failed |")
    print(f"| Verify | {verify['ok']} checks passed, {verify['failed']} failed |")
    print(
        f"| Lynis hardening index | {before['hardening_index']} -> **{after['hardening_index']}** "
        f"({delta:+d}) |"
    )
    print(f"| Lynis warnings | {before['warnings']} -> {after['warnings']} |")
    print(f"| Lynis suggestions | {before['suggestions']} -> {after['suggestions']} |")
    print()


def fleet(results: Path) -> None:
    rows = [json.loads(p.read_text()) for p in sorted(results.rglob("*.json"))]
    if not rows:
        raise SystemExit(f"no results under {results}")
    print("## Fleet hardening results\n")
    print("| Distribution | Converge changes | Idempotence changes | Verify checks | Lynis before | Lynis after |")
    print("| --- | ---: | ---: | ---: | ---: | ---: |")
    for r in rows:
        print(
            f"| {r['os']} | {r['converge']['changed']} | {r['idempotence']['changed']} | "
            f"{r['verify']['ok']} | {r['lynis_before']['hardening_index']} | "
            f"{r['lynis_after']['hardening_index']} |"
        )
    print()
    idem_clean = sum(1 for r in rows if r["idempotence"]["changed"] == 0)
    print(f"Idempotence: {idem_clean}/{len(rows)} distributions reported 0 changes on the second run.")


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "distro":
        distro(sys.argv[2], Path(sys.argv[3]))
    elif len(sys.argv) == 3 and sys.argv[1] == "fleet":
        fleet(Path(sys.argv[2]))
    else:
        raise SystemExit(__doc__)
