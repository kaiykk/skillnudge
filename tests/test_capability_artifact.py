import hashlib
import unittest

from skillnudge.capability_artifact import CapabilityArtifactError, validate_capability_artifact


def artifact(content="Check the result before reporting.", *, version="v1", capability_id="check-result"):
    return {
        "schema_version": "native.capability-artifact.v0",
        "capability_id": capability_id,
        "version": version,
        "type": "instruction",
        "exact_content": content,
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
    }


class CapabilityArtifactTests(unittest.TestCase):
    def test_valid_artifact_is_normalized(self):
        value = validate_capability_artifact(artifact())
        self.assertEqual(value["version"], "v1")

    def test_bad_hash_rejected(self):
        value = artifact()
        value["sha256"] = "0" * 64
        with self.assertRaises(CapabilityArtifactError):
            validate_capability_artifact(value)

    def test_unsupported_type_rejected(self):
        value = artifact()
        value["type"] = "plugin"
        with self.assertRaises(CapabilityArtifactError):
            validate_capability_artifact(value)

    def test_extra_mutation_field_rejected(self):
        value = artifact()
        value["parent_sha256"] = "0" * 64
        with self.assertRaises(CapabilityArtifactError):
            validate_capability_artifact(value)


if __name__ == "__main__":
    unittest.main()
