# Security Policy

## Supported Versions

DataGuard AI is currently a public beta. Security fixes are provided for the latest released version.

| Version | Supported |
| ------- | --------- |
| 0.2.1    | Yes       |
| <= 0.2.0 | No        |

## Reporting a Vulnerability

Please do not open a public GitHub issue for a suspected security vulnerability.

Report vulnerabilities privately through GitHub's **Private vulnerability reporting** feature for this repository.

When reporting a vulnerability, please include, when possible:

- A description of the issue and its potential impact
- Steps to reproduce the issue
- The affected DataGuard AI version
- Relevant configuration or environment details
- A minimal proof of concept, if appropriate
- Any suggested mitigation or remediation

Please do not include credentials, API keys, secrets, production records, or sensitive personal data in vulnerability reports.

Security reports will be reviewed as time permits. Confirmed vulnerabilities will be addressed based on severity, impact, and available maintainer resources.

Please allow a reasonable period for investigation and remediation before publicly disclosing a reported vulnerability.

## Data Handling and Privacy

The core DataGuard AI scanner runs locally and does not require an LLM.

Optional AI-assisted functionality may send structured findings to an external AI provider. The included OpenAI provider removes sampled raw values before transmission. Users should nevertheless review the information being transmitted and ensure that use of external providers complies with their organization's security, privacy, contractual, and regulatory requirements.

DataGuard AI should not be treated as a substitute for an organization's security, privacy, compliance, or data-governance controls.

## Security Best Practices

When using DataGuard AI:

- Do not commit credentials, API keys, or secrets to configuration files.
- Avoid using production datasets when a representative test dataset is sufficient.
- Review generated reports before sharing them because findings or metadata may contain sensitive information.
- Keep DataGuard AI and its dependencies up to date.
- Review optional integrations before enabling them in production environments.
