"""
Interview Agent Module

This module provides the AI agent that orchestrates the entire interview process,
including question generation, answer evaluation, weak area identification,
and personalized suggestion generation.

The agent follows an observe-think-act loop to make intelligent decisions
throughout the interview session.

Key Components:
- InterviewAgent: The main orchestrator class
- AgentState: Manages interview context and state
- AgentTools: Collection of tools for question generation, evaluation, etc.
- AgentConfig: Configuration settings for agent behavior
"""

from .interview_agent import InterviewAgent
from .agent_state import AgentState, InterviewContext, AgentPhase
from .tools import AgentTools, ToolResult
from .config import AgentConfig, get_config, default_config

__all__ = [
    "InterviewAgent",
    "AgentState",
    "InterviewContext",
    "AgentPhase",
    "AgentTools",
    "ToolResult",
    "AgentConfig",
    "get_config",
    "default_config"
]
