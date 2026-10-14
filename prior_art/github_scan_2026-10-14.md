# GitHub scan — agent swarms, stigmergy, LLM ants (2026-10-14, Claude)

Method: web search restricted to github.com (GitHub API search not available from this session), ~7 queries, top repos read. Not exhaustive.

Verdict: no repo found that runs LLM agents on a double bridge with an evaporation sweep, an exploration dose and an ant control. Novelty claim stands. Practical gap: several tools ship "evaporating pheromone memory" for AI agents with no evidence on decay or exploration settings.

| Repo | What | Closeness | Stars / licence | Use |
|---|---|---|---|---|
| roanbrasil/agentic-superorganisms | Insect primitives for multi-agent systems; E1 = double bridge with late shortcut, evaporation varied; recovery is zero without evaporation. No LLM in the loop. | High on the ant side (same idea as our ant control) | 0 / MIT | Cite as code prior art; independent reference for the ant result |
| crjimene/swarm_gpt | Code for Jimenez-Romero et al. 2025: GPT-4o ants with pheromones in NetLogo | High (LLM ants), but no switch test, no decay sweep | — | Already cited |
| calabamatex/Stigmergy-mcp | MCP server: typed decaying traces for AI coding agents (24 h exponential decay). Says the benefit of decay is unproven. | Applied; our result speaks to its open question | 55 / MIT | Possible user/collaborator; shows practical demand |
| ChrisRoyse/Pheromind | Proprietary "pheromone" swarm for software dev; no data | Low (marketing) | 377 / proprietary | Market signal only |
| qayyumu/crewSwarm | CrewAI agents with evaporating pheromone trails; no measurements | Low | 0 / — | — |
| MartinM10/Myrmo; MyKineID/aoc-memory-for-ai-agent; Happyarch/stigmergy; oasis-main/dot_swarm; ellmos-ai/swarm_ai | Shared-memory / trail tools for AI agents; no experiments on decay or exploration | Low | small | Market signal: builders want fading shared memory |
| RUC-GSAI/YuLan-SwarmIntell (SwarmBench, arXiv 2505.04364) | Benchmark of LLM swarm tasks (pursuit, sync, foraging, flocking, transport); local view, no pheromones | Medium (LLM swarm benchmark) | 39 / MIT | Possible venue: propose a double-bridge task |
| SwarmSys (arXiv 2510.10047) | Pheromone-inspired explorer/worker/validator LLM roles; no decay ablation in abstract | Medium | — | Cite in related work |
| AaryaTedla/stigmergy-robustness | PPO agents, pheromone fields, attack/defence; early | Low (no LLM) | 0 | — |
