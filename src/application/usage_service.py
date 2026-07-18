from typing import List, Optional
from src.domain.models import UsageLog
from src.application.ports import UsageLogRepositoryPort, AgentRepositoryPort, ClientRepositoryPort

# Pricing per 1M tokens (in / out)
MODEL_PRICES = {
    "gpt-4o-mini": {"in": 0.15, "out": 0.60},
    "gpt-4o": {"in": 2.50, "out": 10.00},
    "claude-sonnet": {"in": 3.00, "out": 15.00},
    "claude-3-5-sonnet-20241022": {"in": 3.00, "out": 15.00},
    "gemini-2.0-flash": {"in": 0.10, "out": 0.40},
}

class UsageService:
    def __init__(
        self,
        usage_repo: UsageLogRepositoryPort,
        agent_repo: AgentRepositoryPort,
        client_repo: ClientRepositoryPort
    ):
        self.usage_repo = usage_repo
        self.agent_repo = agent_repo
        self.client_repo = client_repo

    def calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        # Default to 0 if model is unknown
        prices = MODEL_PRICES.get(model, {"in": 0.0, "out": 0.0})
        cost_in = (tokens_in / 1_000_000) * prices["in"]
        cost_out = (tokens_out / 1_000_000) * prices["out"]
        return cost_in + cost_out

    def log_usage(self, agent_id: int, tokens_in: int, tokens_out: int) -> Optional[UsageLog]:
        agent = self.agent_repo.get_by_id(agent_id)
        if not agent:
            return None
        
        model = agent.model
        client_id = agent.client_id
        cost_usd = self.calculate_cost(model, tokens_in, tokens_out)
        
        data = {
            "agent_id": agent_id,
            "client_id": client_id,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd
        }
        return self.usage_repo.create(data)

    def get_client_usage(self, client_id: int, period: str) -> dict:
        client = self.client_repo.get_by_id(client_id)
        if not client:
            return {"error": "Client not found"}
            
        logs = self.usage_repo.get_by_client_id_and_period(client_id, period)
        
        total_tokens = sum(log.tokens_in + log.tokens_out for log in logs)
        total_cost_usd = sum(log.cost_usd for log in logs)
        
        # Breakdown by agent and model
        breakdown = {}
        for log in logs:
            key = f"{log.agent_id}_{log.model}"
            if key not in breakdown:
                breakdown[key] = {
                    "agent_id": log.agent_id,
                    "model": log.model,
                    "tokens_in": 0,
                    "tokens_out": 0,
                    "total_tokens": 0,
                    "cost_usd": 0.0,
                    "runs": 0
                }
            breakdown[key]["tokens_in"] += log.tokens_in
            breakdown[key]["tokens_out"] += log.tokens_out
            breakdown[key]["total_tokens"] += (log.tokens_in + log.tokens_out)
            breakdown[key]["cost_usd"] += log.cost_usd
            breakdown[key]["runs"] += 1
            
        return {
            "client_id": client_id,
            "client_name": client.name,
            "period": period,
            "total_tokens": total_tokens,
            "total_cost_usd": total_cost_usd,
            "total_runs": len(logs),
            "breakdown": list(breakdown.values())
        }
        
    def get_summary(self, period: str) -> List[dict]:
        summary_data = self.usage_repo.get_summary_by_period(period)
        
        result = []
        for item in summary_data:
            client = self.client_repo.get_by_id(item["client_id"])
            item["client_name"] = client.name if client else "Unknown"
            result.append(item)
            
        return result
