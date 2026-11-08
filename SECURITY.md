# Security policy

The latest release is the supported version. This repository contains agent instructions and static examples, not an authentication or financial service. A skill does not sandbox an agent or grant permissions. Review downloaded changes and keep your coding agent’s normal approval controls enabled.

## Report privately

For a security vulnerability, use **Security → Report a vulnerability** in this repository when GitHub private vulnerability reporting is available. Otherwise use GitHub’s private reporting controls for exposed secrets or harmful content. Do not post exploit details, secrets, personal data or private application code in a public issue. Non-sensitive questions about reporting availability can be raised publicly without vulnerability details.

Include affected version/file, a synthetic reproduction, expected versus observed behaviour and impact. We will investigate and coordinate a fix; no guaranteed response time or bounty is offered.

Security-relevant examples include instructions that leak project data, silently grant external-action authority, install untrusted source, or bypass target-repository controls. Ordinary visual bugs belong in an issue.

CI runs without production credentials. Browser fixtures make no backend requests. Fork pull requests receive read-only workflow permissions; publishing runs only from the main branch after validation.
