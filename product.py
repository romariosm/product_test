import json
import functools
import logging
from datetime import datetime
from datetime import timedelta

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("PRODUCT")


class DecodeProductAttr(json.JSONDecoder):
    DATETIME_FORMAT: str = "%Y-%m-%d"
    ATTR_CONVERSION: dict = {"updated_at": "datetime"}

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, json_dict):
        for key, value in json_dict.items():
            attr_conversion = self.ATTR_CONVERSION.get(key)
            if attr_conversion == "datetime":
                json_dict[key] = self.parse_datetime(value)
        return json_dict

    def parse_datetime(self, value: str) -> datetime:
        try:
            return datetime.strptime(value, self.DATETIME_FORMAT)
        except Exception as e:
            logger.error(f"Datetime value {value} could not be parsed. Error={e}")


class Product:
    def __init__(self, filename) -> None:
        self.products = self.__open_products(filename)

    def __open_products(self, filename) -> list:
        with open(filename, "r") as p:
            products = json.loads(p.read(), cls=DecodeProductAttr)
            p.close()
            return products

    def sort_by_price(self, products: list = None, asc: bool = False) -> list:
        products = products or self.products
        try:
            return sorted(products, key=lambda p: p["price"], reverse=asc)
        except Exception as e:
            logger.info(f"Error sorting by price. Error={e}")
            return []

    def filter_gte_updated_at(self, date: datetime, products: list = []):
        products = products or self.products
        try:
            return list(filter(lambda p: p["updated_at"] > date, products))
        except Exception as e:
            logger.error(f"Error filtering by updated at. Error={e}")
            return []

    def calculate_avg(self, attr_name: str, products=[]) -> float:
        try:
            products = products or self.products
            return functools.reduce(
                lambda p1, p2: p1 + p2[attr_name], products, 0
            ) / len(products)
        except Exception as e:
            logger.error(f"Error calculating avg. Error={e}")
            return 0.0

    def get_avg_rating_top_expensive(self):
        updated_at_period = datetime.today() - timedelta(days=90)
        last_updated_at_products = self.filter_gte_updated_at(updated_at_period)
        return self.calculate_avg("rating", last_updated_at_products)


if __name__ == "__main__":
    product = Product("product.json")
    logger.info(product.sort_by_price())
    logger.info(product.get_avg_rating_top_expensive())
