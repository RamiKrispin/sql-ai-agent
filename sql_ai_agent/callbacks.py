"""
LangChain Callbacks for SQL AI Agent

Provides custom callback handlers for tracking LLM metrics including:
- Token usage and cost estimation
- LLM invocation timing
- Error tracking
- Session-level aggregation
cd
These callbacks automatically log all LLM interactions when attached to
LangChain chains or LLMs.
"""

from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List, Optional
import time
from sql_ai_agent.token_utils import estimate_tokens


class LLMMetricsCallback(BaseCallbackHandler):
    """
    LangChain callback handler for tracking LLM metrics.

    Automatically logs LLM invocations, token usage, timing, and errors.
    Integrates with the SQL AI Agent logging system for structured output.

    Attributes:
        logger: SQLAgentLogger instance for logging
        session_id: Unique session identifier
        agent_config: Dictionary of agent configuration settings
        invocation_count: Total number of LLM calls in this session
        total_tokens: Cumulative token count
        total_cost: Estimated total cost (if pricing configured)

    Usage:
        agent_config = {
            'model': 'gpt-4o',
            'read_only': True,
            'enforce_limit': True,
            'max_result_limit': 10000,
            'memory_enabled': True,
            'memory_size': 10,
            'skill_enabled': False
        }
        callback = LLMMetricsCallback(logger, session_id="abc123", agent_config=agent_config)
        llm = ChatOpenAI(
            model="gpt-4o",
            callbacks=[callback]
        )
    """

    def __init__(self, logger, session_id: str, agent_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the metrics callback.

        Args:
            logger: SQLAgentLogger instance for logging
            session_id: Unique session identifier
            agent_config: Optional dictionary of agent configuration settings
        """
        self.logger = logger
        self.session_id = session_id
        self.agent_config = agent_config or {}
        self.invocation_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self._current_run_start = None

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """
        Called when LLM starts running.

        Logs the start of an LLM invocation with model details, agent settings,
        and prompt token estimation.

        Args:
            serialized: Serialized LLM configuration
            prompts: List of prompt strings
            **kwargs: Additional keyword arguments
        """
        self._current_run_start = time.perf_counter()
        self.invocation_count += 1

        model_name = serialized.get('name', 'unknown')

        # Estimate prompt tokens
        total_prompt_chars = sum(len(p) for p in prompts)
        estimated_prompt_tokens = estimate_tokens(''.join(prompts), model_name)

        # Build log extra fields
        log_extra = {
            'operation_type': 'llm_invocation',
            'model_name': model_name,
            'prompt_count': len(prompts),
            'invocation_number': self.invocation_count,
            'estimated_prompt_tokens': estimated_prompt_tokens,
            'total_prompt_chars': total_prompt_chars,
        }

        # Add agent configuration settings if available
        if self.agent_config:
            log_extra['agent_config'] = {
                'model': self.agent_config.get('model'),
                'read_only': self.agent_config.get('read_only'),
                'enforce_limit': self.agent_config.get('enforce_limit'),
                'max_result_limit': self.agent_config.get('max_result_limit'),
                'memory_enabled': self.agent_config.get('memory_enabled'),
                'memory_size': self.agent_config.get('memory_size'),
                'skill_enabled': self.agent_config.get('skill_enabled'),
                'fallback_enabled': self.agent_config.get('fallback_enabled'),
                'fallback_model': self.agent_config.get('fallback_model'),
            }

        self.logger.debug(
            f"LLM invocation started: {model_name} (~{estimated_prompt_tokens} tokens)",
            extra=log_extra
        )

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """
        Called when LLM finishes running successfully.

        Logs completion with token usage, timing, and cumulative metrics.

        Args:
            response: LLM response object with token usage info
            **kwargs: Additional keyword arguments
        """
        duration_ms = (time.perf_counter() - self._current_run_start) * 1000

        # Extract token usage from response
        llm_output = response.llm_output or {}
        token_usage = llm_output.get('token_usage', {})
        prompt_tokens = token_usage.get('prompt_tokens', 0)
        completion_tokens = token_usage.get('completion_tokens', 0)
        total_tokens = token_usage.get('total_tokens', 0)

        self.total_tokens += total_tokens

        self.logger.info(
            f"LLM invocation completed",
            extra={
                'operation_type': 'llm_invocation',
                'duration_ms': round(duration_ms, 2),
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'cumulative_tokens': self.total_tokens,
                'invocation_number': self.invocation_count
            }
        )

    def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        """
        Called when LLM encounters an error.

        Logs error details with timing and error type information.

        Args:
            error: Exception that occurred
            **kwargs: Additional keyword arguments
        """
        duration_ms = (time.perf_counter() - self._current_run_start) * 1000

        self.logger.error(
            f"LLM invocation failed: {str(error)}",
            extra={
                'operation_type': 'llm_invocation',
                'duration_ms': round(duration_ms, 2),
                'error_type': type(error).__name__,
                'error_message': str(error),
                'invocation_number': self.invocation_count
            },
            exc_info=True
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics for this session.

        Returns:
            Dictionary with session metrics including:
            - session_id: Session identifier
            - total_invocations: Number of LLM calls
            - total_tokens: Total tokens used
            - total_cost: Estimated total cost
        """
        return {
            'session_id': self.session_id,
            'total_invocations': self.invocation_count,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost
        }
