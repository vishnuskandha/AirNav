# Security Policy

## Supported Versions

Security fixes are applied to the `main` branch. AirNav is a personal/educational
project; no backport releases are maintained.

## Reporting a Vulnerability

If you find a security issue, please report it privately by opening a
[security advisory](https://github.com/vishnuskandha/AirNav/security/advisories)
or by emailing the maintainer. Do not open a public issue for vulnerabilities
that involve credentials or remote code execution.

Please include:

- A description of the issue and the affected components.
- Steps to reproduce (if applicable).
- The impact you observed.

We will acknowledge reports within 7 days and aim to release a fix on `main`
as soon as it is verified.

## Known Notes

- AirNav controls the mouse pointer (via `pynput`) based on webcam hand
  tracking. It is input software only and does not transmit any data; camera
  frames are processed locally and never leave the machine.
- The camera feed and hand landmarks are displayed in the picture-in-picture
  overlay. Do not run AirNav unattended in a shared or public workspace if
  camera visibility is a concern.
- Mouse-control software can interfere with normal operation of the host.
  Only run AirNav when you intend to use gesture control, and stop it with
  `Ctrl+C` when done.
- No secrets or credentials are stored by the application. If you add
  authentication or network features in a fork, keep secrets out of the
  repository and out of version control.
