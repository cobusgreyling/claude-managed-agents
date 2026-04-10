# Four Ways to Build AI Agents with Claude — Runner
#
# Usage:
#   make run-sdk              Run Approach 1 (Agent SDK)
#   make run-teams            Run Approach 3 (Agent Teams)
#   make run-managed          Run Approach 4 (Managed Agents)
#   make run-all              Run all programmatic approaches
#   make install              Install all dependencies
#   make clean                Remove generated reports
#
# Note: Approach 2 (Markdown Definitions) runs inside Claude Code,
#       not as a standalone script. Use `make install-md` to copy
#       the agent definition into your Claude Code agents directory.

TARGET ?= sample_target/app.py

.PHONY: install install-md run-sdk run-teams run-managed run-all clean help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

install: ## Install dependencies for all approaches
	pip install -r examples/01_agent_sdk/requirements.txt
	pip install -r examples/03_agent_teams/requirements.txt
	pip install -r examples/04_managed_agents/requirements.txt

install-md: ## Copy Markdown agent definition to Claude Code agents directory
	@mkdir -p ~/.claude/agents
	cp examples/02_markdown_definitions/security-auditor.md ~/.claude/agents/
	@echo "Installed security-auditor.md to ~/.claude/agents/"

run-sdk: ## Run Approach 1 — Agent SDK
	@echo "━━━ Approach 1: Agent SDK ━━━"
	cd examples/01_agent_sdk && python audit_agent.py ../../$(TARGET)

run-teams: ## Run Approach 3 — Agent Teams
	@echo "━━━ Approach 3: Agent Teams ━━━"
	cd examples/03_agent_teams && python team_audit.py ../../$(TARGET)

run-managed: ## Run Approach 4 — Managed Agents
	@echo "━━━ Approach 4: Managed Agents ━━━"
	cd examples/04_managed_agents && python audit_agent.py ../../$(TARGET)

run-all: run-sdk run-teams run-managed ## Run all programmatic approaches sequentially
	@echo ""
	@echo "━━━ All approaches complete ━━━"
	@echo "Reports saved to:"
	@echo "  examples/01_agent_sdk/audit_report.md"
	@echo "  examples/03_agent_teams/team_audit_report.md"
	@echo "  examples/04_managed_agents/audit_report.md"

clean: ## Remove generated audit reports
	rm -f examples/01_agent_sdk/audit_report.md
	rm -f examples/03_agent_teams/team_audit_report.md
	rm -f examples/04_managed_agents/audit_report.md
