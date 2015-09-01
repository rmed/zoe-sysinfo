# zoe-sysinfo ![Agent version](https://img.shields.io/badge/Zoe_Agent-0.3.2-blue.svg "Zoe sysinfo")

System and usage information gathering for Zoe


## Funtionality

Right now, the agent obtains information on:

- CPU usage (per CPU in system)
- Disk usage and relevant information (per partition)
- Memory usage (RAM and SWAP)
- Running processes information (only in complete report)

This information is asked for through jabber or Telegram. A report in HTML can
also be generated and sent through email.
