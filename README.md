# AI Agent Sandbox

AI Agent Sandbox is a controlled Python execution environment designed for AI-agent workflows. It provides a restricted tool interface with permission checks, filesystem isolation, resource limits, audit logging, and automatic rollback when operations fail.

## Features

* Controlled tool execution
* Tool allowlisting
* `read_file`
* `write_file`
* `list_files`
* Sandbox path isolation
* Path traversal protection
* Permission controls
* Operation limits
* File-size limits
* Total write limits
* Automatic rollback
* Transaction-style snapshots
* Execution audit logs
* JSON reports
* Built-in demo mode

## Tech Stack

**Python | File System | JSON | CLI | Security | DSA**

## DSA Used

**Dictionary | Set | deque | Snapshot State | Queue-based Task Processing**

## Usage

Run the built-in demo:

```bash
python ai_agent_sandbox.py --demo
```

Run custom tasks:

```bash
python ai_agent_sandbox.py --tasks tasks.json
```

Set resource limits:

```bash
python ai_agent_sandbox.py --tasks tasks.json --max-ops 20 --max-write-bytes 10000 --max-file-bytes 5000
```

Generate a JSON report:

```bash
python ai_agent_sandbox.py --demo --json sandbox_report.json
```

## Architecture

```text
AI Agent
   ↓
Task Queue
   ↓
Permission Engine
   ↓
Tool Registry
   ↓
Sandbox Filesystem
   ↓
Resource Validation
   ↓
Execution
   ↓
Audit Log
   ↓
Commit / Rollback
```

## Example Task

```json
[
  {
    "tool":"write_file",
    "args":{
      "path":"workspace/result.txt",
      "content":"Task completed."
    }
  },
  {
    "tool":"read_file",
    "args":{
      "path":"workspace/result.txt"
    }
  }
]
```

## Security Model

The sandbox deliberately exposes only approved tools and prevents arbitrary shell commands or unrestricted Python execution. File operations are confined to the sandbox, and configured resource limits prevent excessive operations or writes.

## Purpose

Built to demonstrate secure AI-agent tooling, permission systems, sandbox isolation, resource governance, auditability, and transaction-based rollback using Python.


