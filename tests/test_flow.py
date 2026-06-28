import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from autoflow import Flow, StepFailedError, step


class FlowTests(unittest.TestCase):
    def test_flow_merges_step_results_into_context(self):
        flow = (
            Flow("signup")
            .add(lambda ctx: {"email": ctx["email"].lower()})
            .add(lambda ctx: {"slug": ctx["email"].split("@")[0]})
        )

        result = flow.run({"email": "ADA@EXAMPLE.COM"})

        self.assertEqual(result.get("email"), "ada@example.com")
        self.assertEqual(result.get("slug"), "ada")
        self.assertEqual([event.name for event in result.events], [
            "flow_started",
            "step_started",
            "step_finished",
            "step_started",
            "step_finished",
            "flow_finished",
        ])

    def test_non_mapping_result_is_stored_as_last_value(self):
        flow = Flow().add(lambda ctx: 42)

        result = flow.run()

        self.assertEqual(result.get("_"), 42)

    def test_step_retries_before_failing(self):
        attempts = {"count": 0}

        @step(retries=2)
        def unstable(ctx):
            attempts["count"] += 1
            raise RuntimeError("temporary")

        with self.assertRaises(StepFailedError) as raised:
            Flow().add(unstable).run()

        self.assertEqual(attempts["count"], 3)
        self.assertEqual(raised.exception.step_name, "unstable")
        self.assertEqual(raised.exception.attempts, 3)
        self.assertIn("flow_failed", [event.name for event in raised.exception.events])
        self.assertEqual(
            [event.metadata["next_attempt"] for event in raised.exception.events if event.name == "step_retrying"],
            [2, 3],
        )

    def test_retry_can_recover(self):
        attempts = {"count": 0}

        @step(retries=1)
        def sometimes(ctx):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise RuntimeError("not yet")
            return {"ok": True}

        result = Flow().add(sometimes).run()

        self.assertTrue(result.get("ok"))
        self.assertEqual(attempts["count"], 2)

    def test_step_decorator_can_be_used_without_parentheses(self):
        @step
        def mark(ctx):
            return {"marked": True}

        result = Flow().add(mark).run()

        self.assertTrue(result.get("marked"))

    def test_step_decorator_accepts_positional_name(self):
        @step("custom_name")
        def mark(ctx):
            return {"marked": True}

        result = Flow().add(mark).run()

        self.assertEqual(result.events_named("step_finished")[0].step, "custom_name")

    def test_result_reports_step_elapsed_time(self):
        result = Flow().add(lambda ctx: {"ok": True}).run()

        self.assertGreaterEqual(result.elapsed, 0)
        self.assertEqual(len(result.events_named("step_finished")), 1)

    def test_initial_context_must_be_mapping(self):
        with self.assertRaises(TypeError):
            Flow().run(["not", "a", "mapping"])


if __name__ == "__main__":
    unittest.main()
