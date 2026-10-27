# Security policy

## Supported versions

Only the `main` branch is maintained. Fixes are not backported to tags.

## Reporting a vulnerability

Please do not open a public issue for security problems. Use GitHub's
[private vulnerability reporting](https://github.com/ahmedelgmal310/ansible-linux-hardening/security/advisories/new)
for this repository instead.

Include the affected role, the distribution and version, and steps to
reproduce. You can expect an acknowledgement within 5 working days.

Reports are in scope when a role:

- leaves a host less secure than its documented control says (for example a
  setting that is not applied or is silently reverted),
- exposes credentials or key material, or
- can lock operators out of a host when used as documented.

## Hardening caveats

These roles change SSH, firewall and account settings. Always roll out with
check mode and a canary group first, as described in
[docs/rollout.md](docs/rollout.md).
