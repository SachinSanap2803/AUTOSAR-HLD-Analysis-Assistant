import pandas as pd


class TraceabilityBuilder:

    def __init__(self, analysis):

        self.analysis = analysis or {}

        self.components = self.analysis.get(
            "components",
            []
        )

        self.interfaces = self.analysis.get(
            "interfaces",
            []
        )

        self.ports = self.analysis.get(
            "ports",
            []
        )

        self.functional_flow = self.analysis.get(
            "functional_flow",
            []
        )

        self.data_flow = self.analysis.get(
            "data_flow",
            []
        )

    # ==================================================
    # BUILD TRACEABILITY MATRIX
    # ==================================================

    def build_matrix(self):

        rows = []

        # ------------------------------------------------
        # 1. Build component-based rows
        # ------------------------------------------------

        component_names = []

        for component in self.components:

            name = component.get(
                "name",
                ""
            ).strip()

            if name:
                component_names.append(name)

        # ------------------------------------------------
        # 2. Process every component
        # ------------------------------------------------

        for component_name in component_names:

            # --------------------------------------------
            # Find ports belonging to this component
            # --------------------------------------------

            component_ports = [
                port
                for port in self.ports
                if port.get(
                    "component",
                    ""
                ).strip()
                == component_name
            ]

            # --------------------------------------------
            # Find required ports
            # --------------------------------------------

            required_ports = [
                port.get(
                    "name",
                    ""
                ).strip()

                for port in component_ports

                if port.get(
                    "type",
                    ""
                ).lower()
                == "required"
            ]

            # --------------------------------------------
            # Find provided ports
            # --------------------------------------------

            provided_ports = [
                port.get(
                    "name",
                    ""
                ).strip()

                for port in component_ports

                if port.get(
                    "type",
                    ""
                ).lower()
                == "provided"
            ]

            # --------------------------------------------
            # Find interfaces related to component
            # --------------------------------------------

            related_interfaces = []

            component_text = (
                component_name.lower()
            )

            for interface in self.interfaces:

                interface_name = interface.get(
                    "name",
                    ""
                ).strip()

                interface_purpose = interface.get(
                    "purpose",
                    ""
                ).strip()

                combined_text = (
                    f"{interface_name} "
                    f"{interface_purpose}"
                ).lower()

                if (
                    component_text
                    and component_text in combined_text
                ):

                    related_interfaces.append(
                        interface_name
                    )

            # --------------------------------------------
            # Find functional-flow references
            # --------------------------------------------

            flow_steps = []

            for step in self.functional_flow:

                description = step.get(
                    "description",
                    ""
                ).strip()

                if (
                    component_name.lower()
                    in description.lower()
                ):

                    step_number = step.get(
                        "step",
                        ""
                    )

                    if step_number:

                        flow_steps.append(
                            f"Step {step_number}"
                        )

                    else:

                        flow_steps.append(
                            "Functional Flow"
                        )

            # --------------------------------------------
            # Create row
            # --------------------------------------------

            rows.append({

                "Component": component_name,

                "Required Ports": (
                    ", ".join(required_ports)
                    if required_ports
                    else "—"
                ),

                "Provided Ports": (
                    ", ".join(provided_ports)
                    if provided_ports
                    else "—"
                ),

                "Interfaces": (
                    ", ".join(
                        related_interfaces
                    )
                    if related_interfaces
                    else "—"
                ),

                "Functional Flow": (
                    ", ".join(flow_steps)
                    if flow_steps
                    else "—"
                )
            })

        return rows

    # ==================================================
    # BUILD PORT TRACEABILITY
    # ==================================================

    def build_port_matrix(self):

        rows = []

        for port in self.ports:

            port_name = port.get(
                "name",
                ""
            ).strip()

            component = port.get(
                "component",
                ""
            ).strip()

            port_type = port.get(
                "type",
                ""
            ).strip()

            page = port.get(
                "page",
                ""
            )

            if not port_name:
                continue

            # --------------------------------------------
            # Determine status
            # --------------------------------------------

            same_port = [
                p
                for p in self.ports

                if p.get(
                    "name",
                    ""
                ).strip()
                == port_name
            ]

            has_required = any(
                p.get(
                    "type",
                    ""
                ).lower()
                == "required"

                for p in same_port
            )

            has_provided = any(
                p.get(
                    "type",
                    ""
                ).lower()
                == "provided"

                for p in same_port
            )

            if has_required and has_provided:

                status = "Connected"

            elif port_type.lower() == "required":

                status = "Missing Provider"

            elif port_type.lower() == "provided":

                status = "No Consumer"

            else:

                status = "Unknown"

            rows.append({

                "Port": port_name,

                "Component": component,

                "Type": port_type,

                "Status": status,

                "Page": page
            })

        return rows

    # ==================================================
    # BUILD INTERFACE TRACEABILITY
    # ==================================================

    def build_interface_matrix(self):

        rows = []

        for interface in self.interfaces:

            name = interface.get(
                "name",
                ""
            ).strip()

            purpose = interface.get(
                "purpose",
                ""
            ).strip()

            page = interface.get(
                "page",
                ""
            )

            if not name:
                continue

            # --------------------------------------------
            # Search functional flow
            # --------------------------------------------

            referenced_in_flow = False

            for step in self.functional_flow:

                description = step.get(
                    "description",
                    ""
                )

                if name.lower() in description.lower():

                    referenced_in_flow = True
                    break

            if referenced_in_flow:

                status = "Referenced"

            else:

                status = "Defined Only"

            rows.append({

                "Interface": name,

                "Purpose": purpose,

                "Used in Functional Flow": (
                    "Yes"
                    if referenced_in_flow
                    else "No"
                ),

                "Status": status,

                "Page": page
            })

        return rows

    # ==================================================
    # BUILD COMPLETE TRACEABILITY DATA
    # ==================================================

    def build(self):

        return {

            "component_matrix":
                self.build_matrix(),

            "port_matrix":
                self.build_port_matrix(),

            "interface_matrix":
                self.build_interface_matrix()
        }