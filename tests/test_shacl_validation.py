#!/usr/bin/env python3
"""
SHACL validation tests for the AWS Resource Ontology.

Closed-world checks over ontology/examples.ttl using ontology/aws.shapes.ttl.
Complements the OWL open-world reasoning tests: OWL restrictions can never name
a specific individual as wrong, only "not enough information" — SHACL can.
"""

import sys
import unittest
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rdflib import RDF, BNode, Graph
from rdflib.namespace import SH

from utils.common import get_ontology_files, get_project_root, load_ontology_graph

try:
    from pyshacl import validate

    PYSHACL_AVAILABLE = True
except ImportError:
    PYSHACL_AVAILABLE = False


@unittest.skipUnless(PYSHACL_AVAILABLE, "pyshacl not available")
class TestSHACLValidation(unittest.TestCase):
    """Validate example instances against ontology/aws.shapes.ttl."""

    @classmethod
    def setUpClass(cls):
        project_root = get_project_root()
        cls.shapes_file = project_root / "ontology" / "aws.shapes.ttl"
        _, _, examples_file = get_ontology_files()

        ontology_graph = load_ontology_graph(project_root / "ontology" / "aws.ttl", "turtle")
        examples_graph = load_ontology_graph(examples_file, "turtle")
        cls.data_graph = ontology_graph + examples_graph

        cls.shapes_graph = load_ontology_graph(cls.shapes_file, "turtle")
        self_check = cls.shapes_graph is not None
        if not self_check:
            raise RuntimeError(f"Failed to load SHACL shapes from {cls.shapes_file}")

    def run_validation(self):
        conforms, results_graph, results_text = validate(
            self.data_graph,
            shacl_graph=self.shapes_graph,
            ont_graph=None,
            inference=None,
            abort_on_first=False,
            allow_infos=True,
            allow_warnings=True,
        )
        return conforms, results_graph, results_text

    def test_no_violations(self):
        """No sh:Violation-severity shape may be broken by current example data.

        Warning-severity shapes (known, tracked data-completeness gaps — see
        ontology/aws.shapes.ttl header) are deliberately excluded from this gate.
        """
        conforms, _, results_text = self.run_validation()
        self.assertTrue(
            conforms,
            f"SHACL validation reported at least one Violation-severity result:\n{results_text}",
        )

    def test_shapes_file_is_valid_turtle(self):
        self.assertIsNotNone(self.shapes_graph)
        self.assertGreater(len(self.shapes_graph), 0)


@unittest.skipUnless(PYSHACL_AVAILABLE, "pyshacl not available")
class TestSecurityShapesRejectBadData(unittest.TestCase):
    """REQ-044: the security-analysis shapes must reject data that breaks AWS's limits.

    test_no_violations only shows that valid examples pass; these cases show each limit
    actually fires, and that valid edge cases (system tags, typed literals) still pass.
    """

    PREFIXES = (
        "@prefix : <https://w3id.org/arango-solutions/aws-ontology#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
    )

    @classmethod
    def setUpClass(cls):
        project_root = get_project_root()
        cls.ontology_graph = load_ontology_graph(project_root / "ontology" / "aws.ttl", "turtle")
        cls.shapes_graph = load_ontology_graph(
            project_root / "ontology" / "aws.shapes.ttl", "turtle"
        )
        if cls.ontology_graph is None or cls.shapes_graph is None:
            raise RuntimeError("Failed to load the ontology or the SHACL shapes")

    def shape_name(self, shape) -> str:
        """Local name of the node shape that owns a (possibly blank-node) property shape."""
        if isinstance(shape, BNode):
            shape = self.shapes_graph.value(predicate=SH.property, object=shape) or shape
        return str(shape).split("#")[-1]

    def results(self, turtle: str) -> set[tuple[str, str | None, str, str]]:
        """Validate a data snippet; return (focus node, path, severity, node shape) names."""
        data = self.ontology_graph + Graph().parse(data=self.PREFIXES + turtle, format="turtle")
        _, results_graph, _ = validate(
            data,
            shacl_graph=self.shapes_graph,
            inference=None,
            allow_infos=True,
            allow_warnings=True,
        )
        found = set()
        for result in results_graph.subjects(RDF.type, SH.ValidationResult):
            path = results_graph.value(result, SH.resultPath)
            found.add(
                (
                    str(results_graph.value(result, SH.focusNode)).split("#")[-1],
                    str(path).split("#")[-1] if path is not None else None,
                    str(results_graph.value(result, SH.resultSeverity)).split("#")[-1],
                    self.shape_name(results_graph.value(result, SH.sourceShape)),
                )
            )
        return found

    def test_lambda_has_at_most_one_execution_role(self):
        found = self.results(
            ":Fn a :LambdaFunction ; :hasExecutionRole :RoleA, :RoleB . "
            ":RoleA a :IAMRole . :RoleB a :IAMRole ."
        )
        self.assertIn(("Fn", "hasExecutionRole", "Violation", "LambdaFunctionShape"), found)

    def test_lambda_without_execution_role_warns(self):
        found = self.results(":Fn a :LambdaFunction .")
        self.assertIn(("Fn", "hasExecutionRole", "Warning", "LambdaFunctionShape"), found)

    def test_ec2_instance_has_at_most_one_instance_profile(self):
        found = self.results(
            ":Vm a :EC2Instance ; :hasInstanceProfile :P1, :P2 . "
            ":P1 a :IAMInstanceProfile . :P2 a :IAMInstanceProfile ."
        )
        self.assertIn(("Vm", "hasInstanceProfile", "Violation", "EC2InstanceShape"), found)

    def test_instance_profile_has_at_most_one_role(self):
        found = self.results(
            ":P a :IAMInstanceProfile ; :hasRole :RoleA, :RoleB . "
            ":RoleA a :IAMRole . :RoleB a :IAMRole ."
        )
        self.assertIn(("P", "hasRole", "Violation", "IAMInstanceProfileShape"), found)

    TAG_LIMIT = ("Bucket", None, "Violation", "TaggedResourceShape")

    def tagged_bucket(self, user_tags: int, system_prefixes: tuple[str, ...] = ()) -> str:
        lines = [":Bucket a :S3Bucket ."]
        for i in range(user_tags):
            lines.append(f':Bucket :hasTag :U{i} . :U{i} a :Tag ; :tagKey "team{i}" .')
        for i, prefix in enumerate(system_prefixes):
            lines.append(
                f':Bucket :hasTag :S{i} . :S{i} a :Tag ; :tagKey "{prefix}cloudformation:k{i}" .'
            )
        return "\n".join(lines)

    def test_more_than_50_user_tags_is_rejected(self):
        found = self.results(self.tagged_bucket(user_tags=51))
        self.assertIn(self.TAG_LIMIT, found)

    def test_system_tags_do_not_count_toward_the_limit(self):
        found = self.results(self.tagged_bucket(user_tags=50, system_prefixes=("aws:",) * 5))
        self.assertNotIn(self.TAG_LIMIT, found)

    def test_reserved_prefix_is_case_insensitive(self):
        """AWS reserves aws: in any letter case, so AWS: and Aws: keys are system tags too."""
        found = self.results(self.tagged_bucket(user_tags=50, system_prefixes=("AWS:", "Aws:")))
        self.assertNotIn(self.TAG_LIMIT, found)

    def test_tag_key_and_value_lengths(self):
        found = self.results(
            f':Long a :Tag ; :tagKey "{"k" * 129}" . '
            f':BigValue a :Tag ; :tagKey "owner" ; :tagValue "{"v" * 257}" . '
            ':NoKey a :Tag ; :tagValue "x" . '
            ':EmptyValue a :Tag ; :tagKey "owner" ; :tagValue "" .'
        )
        self.assertIn(("Long", "tagKey", "Violation", "TagShape"), found)
        self.assertIn(("BigValue", "tagValue", "Violation", "TagShape"), found)
        self.assertIn(("NoKey", "tagKey", "Violation", "TagShape"), found)
        self.assertFalse([r for r in found if r[0] == "EmptyValue"])

    def test_access_level_must_be_one_of_five(self):
        found = self.results(
            ':Bad a :Action ; :accessLevel "Admin" . '
            ':Typed a :Action ; :accessLevel "Read"^^xsd:string . '
            ':Plain a :Action ; :accessLevel "Permissions management" .'
        )
        self.assertIn(("Bad", "accessLevel", "Violation", "ActionShape"), found)
        self.assertFalse([r for r in found if r[0] in ("Typed", "Plain")])

    def test_publicly_accessible_must_be_boolean(self):
        found = self.results(':Bucket a :S3Bucket ; :isPubliclyAccessible "yes" .')
        self.assertIn(
            ("Bucket", "isPubliclyAccessible", "Violation", "PubliclyAccessibleShape"), found
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
