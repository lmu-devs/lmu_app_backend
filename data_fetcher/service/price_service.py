
class PriceService:

    def calculate_simple_price(student_price):
        """
        Calculate a simple price rating from 1 to 3 based on student pricing.
        
        :param student_price: A dictionary containing student pricing information
        :return: String rating from € to €€€, or None if conditions are not met
        """
        if not student_price:
            return None
        
        base_price = student_price.get('base_price', 0)
        price_per_unit = student_price.get('price_per_unit')
        unit = student_price.get('unit')

        # Ensure base_price is valid
        if base_price is None or (price_per_unit is None and unit is None):
            return None

        # Calculate total price (assuming 100g as a standard portion)
        total_price = base_price + (price_per_unit or 0)

        # Thresholds
        if total_price <= 1:
            return "€"  # Cheap
        elif total_price <= 2:
            return "€€"  # Moderate
        else:
            return "€€€"  # Expensive