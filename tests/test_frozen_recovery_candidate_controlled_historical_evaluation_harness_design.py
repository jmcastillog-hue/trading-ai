from __future__ import annotations

import ast
import inspect
import unittest
from dataclasses import replace
from pathlib import Path

from src.validation import (
    frozen_recovery_candidate_controlled_historical_evaluation_harness_design_v1
    as design,
)


class ControlledHistoricalEvaluationHarnessDesignTests(unittest.TestCase):
    def test_source_anchors_are_exact(self) -> None:
        root = Path.cwd()
        for relative_path, expected_hash in design.EXPECTED_SOURCE_HASHES.items():
            path = root / relative_path
            self.assertTrue(path.is_file(), relative_path)
            self.assertEqual(
                design.normalized_source_sha256(path),
                expected_hash,
                relative_path,
            )

    def test_source_is_not_runtime_or_data_loader_code(
        self,
    ) -> None:
        import ast as local_ast
        import inspect as local_inspect

        from src.validation import (
            frozen_recovery_candidate_controlled_historical_evaluation_harness_design_v1
            as harness_design
        )

        source = local_inspect.getsource(harness_design)
        tree = local_ast.parse(source)

        imported_modules: list[str] = []
        called_names: list[str] = []

        for node in local_ast.walk(tree):
            if isinstance(node, local_ast.Import):
                imported_modules.extend(
                    alias.name
                    for alias in node.names
                )

            elif isinstance(node, local_ast.ImportFrom):
                imported_modules.append(node.module or "")

            elif isinstance(node, local_ast.Call):
                if isinstance(node.func, local_ast.Name):
                    called_names.append(node.func.id)

                elif isinstance(node.func, local_ast.Attribute):
                    called_names.append(node.func.attr)

        actual_forbidden_imports = sorted(
            {
                module_name
                for module_name in imported_modules
                if any(
                    module_name == prefix
                    or module_name.startswith(prefix + ".")
                    for prefix
                    in harness_design.FORBIDDEN_IMPORT_PREFIXES
                )
            }
        )

        self.assertEqual(actual_forbidden_imports, [])

        forbidden_calls = {
            "read_csv",
            "read_excel",
            "read_parquet",
            "download_binance_klines",
            "download_historical_klines",
            "run_backtest",
            "run_historical_backtest",
        }

        actual_forbidden_calls = sorted(
            set(called_names) & forbidden_calls
        )

        self.assertEqual(actual_forbidden_calls, [])

    def test_manifest_schema_has_exact_twenty_five_fields(self) -> None:
        fields = design.build_manifest_fields()
        self.assertEqual(len(fields), 25)
        self.assertEqual(
            tuple(field.position for field in fields),
            tuple(range(1, 26)),
        )
        self.assertTrue(all(field.immutable_after_binding for field in fields))

    def test_dataset_slots_form_exact_unbound_three_by_three_grid(self) -> None:
        slots = design.build_dataset_slots()
        self.assertEqual(len(slots), 9)
        self.assertEqual(
            {(slot.symbol, slot.timeframe) for slot in slots},
            {
                (symbol, timeframe)
                for symbol in design.SYMBOLS
                for timeframe in design.TIMEFRAMES
            },
        )
        self.assertTrue(all(slot.binding_state == "UNBOUND_DESIGN_ONLY" for slot in slots))
        self.assertTrue(all(slot.relative_path == "" for slot in slots))
        self.assertTrue(all(slot.file_sha256 == "" for slot in slots))
        self.assertTrue(all(not slot.content_read_allowed_in_phase_2i for slot in slots))

    def test_component_graph_is_exact_and_acyclic(self) -> None:
        components = design.build_components()
        self.assertEqual(len(components), 13)
        order = {item.component_id: item.evaluation_order for item in components}
        self.assertTrue(all(
            dependency in order and order[dependency] < item.evaluation_order
            for item in components
            for dependency in item.depends_on
        ))
        self.assertTrue(all(not item.implemented_in_phase_2i for item in components))

    def test_state_machine_blocks_runtime_actions(self) -> None:
        transitions = design.build_state_transitions()
        self.assertEqual(len(transitions), 12)
        runtime_events = {
            "BIND_INPUT_MANIFEST", "READ_MARKET_BYTES",
            "RUN_HISTORICAL_EVALUATION", "OPEN_LOCKBOX",
        }
        self.assertTrue(all(
            not transition.permitted_in_phase_2i
            for transition in transitions
            if transition.event in runtime_events
        ))
        self.assertTrue(all(transition.fail_closed for transition in transitions))

    def test_twenty_failure_modes_are_terminal_fail_closed(self) -> None:
        modes = design.build_failure_modes()
        self.assertEqual(len(modes), 20)
        self.assertTrue(all(mode.terminal_state == "BLOCKED_FAIL_CLOSED" for mode in modes))
        self.assertTrue(all(mode.blocks_all_downstream_stages for mode in modes))

    def test_audit_artifacts_are_future_design_only(self) -> None:
        artifacts = design.build_audit_artifacts()
        self.assertEqual(len(artifacts), 12)
        self.assertTrue(all("phase_10_42r_2k" in item.future_relative_path_template for item in artifacts))
        self.assertTrue(all(not item.write_allowed_in_phase_2i for item in artifacts))
        self.assertTrue(all(item.required_for_future_reproducibility for item in artifacts))

    def test_twenty_four_invariants_are_locked(self) -> None:
        invariants = design.build_invariants()
        self.assertEqual(len(invariants), 24)
        self.assertTrue(all(item.enforced_fail_closed for item in invariants))
        self.assertTrue(all(not item.mutable_after_first_historical_read for item in invariants))

    def test_repair_policy_terminates_recursive_repair_line(self) -> None:
        self.assertIn("NO_NEW_REPAIR_SUBPHASE", design.REPAIR_POLICY)
        self.assertEqual(
            design.FINITE_COMPLETION_ROUTE,
            (
                "2I_HARNESS_DESIGN",
                "2J_INPUT_MANIFEST_BINDING_AND_INTEGRITY",
                "2K_CONTROLLED_KNOWN_EVIDENCE_EVALUATION",
                "2L_INDEPENDENT_RESULT_AUDIT_AND_DISPOSITION",
            ),
        )

    def test_all_permissions_are_false(self) -> None:
        self.assertTrue(design.PERMISSIONS)
        self.assertTrue(all(value is False for value in design.PERMISSIONS.values()))

    def test_design_is_deterministic(self) -> None:
        first = design.build_design()
        second = design.build_design()
        self.assertEqual(first, second)
        self.assertEqual(design.design_sha256(first), design.design_sha256(second))

    def test_tampered_design_is_rejected(self) -> None:
        harness = design.build_design()
        tampered = replace(harness, repair_policy="REPAIR_FOREVER")
        self.assertIn("repair_policy", design.validate_design_object(tampered))

    def test_preflight_passes_without_historical_access(self) -> None:
        result = design.require_valid_harness_design(preflight_only=True)
        summary = result["summary"]
        self.assertEqual(summary["validation_decision"], "PREFLIGHT_PASSED")
        self.assertTrue(summary["validation_passed"])
        self.assertEqual(summary["real_data_content_read_count"], 0)
        self.assertEqual(summary["historical_file_hash_read_count"], 0)
        self.assertEqual(summary["historical_schema_parse_count"], 0)
        self.assertEqual(summary["historical_evaluation_count"], 0)
        self.assertFalse(summary["historical_evaluation_allowed"])

    def test_full_design_freezes_without_runtime_execution(self) -> None:
        result = design.require_valid_harness_design()
        summary = result["summary"]
        self.assertEqual(
            summary["validation_decision"],
            "CONTROLLED_HISTORICAL_EVALUATION_HARNESS_DESIGN_FROZEN",
        )
        self.assertTrue(summary["validation_passed"])
        self.assertTrue(summary["design_frozen"])
        self.assertFalse(summary["harness_implemented"])
        self.assertFalse(summary["repair_cycle_open"])
        self.assertEqual(summary["repair_phase_count"], 0)
        self.assertEqual(summary["manifest_field_count"], 25)
        self.assertEqual(summary["dataset_slot_template_count"], 9)
        self.assertEqual(summary["component_count"], 13)
        self.assertEqual(summary["failure_mode_count"], 20)
        self.assertEqual(summary["audit_artifact_design_count"], 12)
        self.assertEqual(summary["run_invariant_count"], 24)
        self.assertEqual(summary["failed_check_count"], 0)
        self.assertEqual(summary["blocker_count"], 0)
        self.assertEqual(summary["permissions_enabled_count"], 0)
        self.assertEqual(summary["real_data_content_read_count"], 0)
        self.assertEqual(summary["historical_evaluation_count"], 0)
        self.assertEqual(summary["result_artifact_write_count"], 0)

    def test_full_design_is_deterministic(self) -> None:
        first = design.require_valid_harness_design()
        second = design.require_valid_harness_design()
        self.assertEqual(first["summary"], second["summary"])
        self.assertEqual(first["checks"], second["checks"])
        self.assertEqual(first["design"], second["design"])


if __name__ == "__main__":
    unittest.main()
