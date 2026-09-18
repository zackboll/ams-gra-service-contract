# Repository Bootstrap and Publication Guide

The downloadable scaffold is intentionally a normal source tree without a required Git history. The following sequence creates a clean repository and initial commit.

## 1. Initialize Git

```bash
git init -b main
git add .
git status
git commit -m "Bootstrap machine-readable AMS GRA service contract specification"
```

Before committing, run:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
make check
```

## 2. Suggested GitHub repository metadata

**Repository name**

```text
ams-gra-service-contract
```

**Suggested description**

```text
Experimental language-neutral machine-readable companion format for OMS Service Contracts in AMS GRA-oriented code-generation toolchains.
```

**Suggested topics**

```text
ams-gra
open-mission-systems
oms
uci
code-generation
json-schema
yaml
service-contract
open-architecture
```

Do not describe the repository as an official AMS GRA/OMS/UCI standard.

## 3. Create a GitHub repository with `gh`

For a personal public repository:

```bash
gh repo create ams-gra-service-contract \
  --public \
  --source=. \
  --remote=origin \
  --push
```

For an organization-owned repository, specify the full owner/name:

```bash
gh repo create OWNER/ams-gra-service-contract \
  --public \
  --source=. \
  --remote=origin \
  --push
```

Choose visibility according to the intended project policy. The upstream references in this scaffold are all public, but that does not require this derivative project to be public.

## 4. Recommended branch workflow

Keep `main` releasable and use short-lived branches for specification changes, for example:

```text
task/001-bootstrap-contract-spec
task/002-uci-resolver-conformance
task/003-data-transfer-refinement
```

A schema/semantic pull request should normally include:

1. rationale;
2. upstream source/reference when applicable;
3. schema changes;
4. semantic documentation changes;
5. valid/invalid fixtures;
6. changelog entry; and
7. passing `make check`.

## 5. Recommended GitHub protections

After the first push, consider:

- require pull requests for `main`;
- require the `contract-conformance` GitHub Actions job;
- require branches to be current before merge;
- disallow force-pushes to `main`;
- require review for contract-language semantic changes; and
- enable Dependabot/security updates if desired for validator dependencies.

For a one-person experimental repository, these can be introduced incrementally rather than blocking early iteration.

## 6. First tag

The contract language is explicitly experimental. After the initial repository review, a reasonable first tag is:

```bash
git tag -a v0.1.0 -m "Machine-readable Service Contract specification v0.1.0"
git push origin v0.1.0
```

The **Git tag** (`v0.1.0`) identifies a release of this repository. The **contract document field** remains:

```yaml
contract_version: "0.1"
```

That separation allows patch releases of documentation/validator tooling without changing the contract grammar.

## 7. Suggested next engineering task

The next repository should not immediately add language-specific code. First exercise this schema against several real or representative OMS Service Contracts and record gaps.

A good next task is:

```text
Validate v0.1 against three distinct OMS Service Contract function shapes:
1. Service Status,
2. a command/request + status-response function,
3. a function containing Data Transfer or Non-OMS exchange data.

For each, document any information loss or ambiguity. Do not expand the
schema unless the missing field is required for deterministic generation
or round-trip traceability.
```

Once that exercise is stable, add contract-aware resolution to the code-generator project rather than embedding a UCI parser into this specification repository.
