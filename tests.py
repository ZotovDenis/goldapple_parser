import os
import unittest
from unittest.mock import Mock, MagicMock, patch

import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from main import get_items_urls_on_page, get_all_products_urls, get_item_name, \
    get_item_price, get_item_description, get_item_rating, manipulate_menu, create_item_dict, get_dataframe, \
    save_to_csv, make_selenium_get_request, get_items_class


class TestMakeSeleniumGetRequest(unittest.TestCase):
    def test_make_selenium_get_request(self):
        """
        Тестирование функции make_selenium_get_request на корректное формирование URL и
        вызов метода get у объекта driver.

        Создаем заглушку для объекта driver.
        Затем вызываем тестируемую функцию make_selenium_get_request с URL 'https://example.com' и параметром page=1.
        После этого проверяем, что функция driver.get была вызвана с правильным аргументом 'https://example.com?p=1'.
        """

        driver = Mock()
        make_selenium_get_request('https://goldapple.ru/parfjumerija', driver, page=1)
        driver.get.assert_called_once_with('https://goldapple.ru/parfjumerija?p=1')


class TestGetItemsClass(unittest.TestCase):
    def test_get_items_class(self):
        """
        Тестирование функции get_items_class на корректный поиск элементов на странице.

        Создаем заглушку для объекта driver.
        Затем создаем заглушки для найденных элементов и устанавливаем возвращаемое значение для driver.find_elements.
        После этого вызываем тестируемую функцию get_items_class с объектом driver.
        Проверяем, что функция driver.find_elements была вызвана с правильным аргументом (By.CLASS_NAME, "NiYv1").
        Затем проверяем, что функция возвращает ожидаемый результат - список найденных элементов.
        """

        driver = Mock()

        mock_element1 = Mock()
        mock_element2 = Mock()
        driver.find_elements.return_value = [mock_element1, mock_element2]

        result = get_items_class(driver)

        driver.find_elements.assert_called_once_with(By.CLASS_NAME, "Wqob-")
        self.assertEqual(result, [mock_element1, mock_element2])


class TestGetItemsUrlsOnPage(unittest.TestCase):
    def test_get_items_urls_on_page_handles_exception(self):
        """
        Тестирование функции get_items_urls_on_page на обработку исключения.
        """
        # Создаем фейковый объект WebElement, который вызовет исключение
        fake_element = Mock()
        fake_element.find_element.side_effect = NoSuchElementException

        # Вызываем тестируемую функцию
        result = get_items_urls_on_page([fake_element])

        # Проверяем, что функция обрабатывает исключение и возвращает пустой список
        self.assertEqual(result, [])


class TestGetAllProductsUrls(unittest.TestCase):
    @patch('main.make_selenium_get_request')
    @patch('main.get_items_class')
    @patch('main.get_items_urls_on_page', return_value=["https://goldapple.ru/product1", "https://goldapple.ru/product2"])
    def test_get_all_products_urls(self, mock_get_items_urls, mock_get_items_class, mock_make_selenium_get_request):
        """
        Тест проверяет функцию get_all_products_urls, убеждаясь,
        что она возвращает ожидаемый список URL-адресов продуктов.
        """

        fake_driver = Mock()
        mock_get_items_class.return_value = 'fake_items_class'
        result = get_all_products_urls(fake_driver, 1, 1)
        self.assertEqual(result, ["https://goldapple.ru/product1", "https://goldapple.ru/product2"])


class TestGetItemName(unittest.TestCase):
    def test_get_item_name(self):
        """Проверяет, что функция get_item_name возвращает правильное название товара из элемента страницы."""

        # Создаем фиктивный объект driver
        fake_driver = MagicMock()
        fake_element = MagicMock()
        fake_element.text = "Product Name"
        fake_driver.find_element.return_value = fake_element

        # Вызываем тестируемую функцию
        result = get_item_name(fake_driver)

        # Проверяем, что функция возвращает ожидаемый результат
        self.assertEqual(result, "Product Name")

        # Проверяем, что функция возвращает "Not available" при отсутствии элемента
        fake_driver.find_element.side_effect = NoSuchElementException
        result = get_item_name(fake_driver)
        self.assertEqual(result, "Not available")


class TestGetItemPrice(unittest.TestCase):
    def test_get_item_price(self):
        """Проверяет, что функция get_item_price возвращает правильную цену товара из элемента страницы."""

        # Создаем фиктивный объект driver
        fake_driver = MagicMock()
        fake_element = MagicMock()
        fake_element.text = " 12 345 "
        fake_driver.find_element.return_value = fake_element

        # Вызываем тестируемую функцию
        result = get_item_price(fake_driver)

        # Проверяем, что функция возвращает ожидаемый результат
        self.assertEqual(result, '12 345')

        # Проверяем, что функция возвращает "Not available" при отсутствии элемента
        fake_driver.find_element.side_effect = NoSuchElementException
        result = get_item_price(fake_driver)
        self.assertEqual(result, "Not available")


class TestGetItemDescription(unittest.TestCase):
    def test_get_item_description(self):
        """Проверяет, что функция get_item_description возвращает правильное описание товара из элемента страницы."""

        fake_driver = MagicMock()
        fake_element = MagicMock()
        fake_element.text = "Product description"
        fake_driver.find_element.return_value = fake_element

        result = get_item_description(fake_driver)
        self.assertEqual(result, "Product description")

        fake_driver.find_element.side_effect = NoSuchElementException
        result = get_item_description(fake_driver)
        self.assertEqual(result, "Not available")


class TestGetItemRating(unittest.TestCase):
    def test_get_item_rating(self):
        """Проверяет, что функция get_item_rating возвращает правильный рейтинг товара из элемента страницы."""

        fake_driver = MagicMock()
        fake_element = MagicMock()
        fake_element.text = " 4.8 "
        fake_driver.find_element.return_value = fake_element

        result = get_item_rating(fake_driver)
        self.assertEqual(result, 4.8)

        fake_driver.find_element.side_effect = NoSuchElementException
        result = get_item_rating(fake_driver)
        self.assertEqual(result, "Not available")


class TestManipulateMenu(unittest.TestCase):
    def test_manipulate_menu_brand_found(self):
        """Тестирование случая, когда элемент <О БРЕНДЕ> найден.

        Создается фиктивный объект driver, возвращающий элемент <О БРЕНДЕ>.
        Вызывается функция manipulate_menu с фиктивным driver.
        Проверяется, что значение p_item_instructions равно "Not available", а p_item_country равно "О БРЕНДЕ".
        """
        fake_driver = MagicMock()
        fake_menu_item = MagicMock()
        fake_menu_item.text.strip.return_value = "О БРЕНДЕ"
        fake_driver.find_element.return_value = fake_menu_item

        p_item_instructions, p_item_country = manipulate_menu(fake_driver)

        self.assertEqual(p_item_instructions, "Not available")
        self.assertEqual(p_item_country, "О БРЕНДЕ")

    def test_manipulate_menu_not_found(self):
        """Тестирование случая, когда элемент не найден.

        Создается фиктивный объект driver, который выбрасывает исключение NoSuchElementException.
        Вызывается функция manipulate_menu с фиктивным driver.
        Проверяется, что значение p_item_instructions равно "Not available", а p_item_country
        также равно "Not available".
        """
        fake_driver = MagicMock()
        fake_driver.find_element.side_effect = NoSuchElementException

        p_item_instructions, p_item_country = manipulate_menu(fake_driver)

        self.assertEqual(p_item_instructions, "Not available")
        self.assertEqual(p_item_country, "Not available")


class TestCreateItemDict(unittest.TestCase):
    def test_create_item_dict_with_rating_as_float(self):
        """Тестирование создания словаря товара с рейтингом в виде числа с плавающей точкой."""

        item = create_item_dict(1, "/example.com", "Product 1", 99.99, 4.5,
                                "Description 1", "Instructions 1", "Country 1")

        self.assertEqual(item["number"], 1)
        self.assertEqual(item["link"], "/example.com")
        self.assertEqual(item["name"], "Product 1")
        self.assertEqual(item["price"], 99.99)
        self.assertEqual(item["rating"], 4.5)
        self.assertEqual(item["description"], "Description 1")
        self.assertEqual(item["instructions"], "Instructions 1")
        self.assertEqual(item["country"], "Country 1")

    def test_create_item_dict_with_rating_as_string(self):
        """Тестирование создания словаря товара с рейтингом в виде строки."""

        item = create_item_dict(2, "/example2.com", "Product 2", 149.99, "No rating",
                                "Description 2", "Instructions 2", "Country 2")

        self.assertEqual(item["number"], 2)
        self.assertEqual(item["link"], "/example2.com")
        self.assertEqual(item["name"], "Product 2")
        self.assertEqual(item["price"], 149.99)
        self.assertEqual(item["rating"], "No rating")
        self.assertEqual(item["description"], "Description 2")
        self.assertEqual(item["instructions"], "Instructions 2")
        self.assertEqual(item["country"], "Country 2")


class TestGetDataFrame(unittest.TestCase):
    def test_get_dataframe(self):
        """
        Тестирование функции get_dataframe, которая преобразует список словарей
        в объект DataFrame библиотеки Pandas.
        """

        items_dict = [
            {"number": 1, "name": "Product 1", "price": 99.99},
            {"number": 2, "name": "Product 2", "price": 149.99}
        ]
        expected_dataframe = pd.DataFrame(items_dict)
        result_dataframe = get_dataframe(items_dict)

        self.assertTrue(expected_dataframe.equals(result_dataframe))


class TestSaveToCsv(unittest.TestCase):
    def test_save_to_csv(self):
        """Тестирование функции save_to_csv, которая сохраняет DataFrame в CSV."""

        # Создаем DataFrame для сохранения
        data = {
            "name": ["Product 1", "Product 2"],
            "price": [99.99, 149.99]
        }
        df = pd.DataFrame(data)

        # Указываем временный путь для сохранения файла и сохраняем DataFrame в CSV
        test_path = "test_data.csv"
        save_to_csv(df, test_path)

        # Проверяем, что файл был создан
        self.assertTrue(os.path.exists(test_path))

        # Удаляем временный файл
        os.remove(test_path)


if __name__ == '__main__':
    unittest.main()
