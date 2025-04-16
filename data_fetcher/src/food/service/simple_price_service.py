from data_fetcher.src.food.crawler.entities import Prices


class PriceService:

    def calculate_simple_price(prices: Prices):
        """
        Calculate a simple price rating from 1 to 3 based on student pricing.

        :param student_price: A dictionary containing student pricing information
        :return: String rating from € to €€€, or None if conditions are not met
        """
        if not prices.students:
            return None

        base_price = prices.students.base_price
        price_per_unit = prices.students.price_per_unit
        unit = prices.students.unit

        # Ensure base_price is valid
        if base_price is None or (price_per_unit is None and unit is None):
            return None

        # Calculate total price (assuming 100g as a standard portion)
        total_price = base_price + (price_per_unit or 0)

        # Thresholds
        if total_price <= 0.5:
            return "€"  # Cheap
        elif total_price <= 1.6:
            return "€€"  # Moderate
        else:
            return "€€€"  # Expensive
