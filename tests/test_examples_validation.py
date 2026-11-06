#!/usr/bin/env python3
"""
Tests for validating example instances against the AWS ontology.
"""

import sys
import unittest
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.base_test import BaseOntologyTest

try:
    from rdflib import OWL, RDF, RDFS

    RDFLIB_AVAILABLE = True
except ImportError:
    RDFLIB_AVAILABLE = False


@unittest.skipUnless(RDFLIB_AVAILABLE, "rdflib not available")
class TestExamplesValidation(BaseOntologyTest):
    """Test validation of example instances."""

    def setUp(self):
        """Set up test environment."""
        super().setUp()
        # Load examples and combined graphs using base class methods
        self.examples = self.load_examples_graph()
        self.combined = self.load_combined_graph()
        # Alias for backward compatibility
        self.ontology = self.graph

    def test_examples_file_exists(self):
        """Test that examples file exists and is readable."""
        self.assertTrue(self.examples_file.exists(), "Examples file not found")
        self.assertGreater(len(self.examples), 0, "Examples file is empty")

    def test_example_instances_have_types(self):
        """Test that all example instances have proper types."""
        # Get all subjects that are not classes or properties
        subjects = set()

        for s, _p, _o in self.examples:
            # Skip if subject is a class or property
            if (s, RDF.type, OWL.Class) in self.ontology:
                continue
            if (s, RDF.type, OWL.ObjectProperty) in self.ontology:
                continue
            if (s, RDF.type, OWL.DatatypeProperty) in self.ontology:
                continue

            subjects.add(s)

        # Check that each subject has at least one type
        for subject in subjects:
            types = list(self.examples.objects(subject, RDF.type))
            self.assertGreater(len(types), 0, f"Instance {subject} has no type declaration")

    def test_instance_types_exist_in_ontology(self):
        """Test that instance types are defined in the ontology."""
        # Get all type assertions from examples
        for _subject, predicate, obj in self.examples:
            if predicate == RDF.type:
                # Check if the type is defined as a class in the ontology
                if str(obj).startswith("https://w3id.org/arango-solutions/aws-ontology#"):
                    self.assertTrue(
                        (obj, RDF.type, OWL.Class) in self.ontology,
                        f"Type {obj} used in examples but not defined as class in ontology",
                    )

    def test_property_usage_consistency(self):
        """Test that properties used in examples are defined in ontology."""
        # Get all properties used in examples
        example_properties = set()
        for _s, p, _o in self.examples:
            if p != RDF.type and p != RDFS.label and p != RDFS.comment:
                example_properties.add(p)

        # Check that each property is defined in ontology
        for prop in example_properties:
            if str(prop).startswith("https://w3id.org/arango-solutions/aws-ontology#"):
                is_object_prop = (prop, RDF.type, OWL.ObjectProperty) in self.ontology
                is_data_prop = (prop, RDF.type, OWL.DatatypeProperty) in self.ontology

                self.assertTrue(
                    is_object_prop or is_data_prop,
                    f"Property {prop} used in examples but not defined in ontology",
                )

    def test_iam_examples_structure(self):
        """Test IAM-specific example structure."""
        # Test that IAM users have proper relationships
        iam_users = list(self.examples.subjects(RDF.type, self.aws.IAMUser))

        for user in iam_users:
            # Users should have at least a label
            labels = list(self.examples.objects(user, RDFS.label))
            self.assertGreater(len(labels), 0, f"IAM user {user} should have a label")

    def test_policy_document_format(self):
        """Test that policy documents are properly formatted."""
        # Find all policy instances
        policies = []
        for policy_class in [
            self.aws.IAMPolicy,
            self.aws.AWSManagedPolicy,
            self.aws.CustomerManagedPolicy,
            self.aws.InlinePolicy,
        ]:
            policies.extend(list(self.examples.subjects(RDF.type, policy_class)))

        for policy in policies:
            policy_docs = list(self.examples.objects(policy, self.aws.policyDocument))

            if policy_docs:  # If policy document exists
                policy_doc = str(policy_docs[0])

                # Basic JSON structure check
                self.assertTrue(
                    policy_doc.strip().startswith("{"),
                    f"Policy document for {policy} should start with '{{'",
                )
                self.assertTrue(
                    policy_doc.strip().endswith("}"),
                    f"Policy document for {policy} should end with '}}'",
                )

                # Should contain Version
                self.assertIn(
                    '"Version"', policy_doc, f"Policy document for {policy} should contain Version"
                )

                # Should contain Statement
                self.assertIn(
                    '"Statement"',
                    policy_doc,
                    f"Policy document for {policy} should contain Statement",
                )

    def test_aws_account_structure(self):
        """Test AWS account structure in examples."""
        accounts = list(self.examples.subjects(RDF.type, self.aws.AWSAccount))

        self.assertGreater(len(accounts), 0, "Should have at least one AWS account example")

        for account in accounts:
            # Account should have a label
            labels = list(self.examples.objects(account, RDFS.label))
            self.assertGreater(len(labels), 0, f"AWS account {account} should have a label")

    def test_regional_structure(self):
        """Test regional structure in examples."""
        regions = list(self.examples.subjects(RDF.type, self.aws.AWSRegion))

        if regions:  # If we have region examples
            for region in regions:
                # Region should have availability zones
                azs = list(self.examples.objects(region, self.aws.hasAvailabilityZone))
                self.assertGreater(len(azs), 0, f"Region {region} should have availability zones")

                # Each AZ should be properly typed
                for az in azs:
                    az_types = list(self.examples.objects(az, RDF.type))
                    self.assertIn(
                        self.aws.AvailabilityZone,
                        az_types,
                        f"AZ {az} should be typed as AvailabilityZone",
                    )

    def test_data_property_values(self):
        """Test that data property values are appropriate."""
        # Test maxSessionDuration values
        for subject in self.examples.subjects(self.aws.maxSessionDuration, None):
            values = list(self.examples.objects(subject, self.aws.maxSessionDuration))
            for value in values:
                try:
                    duration = int(value)
                    self.assertGreater(duration, 0, "maxSessionDuration should be positive")
                    self.assertLessEqual(
                        duration, 43200, "maxSessionDuration should not exceed 12 hours"
                    )
                except ValueError:
                    self.fail(f"maxSessionDuration value {value} is not a valid integer")

    def test_no_broken_references(self):
        """Test that there are no broken references in examples."""
        # Check object property references
        for s, p, o in self.examples:
            # If it's an object property and object starts with our namespace
            if (p, RDF.type, OWL.ObjectProperty) in self.ontology:
                if str(o).startswith("https://w3id.org/arango-solutions/aws-ontology#"):
                    # Object should exist as a subject somewhere
                    referenced_subjects = list(self.examples.subjects(None, None))
                    self.assertIn(
                        o,
                        referenced_subjects,
                        f"Broken reference: {s} {p} {o} - {o} not found as subject",
                    )

    def test_effective_access_levels_pair_with_parent(self):
        """REQ-045: each specific access level is asserted alongside hasEffectiveAccess.

        Consumers that don't apply RDFS reasoning (SPARQL without entailment, the ArangoDB
        import) only find access recorded through the parent property.
        """
        parent = self.aws["hasEffectiveAccess"]
        levels = set(self.ontology.transitive_subjects(RDFS.subPropertyOf, parent)) - {parent}
        self.assertGreaterEqual(len(levels), 5, "Expected one sub-property per access level")

        unpaired = [
            (s, level, o)
            for level in levels
            for s, o in self.examples.subject_objects(level)
            if (s, parent, o) not in self.examples
        ]
        self.assertEqual(unpaired, [], "Access levels asserted without hasEffectiveAccess")

    def test_consistent_labeling(self):
        """Test that examples have consistent labeling."""
        # All instances should have labels
        instances = set()

        # Get all instances (subjects that have types but are not classes/properties)
        for s, p, o in self.examples:
            if p == RDF.type:
                if (o, RDF.type, OWL.Class) in self.ontology:
                    instances.add(s)

        for instance in instances:
            labels = list(self.examples.objects(instance, RDFS.label))
            self.assertGreater(len(labels), 0, f"Instance {instance} should have a label")


def run_examples_validation():
    """Run all example validation tests."""
    if not RDFLIB_AVAILABLE:
        print("❌ rdflib not available. Install with: pip install rdflib")
        return False

    suite = unittest.TestLoader().loadTestsFromTestCase(TestExamplesValidation)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    print("Running example validation tests...")
    success = run_examples_validation()

    if success:
        print("\n✅ All example validation tests passed!")
        exit(0)
    else:
        print("\n❌ Some example validation tests failed!")
        exit(1)
