import os
import unittest
from unittest.mock import Mock, MagicMock, patch

import httpx
import pandas as pd
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from main import make_get_request, get_soup, parse_page, get_items_urls_on_page, get_all_products_urls, get_item_name, \
    get_item_price, get_item_description, get_item_rating, manipulate_menu, create_item_dict, get_dataframe, \
    save_to_csv


class TestMakeGetRequest(unittest.TestCase):
    def test_make_get_request(self):
        """
        Проверяет, что функция make_get_request возвращает ответ с кодом 200 при выполнении запроса на указанный URL.
        """

        actual_response = make_get_request('https://goldapple.ru/parfjumerija')
        self.assertEqual(actual_response.status_code, 200)


class TestGetSoup(unittest.TestCase):
    def test_get_soup(self):
        """
        Проверяет, что функция get_soup корректно создает объект BeautifulSoup
        из фиктивного объекта httpx.Response.
        """

        # Создаем фиктивный объект httpx.Response
        fake_html = b"<html><body><p>Hello, World!</p></body></html>"
        fake_response = Mock(spec=httpx.Response, content=fake_html)

        # Вызываем тестируемую функцию
        soup = get_soup(fake_response)

        # Проверяем, что возвращается объект BeautifulSoup
        self.assertIsInstance(soup, BeautifulSoup)


class TestParsePage(unittest.TestCase):
    def test_parse_page(self):
        """Проверяет, что функция parse_page возвращает ожидаемый результат при обработке фейкового HTML-кода."""

        # Создаем фейковый HTML-код для теста
        fake_html = '<html><body><div class="agT1K"><a class="-VFCY G0WXL _5u-Bz mZ52s" href="product1">Product 1</a><a class="-VFCY G0WXL _5u-Bz mZ52s" href="product2">Product 2</a></div></body></html>'
        soup = BeautifulSoup(fake_html, 'html.parser')

        # Вызываем тестируемую функцию
        result = parse_page(soup)

        # Проверяем, что функция возвращает ожидаемый результат
        self.assertIsNotNone(result)
        self.assertEqual(result['class'], ['agT1K'])


class TestGetItemsUrlsOnPage(unittest.TestCase):
    def test_get_items_urls_on_page(self):
        """Проверяет, что функция get_items_urls_on_page находит URL в элементе и добавляет его в список."""

        # Создаем фейковый объект BeautifulSoup для теста
        fake_html = '<html><body><div class="agT1K"><a class="-VFCY G0WXL _5u-Bz mZ52s" href="/product1">Product 1</a><a class="-VFCY G0WXL _5u-Bz mZ52s" href="/product2">Product 2</a></div></body></html>'
        soup = BeautifulSoup(fake_html, 'html.parser')

        # Вызываем тестируемую функцию
        result = get_items_urls_on_page(soup.find_all('div', class_='agT1K'))

        # Проверяем, что функция возвращает ожидаемый результат
        self.assertEqual(result, ['https://goldapple.ru/product1'])


class TestGetAllProductsUrls(unittest.TestCase):
    @patch('main.make_get_request')
    @patch('main.get_soup')
    @patch('main.parse_page')
    @patch('main.get_items_urls_on_page', return_value=["https://goldapple.ru/product1",
                                                        "https://goldapple.ru/product2"])
    def test_get_all_products_urls(self, mock_get_items_urls, mock_parse_page, mock_get_soup, mock_make_get_request):
        """
        Тест проверяет функцию get_all_products_urls, убеждаясь,
        что она возвращает ожидаемый список URL-адресов продуктов.
        """

        mock_make_get_request.return_value.status_code = 200
        result = get_all_products_urls(1, 1)
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
        self.assertEqual(result, 12345.0)

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

    def test_manipulate_menu_application_found(self):
        """Тестирование случая, когда элемент <ПРИМЕНЕНИЕ> найден.

        Создается фиктивный объект driver, возвращающий элемент <ПРИМЕНЕНИЕ>.
        Вызывается функция manipulate_menu с фиктивным driver.
        Проверяется, что значение p_item_instructions равно "ПРИМЕНЕНИЕ", а p_item_country равно "Not available".
        """
        fake_driver = MagicMock()
        fake_menu_item = MagicMock()
        fake_menu_item.text.strip.return_value = "ПРИМЕНЕНИЕ"
        fake_driver.find_element.return_value = fake_menu_item

        p_item_instructions, p_item_country = manipulate_menu(fake_driver)

        self.assertEqual(p_item_instructions, "ПРИМЕНЕНИЕ")
        self.assertEqual(p_item_country, "Not available")

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
