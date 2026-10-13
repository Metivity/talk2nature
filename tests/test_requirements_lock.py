import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PIN = re.compile(r"^([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?==([^\s;]+)$")


def read_pins(path):
    pins = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        match = PIN.fullmatch(line)
        if match is None:
            raise AssertionError(f"{path.name}:{line_number} is not an exact version pin")
        name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
        if name in pins:
            raise AssertionError(f"{path.name}:{line_number} repeats {name}")
        pins[name] = match.group(2)
    return pins


class RequirementsLockTests(unittest.TestCase):
    def test_direct_dependencies_match_runtime_lock(self):
        direct = read_pins(ROOT / "admin" / "requirements.txt")
        locked = read_pins(ROOT / "admin" / "requirements.lock")

        for package, version in direct.items():
            with self.subTest(package=package):
                self.assertEqual(locked.get(package), version)


if __name__ == "__main__":
    unittest.main()
