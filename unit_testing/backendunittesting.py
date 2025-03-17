import unittest
from unittest.mock import patch
from backend.backend import console_add_type, console_add_product, console_edit_product

# Dummy controller to simulate Db_Controller
class DummyController:
    def __init__(self):
        self.add_part_type_called = False
        self.add_product_called = False
        self.edit_product_called = False
        self.add_part_type_args = None
        self.add_product_args = None
        self.edit_product_args = None
        self.getter = self.DummyGetter()
        self.db = self.DummyDB()

    def add_part_type(self, name, *specs):
        self.add_part_type_called = True
        self.add_part_type_args = (name, specs)

    def add_product(self, name, type_name, stock, price, manufacturer, *specs):
        self.add_product_called = True
        self.add_product_args = (name, type_name, stock, price, manufacturer, specs)

    def edit_product(self, name, type_name, *fields):
        self.edit_product_called = True
        self.edit_product_args = (name, type_name, fields)

    class DummyGetter:
        def get_specs(self, part_type):
            # Return a valid specs list if part_type is "valid"; otherwise, return empty.
            if part_type == "valid":
                # For example, first spec is a string (1) and second requires an int (2).
                return [("spec1", 1), ("spec2", 2)]
            return []
        
        def get_spec_var_form(self, part_type, field):
            # For testing, assume if field is "spec2", it requires an int.
            if field == "spec2":
                return 2
            return 1

    class DummyDB:
        def exists_in(self, table, column, value):
            # Simulate that only "valid" part types exist.
            return value == "valid"

class TestBackendFunctions(unittest.TestCase):

    def test_console_add_type_cancel(self):
        # User cancels immediately by entering 'x'
        dummy_controller = DummyController()
        inputs = iter(["x"])
        with patch("builtins.input", lambda prompt: next(inputs)):
            console_add_type(dummy_controller)
        self.assertFalse(dummy_controller.add_part_type_called)

    def test_console_add_type_success(self):
        # User enters a valid type name and one spec.
        # Sequence: part type name -> "Type1"
        #           spec name -> "SpecA", then spec type -> "1", then finish spec input with "o"
        dummy_controller = DummyController()
        inputs = iter(["Type1", "SpecA", "1", "o"])
        with patch("builtins.input", lambda prompt: next(inputs)):
            console_add_type(dummy_controller)
        self.assertTrue(dummy_controller.add_part_type_called)
        # Verify that add_part_type was called with the correct arguments.
        self.assertEqual(dummy_controller.add_part_type_args[0], "Type1")
        self.assertEqual(dummy_controller.add_part_type_args[1], (("SpecA", 1),))

    def test_console_add_product_invalid_part_type(self):
        # When an invalid product type is entered (dummy getter returns an empty list),
        # the function should print an error message and not call add_product.
        dummy_controller = DummyController()
        inputs = iter(["Product1", "invalid"])  # "invalid" will produce no specs.
        with patch("builtins.input", lambda prompt: next(inputs)):
            with patch("builtins.print") as mock_print:
                console_add_product(dummy_controller)
                mock_print.assert_any_call("Part type does not exist")
        self.assertFalse(dummy_controller.add_product_called)

    def test_console_add_product_success(self):
        # Simulate a valid product addition.
        # Sequence:
        # - Product name: "Product1"
        # - Product type: "valid" (yields specs: [("spec1", 1), ("spec2", 2)])
        # - Stock: "10" (converted to int 10)
        # - Price: "20" (converted to int 20)
        # - Manufacturer: "Maker"
        # - For spec1 (string): "ValueA"
        # - For spec2 (int): "30" (converted to int 30)
        dummy_controller = DummyController()
        inputs = iter(["Product1", "valid", "10", "20", "Maker", "ValueA", "30"])
        with patch("builtins.input", lambda prompt: next(inputs)):
            with patch("builtins.print"):
                console_add_product(dummy_controller)
        self.assertTrue(dummy_controller.add_product_called)
        expected_specs = (("spec1", "ValueA"), ("spec2", 30))
        self.assertEqual(dummy_controller.add_product_args,
                         ("Product1", "valid", 10, 20, "Maker", expected_specs))

    def test_console_edit_product_invalid_part_type(self):
        # If an invalid product type is entered (dummy db.exists_in returns False),
        # the function should print an error message and not proceed.
        dummy_controller = DummyController()
        inputs = iter(["Product1", "invalid"])
        with patch("builtins.input", lambda prompt: next(inputs)):
            with patch("builtins.print") as mock_print:
                console_edit_product(dummy_controller)
                # Note: The error message in the function is 'Part type does not exist)'
                mock_print.assert_any_call("Part type does not exist)")
        self.assertFalse(dummy_controller.edit_product_called)

    def test_console_edit_product_cancel(self):
        # If the user cancels editing (enters 'x' for field input), no edit should be made.
        dummy_controller = DummyController()
        inputs = iter(["Product1", "valid", "x"])
        with patch("builtins.input", lambda prompt: next(inputs)):
            console_edit_product(dummy_controller)
        self.assertFalse(dummy_controller.edit_product_called)

    def test_console_edit_product_success(self):
        # Simulate a successful edit:
        # Sequence:
        # - Product name: "Product1"
        # - Product type: "valid"
        # - In the edit loop, first field: "stock", then value: "15"
        # - Then second field: "spec2", then value: "25" (converted to int because get_spec_var_form returns 2)
        # - Then finish with "o"
        dummy_controller = DummyController()
        inputs = iter(["Product1", "valid", "stock", "15", "spec2", "25", "o"])
        with patch("builtins.input", lambda prompt: next(inputs)):
            console_edit_product(dummy_controller)
        self.assertTrue(dummy_controller.edit_product_called)
        expected_fields = (("stock", 15), ("spec2", 25))
        self.assertEqual(dummy_controller.edit_product_args,
                         ("Product1", "valid", expected_fields))

if __name__ == '__main__':
    unittest.main()
