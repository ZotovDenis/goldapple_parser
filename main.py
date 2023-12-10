import time

import httpx
import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

URL = "https://goldapple.ru/parfjumerija"
CSV_PATH = "data.csv"

opts = wd.FirefoxOptions()
opts.add_argument("--width=1920")
opts.add_argument("--height=1080")


# ====================================================================================

def main() -> None:
    """Основная функция, которая выполняет сбор данных о продуктах, их обработку и сохранение в CSV-файл."""
    firefox_driver = wd.Firefox(options=opts)

    # print("Загрузка данных...")
    # product_urls = get_all_products_urls(end_page=1)
    # print("Готово! Получено {} товаров.".format(len(product_urls)))

    product_urls = ["https://goldapple.ru/26830400003-dreaming-with-ghosts",
                    "https://goldapple.ru/7430500002-eau-fraiche",
                    "https://goldapple.ru/19000225097"
                    ]

    print("Обработка данных...")
    items_list: list[dict] = []
    item_number = 0
    for _url in product_urls:
        firefox_driver.get(_url)

        time.sleep(1.5)

        item_number: int = item_number + 1
        item_name: str = get_item_name(driver=firefox_driver)
        item_price: float = get_item_price(driver=firefox_driver)
        item_rating: float | str = get_item_rating(driver=firefox_driver)
        item_description: str = get_item_description(driver=firefox_driver)
        item_instructions, item_country = manipulate_menu(driver=firefox_driver)

        items_list.append(create_item_dict(
            number=item_number,
            link=_url,
            name=item_name,
            price=item_price,
            rating=item_rating,
            description=item_description,
            instructions=item_instructions,
            country=item_country
        ))

        print("Товар {} создан!".format(item_name))

    print("Все товары были созданы. Процесс сохранения...")
    items_dataframe = get_dataframe(items_list)
    save_to_csv(items_dataframe, CSV_PATH)
    print("Все товары сохранены в {}".format(CSV_PATH))

    firefox_driver.close()

# ====================================================================================


def make_get_request(url: str, params: dict | None = None) -> httpx.Response:
    """Выполняет HTTP GET-запрос к указанному URL."""
    return httpx.get(
        url, params=params, verify=False, timeout=None
    )


def get_soup(response: httpx.Response) -> bs:
    """Создает объект BeautifulSoup из содержимого HTTP-ответа."""
    return bs(response.content, 'html.parser')


def parse_page(soup: bs) -> bs:
    """
    Ищет элемент <div> с указанным классом в объекте BeautifulSoup
    для последующего получения из него всех ссылок на товары.
    """
    tablet_items_class = soup.find('div', class_=r'hxiVe')
    return tablet_items_class


def get_items_urls_on_page(tablet_items_class_content) -> list:
    """Функция получает элементы товаров и забирает из них ссылки на эти товары."""
    product_urls: list = []
    for item in tablet_items_class_content:
        url = 'https://goldapple.ru' + item.find('a', class_=r'f1gUa HWnwO c1-sc bp3JF').get('href')
        product_urls.append(url)
    return product_urls


def get_all_products_urls(start_page: int = 1, end_page: int = 1) -> list:
    """Функция получает список URL-адресов продуктов с веб-страницы магазина."""
    product_urls: list = []
    for page in range(start_page, end_page + 1):
        # отправление запроса
        response: httpx.Response = make_get_request(URL, params={"p": page})
        # получение html
        all_products_soup: bs = get_soup(response)
        # получение div-ов с карточками продукта
        tablet_items_class: bs = parse_page(all_products_soup)
        # получение списка урлов по продуктам и добавление в общий список
        product_urls += get_items_urls_on_page(tablet_items_class.contents)

        print(f"Страница {page} обработана. Статус {response.status_code}")
        time.sleep(2)
    return product_urls


# ====================================================================================

def get_item_name(driver: wd):
    """Функция осуществляет поиск поле <Название> и парсит соответствующее полю значение."""
    try:
        p_item_name = driver.find_element(
            By.XPATH, '//*[@id="__layout"]/div/main/article/div[4]/div[2]/div/div[2]/div[1]/div/div/div/div[1]')
        return p_item_name.text.strip()
    except NoSuchElementException:
        return "Not available"


def get_item_price(driver: wd):
    """Функция осуществляет поиск поле <Цена> и парсит соответствующее полю значение."""
    try:
        p_item_price = driver.find_element(
            By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[1]/div[1]')
        only_digits_from_value: list[str] = [s for s in p_item_price.text.split() if s.isdigit()]
        float_price: float = float("".join(only_digits_from_value))
        return float_price
    except NoSuchElementException:
        return "Not available"


def get_item_description(driver: wd):
    """Функция осуществляет поиск поле <Описание> и парсит соответствующее полю значение."""
    try:
        p_item_description = driver.find_element(
            By.CLASS_NAME, r'whC8c')
        return p_item_description.text.strip()
    except NoSuchElementException:
        return "Not available"


def get_item_rating(driver: wd) -> float | str:
    """Функция осуществляет поиск поле <Рейтинг> и парсит соответствующее полю значение."""
    try:
        p_item_rating = driver.find_element(
            By.XPATH,
            r'//*[@id="__layout"]/div/main/div[1]/div/div[3]/a[1]/div/div[1]')
        return float(p_item_rating.text.strip())
    except NoSuchElementException:
        return "Not available"


def manipulate_menu(driver: wd):
    """Функция осуществляет поиск полей <О бренде> и <Применение> и парсит соответствующее полю значение."""
    p_item_instructions = "Not available"
    p_item_country = "Not available"

    for i in range(1, 5):
        try:
            driver.find_element(
                By.XPATH,
                f'//*[@id="__layout"]/div/main/article/div[4]/div[2]/div/div[1]/div[1]/div/button[{i}]').click()
            menu_item = driver.find_element(
                By.XPATH, f'//*[@id="__layout"]/div/main/article/div[4]/div[2]/div/div[1]/div[1]/div/button[{i}]/div')

            if menu_item.text.strip() == "ПРИМЕНЕНИЕ":
                p_item_instructions = driver.find_element(
                    By.CLASS_NAME, r'whC8c').text.strip()
            elif menu_item.text.strip() == "О БРЕНДЕ":
                p_item_country = driver.find_element(
                    By.CLASS_NAME, r'jDJBt').text.strip()

        except NoSuchElementException:
            continue

    return p_item_instructions, p_item_country


def create_item_dict(
        number: int, link: str, name: str, price: float = 0, rating: float | str = 0, description: str = "",
        instructions: str = "", country: str = ""
) -> dict[str, str | float]:
    """Функция создает словарь, представляющий отдельный товар с указанными характеристиками."""
    return {
        "number": number,
        "link": link,
        "name": name,
        "price": price,
        "rating": rating,
        "description": description,
        "instructions": instructions,
        "country": country
    }


def get_dataframe(items_dict: list[dict]) -> pd.DataFrame:
    """Функция преобразует список словарей в объект DataFrame библиотеки Pandas."""
    dataframe: pd.DataFrame = pd.DataFrame(items_dict)
    return dataframe


def save_to_csv(df: pd.DataFrame, path: str | None = "data.csv") -> None:
    """Сохранение в CSV-файл."""
    df.to_csv(path, index=False, encoding="utf-8")


if __name__ == '__main__':
    main()
