import re
import unittest

from kf.segments import Edition


class ApparatusIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edition = Edition()
        cls.data = cls.edition.apparatus_data
        cls.variants = cls.data["variants"]

    def test_eyewitness_readings_are_verbatim(self):
        for variant in self.variants:
            for siglum in "BWRC":
                reading = variant["readings"][siglum]
                section = variant.get("reading_sections", {}).get(siglum, variant["section"])
                with self.subTest(variant=variant["id"], witness=siglum):
                    if reading == "om.":
                        continue
                    if "(canc. " in reading:
                        reading = re.sub(r" \(canc\. [^)]+\)", "", reading)
                    self.assertIn(reading, self.edition.reading(section, siglum))

    def test_core_fields_use_declared_values(self):
        valid_sections = set(self.edition.by_id)
        valid_types = set(self.data["metadata"]["criteria"]["types"])
        valid_statuses = set(self.data["metadata"]["fields"]["status"])
        for variant in self.variants:
            with self.subTest(variant=variant["id"]):
                self.assertIn(variant["section"], valid_sections)
                self.assertIn(variant["type"], valid_types)
                self.assertIn(variant["status"], valid_statuses)

    def test_cancellation_notation_is_supported(self):
        for variant in self.variants:
            for siglum, reading in variant["readings"].items():
                if "(canc. " not in reading:
                    continue
                section = variant.get("reading_sections", {}).get(siglum, variant["section"])
                with self.subTest(variant=variant["id"], witness=siglum):
                    self.assertTrue(
                        variant["type"] == "scribal"
                        or "~~" in self.edition.by_id[section].witnesses[siglum].text
                    )

    def test_ids_are_unique_and_contiguous(self):
        ids = [variant["id"] for variant in self.variants]
        numbers = sorted(int(identifier[1:]) for identifier in ids)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(numbers, list(range(1, max(numbers) + 1)))


if __name__ == "__main__":
    unittest.main()
