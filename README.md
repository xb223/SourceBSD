# SourceBSD

A FreeBSD fork targeting servers and homelabs. Focused on security, privacy, and simplicity. No cloud account. No phone-home. No telemetry.

## What is SourceBSD

SourceBSD is a hardened FreeBSD system with automatic jail isolation, a web control panel, and built-in security tools. Every service runs in its own isolated jail automatically. The system is manageable entirely from the command line or through a browser.

## Current Status

In active development. All core features are working on FreeBSD 14.4.

## Features

- Automatic jail-per-service isolation using FreeBSD jails
- srcwatch behavioral anomaly detection using rctl
- srcveil per-jail privacy profiles
- srcbackup with automatic restore testing
- SourcePanel web control plane
- srcharden host hardening levels 1-5
- srcaudit network exposure and security audit
- Key-only SSH enforced
- ZFS for all storage

## Commands

### srcctl
srcctl status - Show full system health

### srcjail
srcjail create <name> --profile <profile> - Create jail with auto-boot
srcjail list - List all jails with status
srcjail start <name> - Start a jail
srcjail stop <name> - Stop a jail
srcjail destroy <name> - Remove a jail

### srcwatch
srcwatch start - Build baselines using rctl
srcwatch score - Show real per-jail anomaly scores
srcwatch tail - Stream live anomaly log
srcwatch check <jail> - Detailed rctl data for one jail

### srcveil
srcveil apply <jail> --profile <profile> - Apply privacy profile
srcveil status - Show all veiled jails
srcveil remove <jail> - Remove veil from jail
Profiles: personal-cloud, no-log, analytics-block, minimal-trace

### srcbackup
srcbackup backup <jail> - Back up a jail
srcbackup backup --all - Back up all jails
srcbackup test <jail> - Test restore from latest backup
srcbackup list - List all backups with test status

### srcaudit
srcaudit expose - Show all open ports and exposure status
srcaudit check - Full security audit with fix suggestions
srcaudit tail - Stream live audit log

### srcharden
srcharden check - Show current hardening status
srcharden apply --level <n> - Apply hardening level 1-5
srcharden revert - Remove all hardening settings
Levels: 1=Basic 2=SSH 3=Network 4=Process 5=Maximum

### srcpol
srcpol compile <policy.sp> - Compile policy into pf + rctl + jail config
srcpol verify <policy.sp> - Dry run show what policy would enforce
srcpol apply <jail> - Apply compiled policy to running jail
srcpol diff <old> <new> - Show changes between two policies

## Jail Profiles

web - 50% CPU, 512MB RAM, network yes - nginx web servers
database - 70% CPU, 1024MB RAM, network no - PostgreSQL MySQL
cache - 30% CPU, 256MB RAM, network no - Redis Memcached
bastion - 20% CPU, 128MB RAM, network yes - SSH jump host

## SourcePanel

Web control plane at http://host:8080
Sections: CPU, Memory, Network, Storage, Jails, Security
Auto-starts with the testweb jail.
Reads real kernel data via FreeBSD sysctls and rctl.

## Requirements

FreeBSD 14.4 or later
ZFS root filesystem
kern.racct.enable=1 in /boot/loader.conf
2GB RAM minimum, 4GB recommended
20GB disk minimum

## License

BSD 2-Clause License
