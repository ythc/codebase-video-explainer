# Codebase analysis workflow

Use this reference while constructing `project-analysis.json`.

## Goal

Build a compact, evidence-backed mental model that is good enough to teach another developer. The analysis should answer how the program starts, which components own the main responsibilities, how data and control move, where external boundaries exist, and where a developer should make common changes.

## Pass 1: Orientation

Read, in this order when present:

1. Root README and docs index.
2. Package/build manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, Gradle/Maven files, workspace manifests).
3. Container/deployment files (`Dockerfile`, compose files, deployment configs, worker/serverless configs).
4. Framework configuration and environment examples.
5. Entrypoints and bootstrapping code.

Use `scan.json` and `project-manifest.json` to decide where to look next rather than opening every file.

## Pass 2: Module boundaries

Group source files into responsibilities such as:

- UI / routes / controllers
- application or domain logic
- service/integration clients
- persistence/data access
- auth/security
- queues/jobs/events
- platform/deployment glue
- shared utilities

For each module record:

- purpose
- public entry files or symbols
- dependencies on other modules
- external systems touched
- evidence paths

Avoid treating a directory name as proof of responsibility. Verify with imports, registrations, routes, constructors, call sites, or tests.

## Pass 3: Representative execution paths

Choose 1–3 flows that teach the system better than a file-by-file tour. Good candidates include:

- application startup
- an HTTP/API request
- authentication/login
- database read/write
- an AI/model request
- background job or queue message
- WebSocket/event flow
- a primary user interaction

Trace each flow from trigger to final side effect. For every step capture:

- file path
- symbol/function/class/route
- input
- output or side effect
- next hop

If a step is dynamic or framework-generated and cannot be proven directly, label it `inferred` and explain why.

## Evidence model

For every architectural claim, attach evidence as one or more objects:

```json
{
  "claim": "Chat requests are handled by the API route before invoking the model service.",
  "status": "verified",
  "sources": [
    {"path": "src/api/chat.ts", "symbol": "POST"},
    {"path": "src/services/llm.ts", "symbol": "generateResponse"}
  ]
}
```

Allowed status values:

- `verified` — directly supported by source/config/tests.
- `inferred` — strongly suggested but not directly proven.
- `unknown` — cannot be established from available source.

Do not silently upgrade inference to fact.

## Important-file selection

Prefer 5–15 files that explain most of the architecture. Favor:

- bootstraps/entrypoints
- router/controller registrations
- module composition roots
- central domain/service implementations
- persistence adapters/schema
- external API clients
- auth middleware/policy
- representative tests

Do not select files solely because they are large.

## Monorepos

For monorepos:

1. Identify workspace/package boundaries.
2. Find runnable apps/services.
3. Determine shared packages used by the primary app.
4. Scope the main video to one runnable product unless the user asks for a repository-wide architecture tour.
5. Show cross-package dependencies only when they matter to the selected execution paths.

## Security and privacy

Never include secret values. Do not read or quote credentials from `.env`, secret files, private keys, certificates, auth cookies, or local credential stores. Environment-variable names and configuration structure are sufficient for explanation.
