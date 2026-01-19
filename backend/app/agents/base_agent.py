"""
Base agent class for all evaluation agents.
"""
import json
import logging
from typing import Dict, Any, Optional
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all evaluation agents.

    Provides common functionality including:
    - AWS Bedrock LLM initialization
    - Prompt formatting
    - JSON response parsing
    - Error handling
    - Logging
    """

    def __init__(
        self,
        agent_name: str = "BaseAgent",
        model_id: str = "anthropic.claude-sonnet-4-20250514-v1:0",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        region_name: Optional[str] = None
    ):
        """
        Initialize the base agent.

        Args:
            agent_name: Name of the agent for logging
            model_id: AWS Bedrock model ID
            temperature: LLM temperature (0.0 - 1.0)
            max_tokens: Maximum tokens in response
            region_name: AWS region (optional, uses default if not provided)
        """
        self.agent_name = agent_name
        self.model_id = model_id

        # Initialize AWS Bedrock LLM
        bedrock_kwargs = {
            "model_id": model_id,
            "model_kwargs": {
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }

        if region_name:
            bedrock_kwargs["region_name"] = region_name

        try:
            self.llm = ChatBedrock(**bedrock_kwargs)
            logger.info(f"{self.agent_name} initialized with model {model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize {self.agent_name}: {str(e)}")
            raise

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main invocation method. Must be implemented by subclasses.

        Args:
            input_data: Input data for the agent

        Returns:
            Dict containing agent output

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError(
            f"{self.agent_name}.invoke() must be implemented by subclass"
        )

    def _create_prompt(
        self,
        system_prompt: str,
        user_prompt: str,
        **kwargs
    ) -> list:
        """
        Create a formatted prompt for the LLM.

        Args:
            system_prompt: System message content
            user_prompt: User message template with placeholders
            **kwargs: Variables to format into the user prompt

        Returns:
            List of messages for the LLM
        """
        try:
            # Format the user prompt with provided variables
            formatted_user_prompt = user_prompt.format(**kwargs)

            # Create message list
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=formatted_user_prompt)
            ]

            return messages

        except KeyError as e:
            logger.error(f"{self.agent_name}: Missing prompt variable: {str(e)}")
            raise ValueError(f"Missing required prompt variable: {str(e)}")
        except Exception as e:
            logger.error(f"{self.agent_name}: Error creating prompt: {str(e)}")
            raise

    async def _invoke_llm(
        self,
        messages: list,
        parse_json: bool = True
    ) -> Dict[str, Any]:
        """
        Invoke the LLM with messages and parse response.

        Args:
            messages: List of messages to send to LLM
            parse_json: Whether to parse response as JSON

        Returns:
            Dict containing LLM response (parsed JSON or raw text)

        Raises:
            Exception: If LLM invocation fails
        """
        try:
            logger.info(f"{self.agent_name}: Starting LLM invoke call with model {self.model_id}")
            logger.debug(f"{self.agent_name}: Invoking LLM...")
            logger.debug(f"{self.agent_name}: Number of messages: {len(messages)}")

            # Log message preview
            if messages:
                first_msg = str(messages[0])[:200] if len(str(messages[0])) > 200 else str(messages[0])
                logger.debug(f"{self.agent_name}: First message preview: {first_msg}...")

            # Invoke LLM
            logger.info(f"{self.agent_name}: Calling llm.ainvoke() method now...")
            response = await self.llm.ainvoke(messages)
            logger.info(f"{self.agent_name}: LLM invoke call completed successfully")

            # Extract content
            content = response.content if hasattr(response, 'content') else str(response)

            logger.info(f"{self.agent_name}: Received LLM response ({len(content)} chars)")
            logger.debug(f"{self.agent_name}: Response preview: {content[:200]}..." if len(content) > 200 else f"{self.agent_name}: Response: {content}")

            if parse_json:
                logger.debug(f"{self.agent_name}: Parsing response as JSON...")
                result = self._parse_json_response(content)
                logger.debug(f"{self.agent_name}: JSON parsing completed")
                return result
            else:
                return {"raw_response": content}

        except Exception as e:
            logger.error(f"{self.agent_name}: LLM invocation failed: {str(e)}")
            logger.error(f"{self.agent_name}: LLM invoke call encountered an error")
            raise

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling common issues.

        Args:
            response_text: Raw text response from LLM

        Returns:
            Parsed JSON as dictionary

        Raises:
            ValueError: If JSON parsing fails
        """
        try:
            # Try direct parsing first
            return json.loads(response_text)

        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            logger.debug(f"{self.agent_name}: Direct JSON parse failed, trying to extract from markdown")

            # Look for JSON in code blocks
            import re
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            matches = re.findall(json_pattern, response_text, re.DOTALL)

            if matches:
                try:
                    return json.loads(matches[0])
                except json.JSONDecodeError:
                    pass

            # Try to find JSON object directly
            json_pattern = r'\{.*\}'
            matches = re.findall(json_pattern, response_text, re.DOTALL)

            if matches:
                # Try the longest match (most likely to be complete)
                for match in sorted(matches, key=len, reverse=True):
                    try:
                        return json.loads(match)
                    except json.JSONDecodeError:
                        continue

            logger.error(f"{self.agent_name}: Failed to parse JSON from response")
            logger.debug(f"Response text: {response_text[:500]}...")
            raise ValueError("Failed to parse JSON from LLM response")

    def _validate_output(
        self,
        output: Dict[str, Any],
        required_fields: list
    ) -> bool:
        """
        Validate that output contains all required fields.

        Args:
            output: Output dictionary to validate
            required_fields: List of required field names

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        missing_fields = [field for field in required_fields if field not in output]

        if missing_fields:
            error_msg = f"{self.agent_name}: Missing required fields: {missing_fields}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return True

    def _handle_error(
        self,
        error: Exception,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Handle errors and return standardized error response.

        Args:
            error: The exception that occurred
            context: Additional context about where error occurred

        Returns:
            Dict with error information
        """
        error_msg = f"{self.agent_name} error"
        if context:
            error_msg += f" during {context}"
        error_msg += f": {str(error)}"

        logger.error(error_msg, exc_info=True)

        return {
            "error": True,
            "agent": self.agent_name,
            "error_message": str(error),
            "context": context
        }

    def log_info(self, message: str):
        """Log info message with agent name."""
        logger.info(f"{self.agent_name}: {message}")

    def log_debug(self, message: str):
        """Log debug message with agent name."""
        logger.debug(f"{self.agent_name}: {message}")

    def log_error(self, message: str):
        """Log error message with agent name."""
        logger.error(f"{self.agent_name}: {message}")

    def log_warning(self, message: str):
        """Log warning message with agent name."""
        logger.warning(f"{self.agent_name}: {message}")
