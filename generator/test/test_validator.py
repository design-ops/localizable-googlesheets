import unittest
from tempfile import gettempdir
from os import path, remove

from localisation.validator import validate, MissingValue

class TestValidator(unittest.TestCase):

    def test_validate(self):
        self.maxDiff = None
        validation_result = validate("en", ['', 'test.example', '', '', 
                                            'test.dynamic.one', 'test.dynamic.two', '', '', 'test.plural',
                                            'test.plural', 'test.plural', '', '', 'example.icecream.toppings.title',
                                            'example.icecream.sauces.title', 'example.icecream.saucesAndToppings.title', 'missing_key'],
                                           ['', 'A test example of a localized string', '', '', 'One argument: ${arg}',
                                           'Two arguments: ${arg1} and ${arg2}', '', '', 'One value in the plural',
                                           '${x} values in the plural', 'No values in the plural', '', '',
                                           'You have ${ice_cream_toppings} on your ice cream', 'You have ${ice_cream_sauces} on your ice cream',
                                           'You have ${ice_cream_toppings} and ${ice_cream_sauces} on your ice cream'])

        self.assertEqual(validation_result.result, {'example.icecream.sauces.title': 'You have ${ice_cream_sauces} on your ice cream',
                                                    'example.icecream.saucesAndToppings.title': 'You have ${ice_cream_toppings} and ${ice_cream_sauces} on your ice cream',
                                                    'example.icecream.toppings.title': 'You have ${ice_cream_toppings} on your ice cream',
                                                    'test.dynamic.one': 'One argument: ${arg}',
                                                    'test.dynamic.two': 'Two arguments: ${arg1} and ${arg2}',
                                                    'test.example': 'A test example of a localized string',
                                                    'test.plural': 'No values in the plural'})
        self.assertEqual(validation_result.missing_keys, [])
        self.assertEqual(validation_result.missing_values, [MissingValue(localisation='en', key='missing_key')])
