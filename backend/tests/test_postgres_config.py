import os
import importlib
import unittest


class TestPostgresConfig(unittest.TestCase):
    def test_normalizes_postgres_scheme(self):
        original = os.environ.get("DATABASE_URL")
        try:
            os.environ["DATABASE_URL"] = "postgres://u:p@localhost:5432/janmitra"
            config = importlib.import_module("config")
            importlib.reload(config)
            self.assertTrue(config.Config.SQLALCHEMY_DATABASE_URI.startswith("postgresql://"))
        finally:
            if original is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = original

    def test_default_is_postgres(self):
        original = os.environ.get("DATABASE_URL")
        try:
            os.environ.pop("DATABASE_URL", None)
            config = importlib.import_module("config")
            importlib.reload(config)
            self.assertTrue(config.Config.SQLALCHEMY_DATABASE_URI.startswith("postgresql://"))
        finally:
            if original is not None:
                os.environ["DATABASE_URL"] = original


if __name__ == "__main__":
    unittest.main()
