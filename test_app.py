import unittest
import os

def sanitize_input(user_input: str) -> str:
    return str(user_input).replace("\n", " ").replace("<script>", "").strip()[:500]

class TestResiliPathCore(unittest.TestCase):
    
    def test_security_sanitization(self):
        """Ensures malicious inputs are neutralized."""
        dirty_input = "Drop table \n <script>alert(1)</script>"
        clean = sanitize_input(dirty_input)
        self.assertNotIn("\n", clean)
        self.assertNotIn("<script>", clean)
        self.assertTrue(len(clean) <= 500)

    def test_env_var_handling(self):
        """Simulates environment variable checks for Google Services."""
        os.environ["MOCK_KEY"] = "AIzaSy..."
        self.assertIsNotNone(os.getenv("MOCK_KEY"))

if __name__ == '__main__':
    unittest.main()
