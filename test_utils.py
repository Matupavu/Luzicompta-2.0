# test_utils.py

import unittest
from unittest.mock import patch, mock_open
import json
from utils import save_quotation, generate_devis_number, generate_invoice_number

class TestUtils(unittest.TestCase):

    @patch("builtins.open", new_callable=mock_open)
    def test_save_quotation(self, mock_file):
        data = {"key": "value"}
        filename = "test_file.json"
        
        result = save_quotation(data, filename)
        
        mock_file.assert_called_once_with(filename, 'w')
        mock_file().write.assert_called_once_with(json.dumps(data, indent=4))
        self.assertTrue(result)

    @patch("builtins.open", side_effect=Exception("Erreur de test"))
    def test_save_quotation_exception(self, mock_file):
        data = {"key": "value"}
        filename = "test_file.json"
        
        result = save_quotation(data, filename)
        self.assertFalse(result)

    def test_generate_devis_number(self):
        number = generate_devis_number()
        self.assertTrue(number.startswith("DE"))
        self.assertIn("-", number)
        
    def test_generate_invoice_number(self):
        number = generate_invoice_number()
        self.assertTrue(number.startswith("FA"))
        self.assertIn("-", number)

if __name__ == '__main__':
    unittest.main()
