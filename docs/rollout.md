# Rolling out safely

Hardening touches the three things that can lock you out of a server: SSH,
the firewall and accounts. Treat a first rollout like a schema migration:
preview, canary, then batches.

## 0. Before the first run

- Put real public keys in `users_admins`. Password login is disabled by
  `ssh_hardening`, so a typo in a key means no access.
- Make sure the account Ansible connects as is listed in `users_admins` and
  keeps `ssh_access: true`. `AllowGroups sshusers` rejects everyone else.
- Put the management network in `firewall_allow` before the default policy
  flips to deny. The role adds allow rules first and enables the firewall last,
  but a missing allow rule still cuts you off.
- Keep an out-of-band path (cloud serial console, IPMI, hypervisor console) for
  the canary host.

## 1. Preview with check mode and diff

```bash
ansible-playbook site.yml --check --diff --limit canary
```

Check mode runs every task without changing the host and `--diff` shows the
exact file changes (sshd_config, sysctl drop-in, audit rules, sudoers). Tasks
that only read state (`ssh -Q`, fact gathering) still run, so algorithm
filtering in the preview matches the real run.

Review the diff for `/etc/ssh/sshd_config` in particular: `AllowGroups`,
`PermitRootLogin` and `PasswordAuthentication`.

## 2. Canary

```bash
ansible-playbook site.yml --limit canary
```

Then, from a new terminal (keep the current session open):

```bash
ssh ops@web-01.example.internal 'sudo -n true && echo sudo-ok'
```

`sshd` is only restarted after `sshd -t` accepts the new file, so a syntax
error never takes the daemon down, but only a fresh login proves that keys,
`AllowGroups` and the firewall agree.

## 3. Batches

`serial` and `max_fail_percentage` are play level settings, so pass them as
extra vars:

```bash
# 10% of hosts at a time, stop the whole rollout on the first failed host
ansible-playbook site.yml -e rollout_serial=10% -e rollout_max_fail_percentage=0

# or a fixed ramp: 1 host, then 5, then 25% of the remainder per batch
ansible-playbook site.yml -e '{"rollout_serial": [1, 5, "25%"]}'
```

With `rollout_max_fail_percentage=0` a single failed host stops later batches,
so a bad change reaches at most one batch.

## 4. Narrow the blast radius

| Need | Command |
| --- | --- |
| One group | `--limit web` |
| One host | `--limit web-02.example.internal` |
| One control only | `--tags ssh`, `--tags firewall`, `--tags kernel`, `--tags audit` |
| Everything except one control | `--skip-tags audit` |
| Different target pattern | `-e target_hosts=db` |

## 5. Things that need a reboot or a second look

- **auditd immutable mode** (`-e 2`): rules cannot be changed until the next
  reboot. Set `audit_rules_immutable: false` while you tune rules, then turn it
  back on.
- **Kernel module blacklist**: already loaded modules stay loaded until reboot.
- **sysctl**: applied live and persisted in `/etc/sysctl.d/60-hardening.conf`.
  If a host is a router or runs containers that need forwarding, override
  `net.ipv4.ip_forward` through `kernel_hardening_extra_sysctls`.
- **Drop-ins in `/etc/ssh/sshd_config.d/`** are deliberately not included any
  more. Move anything you still need into role variables.

## 6. Rolling back

Every managed file is a template, so the normal rollback is to change the
variable and run the same play again with `--limit` on the affected hosts.

For SSH there is also a console path: `ssh_hardening_backup` (on by default)
keeps the previous file as `/etc/ssh/sshd_config.<pid>.<timestamp>~`.

```bash
ls -t /etc/ssh/sshd_config.*~ | head -1          # newest backup
cp "$(ls -t /etc/ssh/sshd_config.*~ | head -1)" /etc/ssh/sshd_config
sshd -t && systemctl restart ssh                  # sshd on the RHEL family
```
