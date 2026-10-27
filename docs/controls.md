# Controls and CIS mapping

Each row is one control the roles enforce. IDs follow the **CIS Ubuntu Linux
24.04 LTS Benchmark v1.0.0** numbering; the CIS Debian and RHEL 9 benchmarks
contain the same recommendations under different numbers, so the title is the
reliable key when you map to another benchmark.

"Verified" says how CI proves the control after converge:

- **live**: checked against the running system (`sshd -T`, `sysctl -n`,
  `ufw status`, `firewall-cmd`, systemd state, HTTP request, real SSH login)
- **file**: checked in the rendered configuration file
- **lint**: enforced at template time (`sshd -t`, `visudo -c`) and by idempotence

## base

| # | Control | CIS | Verified |
| --- | --- | --- | --- |
| 1 | NIS, rsh, talk, telnet and ftp clients are not installed | 2.2.1 - 2.2.4, 2.2.6 | lint |
| 2 | A single time daemon (chrony) is installed, enabled and running | 2.3.1.1, 2.3.3.x | live |
| 3 | chrony is configured with the authorised pools and acts as a client only | 2.3.3.1 | file |
| 4 | Security updates install automatically (unattended-upgrades / dnf-automatic) | 1.2.2.1 | file / live |
| 5 | journald stores logs persistently and compresses them | 6.1.1.1.x | file |
| 6 | journald disk usage and retention are bounded | 6.1.1.1.x | file |
| 7 | Local and remote login banners are set (`/etc/issue`, `/etc/motd`) | 1.6.1, 1.6.2 | lint |
| 8 | Time zone is set consistently across the fleet | n/a (operational) | lint |

## users

| # | Control | CIS | Verified |
| --- | --- | --- | --- |
| 9 | Named admin accounts with SSH keys; authorized_keys managed exclusively | 5.1.4 | live (key login) |
| 10 | sudo is installed | 5.2.1 | live |
| 11 | sudo uses a pseudo terminal (`Defaults use_pty`) | 5.2.2 | file |
| 12 | sudo writes its own log file | 5.2.3 | file |
| 13 | sudo requires a password unless `sudo_nopasswd` is set per user | 5.2.4 | live (`sudo -n` refused for opsadmin, allowed for deploy) |
| 14 | sudo authentication timeout is limited | 5.2.6 | file |
| 15 | sudo rules are validated with `visudo -cf` before they are installed | 5.2.x | lint |
| 16 | root password is locked | 5.4.2.4 | live (`/etc/shadow`) |
| 17 | Password maximum age (`PASS_MAX_DAYS`) | 5.4.1.1 | lint |
| 18 | Password minimum age (`PASS_MIN_DAYS`) | 5.4.1.2 | lint |
| 19 | Password expiry warning (`PASS_WARN_AGE`) | 5.4.1.3 | lint |
| 20 | Default user umask is 027 | 5.4.3.3 | lint |
| 21 | Password quality: minimum length 14, all character classes, dictionary check | 5.3.3.2.x | lint |

## ssh_hardening

| # | Control | CIS | Verified |
| --- | --- | --- | --- |
| 22 | `sshd_config` owned by root, mode 0600 | 5.1.1 | live |
| 23 | Host private keys are mode 0600 | 5.1.2 | lint |
| 24 | Access limited with `AllowGroups` | 5.1.4 | live (user outside the group is rejected) |
| 25 | Warning banner (`Banner /etc/issue.net`) | 5.1.5 | live (`sshd -T`) |
| 26 | Only strong ciphers (AEAD and CTR, no CBC) | 5.1.6 | live (`sshd -T`, CBC handshake refused) |
| 27 | Idle timeout (`ClientAliveInterval` / `ClientAliveCountMax`) | 5.1.7 | live |
| 28 | X11, TCP, agent and stream-local forwarding disabled | 5.1.8 | live |
| 29 | GSSAPI authentication disabled | 5.1.9 | file |
| 30 | Host based authentication disabled | 5.1.10 | live |
| 31 | `IgnoreRhosts yes` | 5.1.11 | live |
| 32 | Only strong key exchange algorithms (no SHA-1 groups) | 5.1.12 | live |
| 33 | `LoginGraceTime` 60 s | 5.1.13 | live |
| 34 | `LogLevel VERBOSE` | 5.1.14 | live |
| 35 | Only encrypt-then-MAC SHA-2 MACs | 5.1.15 | live |
| 36 | `MaxAuthTries` 3 | 5.1.16 | live |
| 37 | `MaxSessions` 4 | 5.1.17 | file |
| 38 | `MaxStartups 10:30:60` | 5.1.18 | file |
| 39 | `PermitEmptyPasswords no` | 5.1.19 | live |
| 40 | `PermitRootLogin no` | 5.1.20 | live (root login rejected) |
| 41 | `PermitUserEnvironment no` | 5.1.21 | live |
| 42 | `UsePAM yes` | 5.1.22 | live |
| 43 | Password and keyboard-interactive authentication disabled | 5.1.x (key-only) | live (server offers `publickey` only) |
| 44 | New config validated with `sshd -t` before the file is replaced and again before restart | n/a (safe change) | lint |
| 45 | Vendor and cloud-init drop-ins cannot weaken the config (no `Include`) | n/a (drift) | file |

## firewall

| # | Control | CIS | Verified |
| --- | --- | --- | --- |
| 46 | A single firewall is installed (ufw on Debian/Ubuntu, firewalld on EL) | 4.1.1 / RHEL 4.1.x | live |
| 47 | The firewall service is enabled and active | 4.1.3 | live |
| 48 | Default deny for inbound and routed traffic | 4.1.7 | live (`ufw status verbose`, firewalld target `DROP`) |
| 49 | Explicit allow rules for each open port, optionally per source CIDR | 4.1.6 | live |
| 50 | Unused default services (cockpit, dhcpv6-client) removed on firewalld | RHEL 4.x | live |
| 51 | Firewall logging enabled (ufw) | 4.1.x | file |

## kernel_hardening

| # | Control | CIS | Verified |
| --- | --- | --- | --- |
| 52 | IP forwarding disabled (IPv4 and IPv6) | 3.3.1 | live (`sysctl -n`) |
| 53 | Packet redirect sending disabled | 3.3.2 | live |
| 54 | Bogus ICMP responses ignored | 3.3.3 | live |
| 55 | Broadcast ICMP requests ignored | 3.3.4 | live |
| 56 | ICMP redirects not accepted (IPv4 and IPv6) | 3.3.5 | live |
| 57 | Secure ICMP redirects not accepted | 3.3.6 | live |
| 58 | Reverse path filtering enabled | 3.3.7 | live |
| 59 | Source routed packets not accepted | 3.3.8 | live |
| 60 | Suspicious packets (martians) logged | 3.3.9 | live |
| 61 | TCP SYN cookies enabled | 3.3.10 | live |
| 62 | IPv6 router advertisements not accepted | 3.3.11 | live |
| 63 | ASLR enabled (`kernel.randomize_va_space = 2`) | 1.5.1 | live |
| 64 | ptrace restricted (`kernel.yama.ptrace_scope = 1`) | 1.5.2 | live |
| 65 | Core dumps restricted (`fs.suid_dumpable`, limits.conf, systemd-coredump) | 1.5.3 | live / file |
| 66 | Kernel pointer and dmesg restrictions, SysRq off, unprivileged BPF off, line discipline autoload off | n/a (KSPP) | live |
| 67 | Protected hardlinks, symlinks, FIFOs and regular files | n/a (KSPP) | live |
| 68 | Unused filesystems cannot be loaded: cramfs, freevxfs, hfs, hfsplus, jffs2, udf | 1.1.1.1 - 1.1.1.8 | file |
| 69 | usb-storage cannot be loaded | 1.1.1.x | file |
| 70 | Uncommon network protocols cannot be loaded: dccp, sctp, rds, tipc | 3.2.1 - 3.2.4 | file |

## audit

| # | Control | CIS | Verified |
| --- | --- | --- | --- |
| 71 | auditd is installed and enabled | 6.2.1.1, 6.2.1.2 | lint |
| 72 | Audit backlog limit is sufficient | 6.2.1.4 | file |
| 73 | Audit log size, rotation and retention configured | 6.2.2.1, 6.2.2.2 | file |
| 74 | System behaviour when audit storage fills up | 6.2.2.3, 6.2.2.4 | file |
| 75 | Changes to sudoers are collected (`scope`) | 6.2.3.1 | file (compiled rules) |
| 76 | Actions as another user are collected (`user_emulation`) | 6.2.3.2 | file |
| 77 | Changes to the sudo log are collected | 6.2.3.3 | file |
| 78 | Date and time changes are collected | 6.2.3.4 | file |
| 79 | Network environment changes are collected | 6.2.3.5 | file |
| 80 | Unsuccessful file access attempts are collected | 6.2.3.7 | file |
| 81 | User and group identity changes are collected | 6.2.3.8 | file |
| 82 | Permission and ownership changes are collected | 6.2.3.9 | file |
| 83 | Successful mounts are collected | 6.2.3.10 | file |
| 84 | Session initiation is collected | 6.2.3.11 | file |
| 85 | Login and logout events are collected | 6.2.3.12 | file |
| 86 | File deletion by users is collected | 6.2.3.13 | file |
| 87 | MAC policy changes (AppArmor / SELinux) are collected | 6.2.3.14 | file |
| 88 | `usermod` use is collected | 6.2.3.18 | file |
| 89 | Kernel module loading and unloading is collected | 6.2.3.19 | file |
| 90 | Audit configuration is immutable (`-e 2`) | 6.2.3.20 | file |

## fail2ban and monitoring

| # | Control | CIS | Verified |
| --- | --- | --- | --- |
| 91 | Brute force protection for sshd with incremental ban times (fail2ban, systemd backend) | n/a (defence in depth) | live (`fail2ban-client status sshd`) |
| 92 | Host metrics exported by node_exporter, binary checksum verified, sandboxed systemd unit | n/a (observability) | live (`/metrics`) |

## What containers cannot prove

Molecule runs each distribution in a privileged, systemd enabled container.
That is close to a VM, with two honest exceptions:

- **auditd rules are compiled but not loaded.** The kernel audit subsystem only
  accepts rules from the initial PID namespace, so `auditctl -l` cannot work in a
  container. CI asserts the compiled `/etc/audit/audit.rules` instead, and the
  verify playbook checks `auditctl -l` automatically when it runs against a VM.
- **Non-namespaced sysctls** (`kernel.*`, `fs.*`) are written to the CI
  runner's kernel. That is harmless on a throwaway runner and is what lets CI
  read the live values back.

Bootloader settings (GRUB password, `audit=1`, AppArmor/SELinux enforcement) and
separate partitions for `/tmp`, `/var` and `/home` are out of scope: they belong
to image building or provisioning, not configuration management of running
hosts.
