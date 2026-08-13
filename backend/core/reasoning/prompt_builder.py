"""
Prompt builder.

Constructs prompts for LLM-based reasoning strategies.

The PromptBuilder is intentionally independent of any particular LLM
provider. Its responsibility is limited to translating a
ReasoningRequest and its accompanying ReasoningContext into a structured
prompt that can be consumed by any chat or completion model.

Future implementations may support:

- provider-specific prompt templates
- few-shot prompting
- retrieval-augmented prompts
- tool descriptions
- function calling
- chain-of-thought suppression
- multimodal prompts
"""

from __future__ import annotations

from backend.core.reasoning.reasoning_context import (
    ReasoningContext,
)
from backend.core.reasoning.reasoning_request import (
    ReasoningRequest,
)


class PromptBuilder:
    """
    Builds structured reasoning prompts.
    """

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    def build(
        self,
        request: ReasoningRequest,
        context: ReasoningContext,
    ) -> str:
        """
        Build a reasoning prompt.
        """

        sections: list[str] = []

        sections.append(
            self._system_section(),
        )

        sections.append(
            self._goal_section(
                request,
            ),
        )

        if request.has_constraints:
            sections.append(
                self._constraints_section(
                    request,
                ),
            )

        if request.has_context:
            sections.append(
                self._context_section(
                    context,
                ),
            )

        sections.append(
            self._instructions_section(),
        )

        return "\n\n".join(
            section
            for section in sections
            if section
        )

    # ------------------------------------------------------------------
    # Sections
    # ------------------------------------------------------------------

    def _system_section(
        self,
    ) -> str:
        """
        Build the system prompt.
        """

        return (
            "You are the reasoning engine for an autonomous AI system.\n"
            "Analyze the objective, evaluate constraints, and produce "
            "the safest and most effective decision."
        )

    def _goal_section(
        self,
        request: ReasoningRequest,
    ) -> str:
        """
        Build the goal section.
        """

        return (
            "GOAL\n"
            "----\n"
            f"{request.goal}"
        )

    def _constraints_section(
        self,
        request: ReasoningRequest,
    ) -> str:
        """
        Build the constraints section.
        """

        constraints = "\n".join(
            f"- {constraint}"
            for constraint in request.constraints
        )

        return (
            "CONSTRAINTS\n"
            "-----------\n"
            f"{constraints}"
        )

    def _context_section(
        self,
        context: ReasoningContext,
    ) -> str:
        """
        Build the runtime context section.
        """

        lines: list[str] = []

        if context.memory is not None:
            diagnostics = (
                context.memory.diagnostics()
            )

            lines.append(
                f"Execution memory: {diagnostics}"
            )

        
        if not lines:
            return ""

        return (
            "RUNTIME CONTEXT\n"
            "---------------\n"
            + "\n".join(lines)
        )

    def _instructions_section(
        self,
    ) -> str:
        """
        Build the reasoning instructions.
        """

        return (
            "INSTRUCTIONS\n"
            "------------\n"
            "1. Analyze the objective.\n"
            "2. Consider all constraints.\n"
            "3. Consider available context.\n"
            "4. Produce the best decision.\n"
            "5. Explain the reasoning.\n"
            "6. Estimate confidence.\n"
            "7. Recommend the next action."
        )

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def diagnostics(
        self,
    ) -> dict[str, object]:
        """
        Return prompt builder diagnostics.
        """

        return {
            "component": "PromptBuilder",
        }