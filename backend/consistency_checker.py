import re
from difflib import SequenceMatcher


class ConsistencyChecker:

    def __init__(self, analysis):

        self.analysis = analysis

        self.components = analysis.get(
            "components", []
        )

        self.interfaces = analysis.get(
            "interfaces", []
        )

        self.ports = analysis.get(
            "ports", []
        )

        self.functional_flow = analysis.get(
            "functional_flow", []
        )

        self.data_flow = analysis.get(
            "data_flow", []
        )

    # ==================================================
    # NORMALIZATION
    # ==================================================

    def normalize_name(self, name):

        if not name:
            return ""

        name = str(name)

        # BrakePedalSensorSWC
        # ->
        # Brake Pedal Sensor SWC
        name = re.sub(
            r"(?<=[a-z])(?=[A-Z])",
            " ",
            name
        )

        name = re.sub(
            r"[_\-]+",
            " ",
            name
        )

        # Remove SWC suffix
        name = re.sub(
            r"\bSWC\b",
            "",
            name,
            flags=re.IGNORECASE
        )

        name = re.sub(
            r"\s+",
            " ",
            name
        )

        return name.strip().lower()

    # ==================================================
    # COMPONENT MATCHING
    # ==================================================

    def component_matches(
        self,
        reference,
        defined_component
    ):

        ref = self.normalize_name(
            reference
        )

        component = self.normalize_name(
            defined_component
        )

        if not ref or not component:
            return False

        if ref == component:
            return True

        if (
            ref in component
            or component in ref
        ):
            return True

        ref_tokens = set(
            ref.split()
        )

        component_tokens = set(
            component.split()
        )

        if not ref_tokens or not component_tokens:
            return False

        common_tokens = (
            ref_tokens & component_tokens
        )

        smaller_size = min(
            len(ref_tokens),
            len(component_tokens)
        )

        if (
            smaller_size > 0
            and len(common_tokens) / smaller_size >= 0.75
        ):
            return True

        similarity = SequenceMatcher(
            None,
            ref,
            component
        ).ratio()

        return similarity >= 0.80

    # ==================================================
    # FIND COMPONENT
    # ==================================================

    def find_component(
        self,
        reference,
        defined_components
    ):

        for component in defined_components:

            if self.component_matches(
                reference,
                component
            ):
                return component

        return None

    # ==================================================
    # GET COMPONENTS
    # ==================================================

    def get_component_names(self):

        return [
            component.get(
                "name",
                ""
            ).strip()

            for component in self.components

            if component.get("name")
        ]

    # ==================================================
    # GET INTERFACES
    # ==================================================

    def get_interface_names(self):

        return {
            interface.get(
                "name",
                ""
            ).strip()

            for interface in self.interfaces

            if interface.get("name")
        }

    # ==================================================
    # ADD FINDING
    # ==================================================

    def add_finding(
        self,
        findings,
        severity,
        category,
        finding,
        evidence,
        page,
        recommendation,
        status="Requires Review"
    ):

        findings.append({

            "severity": severity,

            "category": category,

            "finding": finding,

            "evidence": evidence,

            "page": page,

            "recommendation": recommendation,

            "status": status
        })

    # ==================================================
    # 1. COMPONENT CONSISTENCY
    # ==================================================

    def check_component_references(
        self,
        findings
    ):

        defined_components = (
            self.get_component_names()
        )

        if not defined_components:
            return

        # ----------------------------------------------
        # Check data-flow component references
        # ----------------------------------------------

        for item in self.data_flow:

            source = item.get(
                "from",
                ""
            ).strip()

            destination = item.get(
                "to",
                ""
            ).strip()

            page = item.get(
                "page"
            )

            if source:

                source_match = self.find_component(
                    source,
                    defined_components
                )

                if not source_match:

                    self.add_finding(
                        findings,
                        "MEDIUM",
                        "Component Consistency",
                        (
                            f"'{source}' is referenced "
                            f"in the data flow but is not "
                            f"defined in the Software "
                            f"Components section."
                        ),
                        (
                            f"Data flow references "
                            f"'{source}' as a source."
                        ),
                        page,
                        (
                            f"Verify whether '{source}' "
                            f"should be formally defined "
                            f"as a software component."
                        )
                    )

            if destination:

                destination_match = (
                    self.find_component(
                        destination,
                        defined_components
                    )
                )

                if not destination_match:

                    self.add_finding(
                        findings,
                        "MEDIUM",
                        "Component Consistency",
                        (
                            f"'{destination}' is referenced "
                            f"in the data flow but is not "
                            f"defined in the Software "
                            f"Components section."
                        ),
                        (
                            f"Data flow references "
                            f"'{destination}' as a destination."
                        ),
                        page,
                        (
                            f"Verify whether '{destination}' "
                            f"should be formally defined "
                            f"as a software component."
                        )
                    )

    # ==================================================
    # 2. INTERFACE CONSISTENCY
    # ==================================================

    def check_interface_references(
        self,
        findings
    ):

        defined_interfaces = (
            self.get_interface_names()
        )

        for step in self.functional_flow:

            description = step.get(
                "description",
                ""
            )

            page = step.get(
                "page"
            )

            referenced_interfaces = re.findall(
                r"\b[A-Za-z][A-Za-z0-9]*Interface\b",
                description
            )

            for interface in referenced_interfaces:

                if interface not in defined_interfaces:

                    self.add_finding(
                        findings,
                        "MEDIUM",
                        "Interface Consistency",
                        (
                            f"'{interface}' is referenced "
                            f"in the functional flow but "
                            f"is not defined in the "
                            f"Software Interfaces section."
                        ),
                        (
                            f"Functional flow references "
                            f"'{interface}'."
                        ),
                        page,
                        (
                            f"Verify whether '{interface}' "
                            f"was omitted from the Software "
                            f"Interfaces section."
                        )
                    )

    # ==================================================
    # 3. PORT CONSISTENCY
    # ==================================================

    def check_port_consistency(
        self,
        findings
    ):

        port_map = {}

        for port in self.ports:

            name = port.get(
                "name",
                ""
            ).strip()

            port_type = port.get(
                "type",
                ""
            ).strip()

            component = port.get(
                "component",
                ""
            ).strip()

            page = port.get(
                "page"
            )

            if not name:
                continue

            if name not in port_map:

                port_map[name] = {
                    "required": [],
                    "provided": []
                }

            if port_type.lower() == "required":

                port_map[name][
                    "required"
                ].append({
                    "component": component,
                    "page": page
                })

            elif port_type.lower() == "provided":

                port_map[name][
                    "provided"
                ].append({
                    "component": component,
                    "page": page
                })

        # ----------------------------------------------
        # Evaluate ports
        # ----------------------------------------------

        for port_name, information in (
            port_map.items()
        ):

            required = information[
                "required"
            ]

            provided = information[
                "provided"
            ]

            # ------------------------------------------
            # PASS
            # ------------------------------------------

            if required and provided:

                required_component = (
                    required[0]["component"]
                )

                provided_component = (
                    provided[0]["component"]
                )

                self.add_finding(
                    findings,
                    "PASS",
                    "Port Consistency",
                    (
                        f"Port '{port_name}' has a "
                        f"documented provider and "
                        f"consumer."
                    ),
                    (
                        f"Required by "
                        f"'{required_component}' "
                        f"and provided by "
                        f"'{provided_component}'."
                    ),
                    provided[0]["page"],
                    (
                        f"No action required. "
                        f"'{port_name}' has both "
                        f"required and provided "
                        f"definitions."
                    ),
                    status="Verified"
                )

            # ------------------------------------------
            # REQUIRED BUT NO PROVIDER
            # ------------------------------------------

            elif required and not provided:

                component = (
                    required[0]["component"]
                )

                page = required[0]["page"]

                self.add_finding(
                    findings,
                    "HIGH",
                    "Port Consistency",
                    (
                        f"Port '{port_name}' is required "
                        f"by '{component}' but no provider "
                        f"is documented."
                    ),
                    (
                        f"Required port '{port_name}' "
                        f"is listed for '{component}', "
                        f"but no corresponding provided "
                        f"port was identified."
                    ),
                    page,
                    (
                        f"Identify and document the "
                        f"provider of '{port_name}', "
                        f"or verify whether the required "
                        f"port definition is correct."
                    )
                )

            # ------------------------------------------
            # PROVIDED BUT NO CONSUMER
            # ------------------------------------------

            elif provided and not required:

                component = (
                    provided[0]["component"]
                )

                page = provided[0]["page"]

                self.add_finding(
                    findings,
                    "LOW",
                    "Port Consistency",
                    (
                        f"Port '{port_name}' is provided "
                        f"by '{component}' but no required "
                        f"consumer is documented."
                    ),
                    (
                        f"Provided port '{port_name}' "
                        f"has no corresponding required "
                        f"port in the analyzed HLD."
                    ),
                    page,
                    (
                        f"Verify whether '{port_name}' "
                        f"should have a documented "
                        f"consumer."
                    )
                )

    # ==================================================
    # 4. DATA FLOW CONSISTENCY
    # ==================================================

    def check_data_flow(
        self,
        findings
    ):

        defined_components = (
            self.get_component_names()
        )

        for item in self.data_flow:

            source = item.get(
                "from",
                ""
            ).strip()

            destination = item.get(
                "to",
                ""
            ).strip()

            description = item.get(
                "description",
                ""
            )

            page = item.get(
                "page"
            )

            if not source or not destination:
                continue

            source_match = self.find_component(
                source,
                defined_components
            )

            destination_match = (
                self.find_component(
                    destination,
                    defined_components
                )
            )

            # ------------------------------------------
            # PASS
            # ------------------------------------------

            if (
                source_match
                and destination_match
            ):

                self.add_finding(
                    findings,
                    "PASS",
                    "Data Flow",
                    (
                        f"Data flow from "
                        f"'{source_match}' to "
                        f"'{destination_match}' "
                        f"uses defined components."
                    ),
                    description,
                    page,
                    (
                        "No action required. "
                        "Both data-flow endpoints "
                        "are defined."
                    ),
                    status="Verified"
                )

            # ------------------------------------------
            # MISSING SOURCE / DESTINATION
            # ------------------------------------------

            else:

                missing = []

                if not source_match:
                    missing.append(source)

                if not destination_match:
                    missing.append(destination)

                self.add_finding(
                    findings,
                    "MEDIUM",
                    "Data Flow",
                    (
                        "Data flow references "
                        "component(s) that are not "
                        "defined in the Software "
                        "Components section: "
                        + ", ".join(missing)
                    ),
                    description,
                    page,
                    (
                        "Verify that all data-flow "
                        "endpoints are formally "
                        "documented as components."
                    )
                )

    # ==================================================
    # RUN ALL CHECKS
    # ==================================================

    def run_all_checks(self):

        findings = []

        self.check_component_references(
            findings
        )

        self.check_interface_references(
            findings
        )

        self.check_port_consistency(
            findings
        )

        self.check_data_flow(
            findings
        )

        # ----------------------------------------------
        # Summary
        # ----------------------------------------------

        summary = {

            "total": len(findings),

            "pass": sum(
                1
                for finding in findings
                if finding["severity"]
                == "PASS"
            ),

            "high": sum(
                1
                for finding in findings
                if finding["severity"]
                == "HIGH"
            ),

            "medium": sum(
                1
                for finding in findings
                if finding["severity"]
                == "MEDIUM"
            ),

            "low": sum(
                1
                for finding in findings
                if finding["severity"]
                == "LOW"
            )
        }

        return {

            "summary": summary,

            "findings": findings
        }