"""Tests for the Hello World Agent."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage


@pytest.fixture
def mock_llm_response():
    """Mock LLM that always returns 'hello world'."""
    mock_msg = AIMessage(content="hello world")
    mock_result = {"messages": [mock_msg]}
    return mock_result


@pytest.fixture
def agent(mock_llm_response):
    """Create a SampleAgent with mocked LLM."""
    with patch("langchain_litellm.ChatLiteLLM") as mock_chat_cls:
        mock_llm = MagicMock()
        mock_chat_cls.return_value = mock_llm
        with patch("app.agent.create_agent") as mock_create_agent:
            mock_graph = AsyncMock()
            mock_graph.ainvoke = AsyncMock(return_value=mock_llm_response)
            mock_create_agent.return_value = mock_graph
            from app.agent import SampleAgent
            a = SampleAgent()
            a._mock_graph = mock_graph
            a._mock_create = mock_create_agent
            yield a


class TestSampleAgentInvoke:
    """Test the agent invoke method."""

    @pytest.mark.asyncio
    async def test_invoke_returns_hello_world(self, agent, mock_llm_response):
        """Agent should return hello world for any input."""
        with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
            mock_msg = MagicMock()
            mock_msg.content = "hello world"
            mock_invoke.return_value = {"messages": [mock_msg]}

            result = await agent.invoke("hi", "test-context")
            assert result.status == "completed"
            assert "hello world" in result.message.lower()

    @pytest.mark.asyncio
    async def test_invoke_any_message_returns_hello_world(self, agent):
        """Agent should respond hello world regardless of the input message."""
        with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
            mock_msg = MagicMock()
            mock_msg.content = "hello world"
            mock_invoke.return_value = {"messages": [mock_msg]}

            for message in ["hello", "what is 2+2?", "tell me a story", ""]:
                result = await agent.invoke(message, "ctx-1")
                assert result.status == "completed"
                assert "hello world" in result.message.lower()


class TestSampleAgentStream:
    """Test the agent stream method."""

    @pytest.mark.asyncio
    async def test_stream_yields_hello_world(self, agent):
        """Stream should yield a completed response containing hello world."""
        with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
            mock_msg = MagicMock()
            mock_msg.content = "hello world"
            mock_invoke.return_value = {"messages": [mock_msg]}

            results = []
            async for chunk in agent.stream("hi", "ctx-stream"):
                results.append(chunk)

            # Last chunk must be the completed response
            final = results[-1]
            assert final["is_task_complete"] is True
            assert "hello world" in final["content"].lower()

    @pytest.mark.asyncio
    async def test_stream_first_chunk_is_processing(self, agent):
        """First yielded chunk should indicate processing."""
        with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
            mock_msg = MagicMock()
            mock_msg.content = "hello world"
            mock_invoke.return_value = {"messages": [mock_msg]}

            results = []
            async for chunk in agent.stream("hi", "ctx-first"):
                results.append(chunk)

            assert results[0]["is_task_complete"] is False
            assert results[0]["require_user_input"] is False


class TestMilestoneInstrumentation:
    """Test that business milestones are logged."""

    @pytest.mark.asyncio
    async def test_m2_achieved_logged_on_hello_world_response(self, agent, caplog):
        """M2.achieved should be logged when agent returns hello world."""
        import logging
        with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
            mock_msg = MagicMock()
            mock_msg.content = "hello world"
            mock_invoke.return_value = {"messages": [mock_msg]}

            with caplog.at_level(logging.INFO, logger="app.agent"):
                await agent._run_agent("hi", "ctx-m2")

            assert any("M2.achieved" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_m2_missed_logged_when_no_hello_world(self, agent, caplog):
        """M2.missed should be logged when response doesn't contain hello world."""
        import logging
        with patch.object(agent, "_invoke", new_callable=AsyncMock) as mock_invoke:
            mock_msg = MagicMock()
            mock_msg.content = "This is something else entirely"
            mock_invoke.return_value = {"messages": [mock_msg]}

            with caplog.at_level(logging.WARNING, logger="app.agent"):
                await agent._run_agent("hi", "ctx-m2-miss")

            assert any("M2.missed" in r.message for r in caplog.records)


class TestIntegration:
    """End-to-end integration test for the hello world agent flow."""

    @pytest.mark.asyncio
    async def test_end_to_end_hello_world_flow(self):
        """Full agent flow: any message in → hello world out."""
        with patch("langchain_litellm.ChatLiteLLM") as mock_chat_cls:
            mock_llm = MagicMock()
            mock_chat_cls.return_value = mock_llm

            with patch("app.agent.create_agent") as mock_create_agent:
                mock_graph = AsyncMock()
                mock_msg = MagicMock()
                mock_msg.content = "hello world"
                mock_graph.ainvoke = AsyncMock(return_value={"messages": [mock_msg]})
                mock_create_agent.return_value = mock_graph

                from app.agent import SampleAgent
                agent = SampleAgent()
                result = await agent.invoke("any message at all", "e2e-context")

                assert result.status == "completed"
                assert "hello world" in result.message.lower()
