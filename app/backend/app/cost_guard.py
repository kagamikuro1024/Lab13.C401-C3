"""
Cost Guard Module — Token usage tracking and budget protection
"""

from datetime import datetime, timedelta


class CostGuard:
    """Track OpenAI API call costs and enforce budget limits"""
    
    # Token pricing for GPT-4o-mini (USD per 1M tokens)
    INPUT_COST_PER_1M = 0.15
    OUTPUT_COST_PER_1M = 0.60
    
    def __init__(self, per_user_budget=1.0, global_budget=10.0):
        """
        Initialize cost guard.
        
        Args:
            per_user_budget: Daily budget per user (USD)
            global_budget: Global daily budget (USD)
        """
        self.per_user_budget = per_user_budget
        self.global_budget = global_budget
        self.user_usage = {}  # {user_id: {date: {cost, tokens}}}
        self.global_usage = {}  # {date: {cost, tokens}}
    
    def _get_date_key(self):
        """Get today's date as key"""
        return datetime.utcnow().strftime("%Y-%m-%d")
    
    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int):
        """
        Record token usage and calculate cost.
        
        Args:
            user_id: User identifier
            input_tokens: Input tokens used
            output_tokens: Output tokens used
        """
        cost = (input_tokens * self.INPUT_COST_PER_1M + output_tokens * self.OUTPUT_COST_PER_1M) / 1_000_000
        date_key = self._get_date_key()
        
        # User usage
        if user_id not in self.user_usage:
            self.user_usage[user_id] = {}
        if date_key not in self.user_usage[user_id]:
            self.user_usage[user_id][date_key] = {"cost": 0, "tokens": 0}
        
        self.user_usage[user_id][date_key]["cost"] += cost
        self.user_usage[user_id][date_key]["tokens"] += input_tokens + output_tokens
        
        # Global usage
        if date_key not in self.global_usage:
            self.global_usage[date_key] = {"cost": 0, "tokens": 0}
        
        self.global_usage[date_key]["cost"] += cost
        self.global_usage[date_key]["tokens"] += input_tokens + output_tokens
    
    def get_user_cost(self, user_id: str) -> float:
        """
        Get today's cost for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Total cost in USD
        """
        date_key = self._get_date_key()
        if user_id in self.user_usage and date_key in self.user_usage[user_id]:
            return self.user_usage[user_id][date_key]["cost"]
        return 0.0
    
    def get_global_cost(self) -> float:
        """
        Get today's global cost.
        
        Returns:
            Total global cost in USD
        """
        date_key = self._get_date_key()
        if date_key in self.global_usage:
            return self.global_usage[date_key]["cost"]
        return 0.0
    
    def get_user_stats(self, user_id: str) -> dict:
        """
        Get user's daily stats.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with cost stats
        """
        cost = self.get_user_cost(user_id)
        remaining = max(0, self.per_user_budget - cost)
        
        return {
            "spent_today": cost,
            "budget": self.per_user_budget,
            "remaining": remaining,
            "usage_percent": (cost / self.per_user_budget * 100) if self.per_user_budget > 0 else 0,
            "reset_time": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00 UTC")
        }
    
    def get_global_stats(self) -> dict:
        """
        Get global daily stats.
        
        Returns:
            Dictionary with global cost stats
        """
        cost = self.get_global_cost()
        remaining = max(0, self.global_budget - cost)
        
        return {
            "spent_today": cost,
            "budget": self.global_budget,
            "remaining": remaining,
            "usage_percent": (cost / self.global_budget * 100) if self.global_budget > 0 else 0,
            "reset_time": (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d 00:00:00 UTC")
        }
    
    def check_user_budget(self, user_id: str) -> tuple[bool, str]:
        """
        Check if user has remaining budget.
        
        Args:
            user_id: User identifier
            
        Returns:
            (allowed, message) tuple
        """
        cost = self.get_user_cost(user_id)
        remaining = max(0, self.per_user_budget - cost)
        
        if remaining <= 0:
            return False, f"Budget exceeded: ${cost:.4f}/${self.per_user_budget}"
        elif remaining < 0.1:
            return True, f"⚠️ Low budget: ${remaining:.4f} remaining"
        else:
            return True, ""
    
    def check_global_budget(self) -> tuple[bool, str]:
        """
        Check if global budget is available.
        
        Returns:
            (allowed, message) tuple
        """
        cost = self.get_global_cost()
        remaining = max(0, self.global_budget - cost)
        
        if remaining <= 0:
            return False, f"Global budget exceeded: ${cost:.4f}/${self.global_budget}"
        elif remaining < 1.0:
            return True, f"⚠️ Low global budget: ${remaining:.4f} remaining"
        else:
            return True, ""
