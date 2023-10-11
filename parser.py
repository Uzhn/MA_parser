import json

import requests
from bs4 import BeautifulSoup

from core.config import base_url, cookies, domain, headers, params


def parse_urls_tea() -> list[str]:
    """Функция парсит ссылки на все позиции чая в наличии."""
    urls_tea = []
    page_num = 1
    while True:
        response = requests.get(
            base_url, params=params, cookies=cookies, headers=headers
        )
        src = response.text
        soup = BeautifulSoup(src, "lxml")

        products = soup.findAll(
            "div",
            class_="catalog-2-level-product-card product-card"
            " subcategory-or-type__products-item catalog--common"
            " offline-prices-sorting--best-level "
            "with-prices-drop",
        )
        for product in products:
            url_tea = (
                domain
                + product.find("div", class_="product-card__content").find("a")["href"]
            )
            urls_tea.append(url_tea)
        next_page = soup.find(
            "button",
            class_="rectangle-button reset--button-styles "
            "subcategory-or-type__load-more best-blue-outlined "
            "medium normal",
        )
        if next_page:
            page_num += 1
            params["page"] = page_num
        else:
            break
    return urls_tea


def get_data() -> dict[str, dict[str, str | None]]:
    """Функция получает данные о товаре и записывает в словарь."""
    urls_tea = parse_urls_tea()
    headers1 = {
        "user-agent": "Mozilla/5.0 (Linux; Android 10; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4076.0 Mobile Safari/537.36"
    }
    data_dct = {}
    count = 0
    for url_tea in urls_tea:
        try:
            response = requests.get(url=url_tea, headers=headers1, cookies=cookies)
            src = response.text
            soup = BeautifulSoup(src, "lxml")

            article = (
                soup.find("div", class_="product-page-content__rating-and-article")
                .find("p", itemprop="productID", class_="product-page-content__article")
                .text.strip()
            ).split()[1]
            name = (
                soup.find(
                    "h1",
                    class_="product-page-content__product-name "
                    "catalog-heading heading__h2",
                )
                .find("span")
                .text.strip()
            )

            old_price_element = soup.find(
                "span",
                class_="product-price nowrap "
                "product-price-discount-above__old-price "
                "style--product-page-top-separated-old "
                "catalog--common offline-prices-sorting--"
                "best-level",
            )

            if old_price_element:
                base_price_element = (
                    old_price_element.find("span", class_="product-price__sum").find(
                        "span", class_="product-price__sum-rubles"
                    )
                ).text.strip()
                promo_price_element = soup.find(
                    "span",
                    class_="product-price nowrap product-price-"
                    "discount-above__actual-price style--product"
                    "-page-top-separated-actual color--red "
                    "catalog--common offline-prices-sorting--"
                    "best-level",
                )
                promo_price = (
                    promo_price_element.find("span", class_="product-price__sum").find(
                        "span", class_="product-price__sum-rubles"
                    )
                ).text.strip()
            else:
                base_price_element = None
                promo_price = None

            actual_price = (
                soup.find("span", class_="product-price__sum").find(
                    "span", class_="product-price__sum-rubles"
                )
            ).text.strip()

            base_price = base_price_element if base_price_element else actual_price
            brand = (
                soup.find("li", class_="product-attributes__list-item")
                .find("a")
                .text.strip()
            )
            data_dct[article] = {
                "наименование": name,
                "ссылка": url_tea,
                "регулярная_цена": base_price,
                "промо_цена": promo_price,
                "бренд": brand,
            }
            count += 1
            print(f"Записано {count} товаров")
        except AttributeError as err:
            print(f"Произошла ошибка AttributeError: {err}")
    return data_dct


def generate_json_data():
    """Функция записи в JSON."""
    results = get_data()
    with open("results.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
        print("*" * 20)
        print("Загрузка успешно завершена!")
