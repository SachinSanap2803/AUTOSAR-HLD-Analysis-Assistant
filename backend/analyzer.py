import json
import re


class HLDAnalyzer:

    def __init__(self, llm):
        self.llm = llm

    def analyze(self, documents, metadatas):

        # ------------------------------------------
        # Build complete HLD context
        # ------------------------------------------

        context_parts = []

        for document, metadata in zip(
            documents,
            metadatas
        ):

            source = metadata["source"]
            page = metadata["page"]

            context_parts.append(
                f"""
SOURCE: {source}
PAGE: {page}

CONTENT:
{document}
"""
            )

        context = "\n\n".join(context_parts)

        # ------------------------------------------
        # Analysis prompt
        # ------------------------------------------

        prompt = f"""
You are an AUTOSAR High-Level Design document
analysis assistant.

Analyze ONLY the HLD document content provided below.

Do not use outside knowledge.
Do not invent components, interfaces, ports,
requirements, or relationships.

If a category is not present in the document,
return an empty array.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "summary": "Short summary of the HLD",
    "components": [
    {{
        "name": "component name",
        "description": "description from document",
        "page": 1
    }}
    ],
    "interfaces": [
    {{
        "name": "interface name",
        "purpose": "purpose from document",
        "page": 1
    }}
    ],
    "ports": [
    {{
        "component": "component name",
        "type": "Required or Provided",
        "name": "port name",
        "page": 1
    }}
    ],
    "functional_flow": [
    {{
        "step": 1,
        "description": "step description",
        "page": 1
    }}
    ],
    "data_flow": [
    {{
        "from": "source",
        "to": "destination",
        "description": "relationship described in document",
        "page": 1
    }}
    ],
    "observations": [
        "Only mention observations directly supported by the HLD."
    ]
}}

HLD DOCUMENT:
========================
{context}
========================
"""

        response = self.llm.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        result = response.text.strip()

        # ------------------------------------------
        # Remove Markdown JSON fences if returned
        # ------------------------------------------

        result = re.sub(
            r"^```json\s*",
            "",
            result
        )

        result = re.sub(
            r"\s*```$",
            "",
            result
        )

        # ------------------------------------------
        # Parse JSON
        # ------------------------------------------

        try:

            analysis = json.loads(result)

        except json.JSONDecodeError as e:

            raise ValueError(
                f"Could not parse LLM analysis as JSON: {e}"
            )

        return analysis