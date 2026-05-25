from typing import List, Optional
from src.domain.models import Client, Agent
from src.application.ports import ClientRepositoryPort, AgentRepositoryPort

class ClientService:
    def __init__(self, client_repository: ClientRepositoryPort, agent_repository: AgentRepositoryPort):
        self.client_repository = client_repository
        self.agent_repository = agent_repository

    def get_clients(self) -> List[Client]:
        """Retrieves a list of all clients."""
        return self.client_repository.get_all()

    def get_client(self, client_id: int) -> Optional[Client]:
        """Retrieves a specific client by ID."""
        return self.client_repository.get_by_id(client_id)

    def create_client(self, client_data: Client) -> Client:
        """Creates and saves a new client."""
        return self.client_repository.save(client_data)

    def get_client_agents(self, client_id: int) -> List[Agent]:
        """Retrieves all agents assigned to a specific client."""
        return self.agent_repository.get_by_client_id(client_id)

    def get_client_dashboard(self, client_id: int, days: int) -> Optional[dict]:
        """Generates the dashboard metrics for a client and their agents."""
        client = self.client_repository.get_by_id(client_id)
        if not client:
            return None
        
        agents = self.agent_repository.get_by_client_id(client_id)
        
        # Generate mock metrics based on actual agents
        import random
        from datetime import datetime, timedelta, timezone
        
        now = datetime.now(timezone.utc)
        
        agent_list = []
        total_tokens = 0
        total_cost = 0.0
        total_runs = 0
        total_latency = 0
        success_runs = 0
        
        chatbots_count = 0
        agents_count = 0
        active_count = 0
        
        # Consistent randomness per agent based on its ID
        for a in agents:
            # Seed based on agent ID to make mock data persistent
            random.seed(a.id if a.id else 1)
            is_chatbot = a.type == "chatbot" or a.model == "gpt-4o-mini"
            if is_chatbot:
                chatbots_count += 1
            else:
                agents_count += 1
                
            if a.status == "active":
                active_count += 1
                
            # Base usage
            a_runs = random.randint(5, 50) * days
            a_tokens = a_runs * random.randint(300, 1500)
            a_cost = a_tokens * 0.000002
            a_latency = random.randint(200, 1500)
            
            # Error rate
            a_error_rate = random.uniform(0.1, 5.0) if a.status != "testing" else random.uniform(10.0, 25.0)
            
            total_tokens += a_tokens
            total_cost += a_cost
            total_runs += a_runs
            total_latency += a_latency * a_runs
            success_runs += int(a_runs * (1 - a_error_rate/100))
            
            agent_list.append({
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "model": a.model or "gpt-4o-mini",
                "status": "running" if a.status == "active" else "stopped",
                "agent_type": "chatbot" if is_chatbot else "agent",
                "tokens": a_tokens,
                "cost": round(a_cost, 4),
                "avg_latency_ms": float(a_latency),
                "error_rate_pct": round(a_error_rate, 2)
            })
            
        overall_error_rate = 0.0
        overall_avg_latency = 0.0
        if total_runs > 0:
            overall_error_rate = round((1 - (success_runs / total_runs)) * 100, 2)
            overall_avg_latency = float(total_latency / total_runs)
            
        summary = {
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 4),
            "active": active_count,
            "total_agents": len(agents),
            "chatbots": chatbots_count,
            "agents": agents_count,
            "error_rate_pct": overall_error_rate,
            "avg_latency_ms": overall_avg_latency
        }
        
        # Timeseries
        timeseries = []
        random.seed(client_id)
        for i in range(days - 1, -1, -1):
            d = now - timedelta(days=i)
            # Add some variation to the daily runs
            day_runs = int((total_runs / days) * random.uniform(0.6, 1.4)) if days > 0 else 0
            day_tokens = int((total_tokens / days) * random.uniform(0.6, 1.4)) if days > 0 else 0
            timeseries.append({
                "date": d.strftime("%Y-%m-%d"),
                "tokens": day_tokens,
                "cost": round(day_tokens * 0.000002, 4),
                "runs": day_runs,
                "avg_latency_ms": float(overall_avg_latency * random.uniform(0.9, 1.1))
            })
            
        return {
            "client": client,
            "summary": summary,
            "agents": agent_list,
            "timeseries": timeseries
        }
