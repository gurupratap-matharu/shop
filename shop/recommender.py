import redis
from django.conf import settings

from .models import Product

r = redis.Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)


class Recommender:
    """
    A Naive recommender system that suggest products which are frequently bought together.
    """

    def get_product_key(self, id):
        """Returnt the key of a product in redis format."""

        return f"product:{id}:purchased_with"

    def products_bought(self, products):
        """
        Keep record of products that are bought together in the same order.
        """

        product_ids = [p.id for p in products]

        for product_id in product_ids:

            for with_id in product_ids:

                if product_id != with_id:
                    # Get the key for the product in redis format
                    product_key = self.get_product_key(product_id)

                    # Now increment the count for each companion product bought
                    r.zincrby(product_key, 1, with_id)

    def suggest_products_for(self, products, max_results: int = 6):
        """
        Suggest products that are frequently bought for a given list of products based
        on past data.


        products:
            This is a list of `Product` objects to get recommendations for. It can
            contain one or more products

        max_results:
            This is an integer that represents the maximum number of recommendations to
            return
        """

        product_ids = [p.id for p in products]

        if len(products) == 1:
            # only 1 product
            product_key = self.get_product_key(product_ids[0])
            suggestions = r.zrange(product_key, 0, -1, desc=True)[:max_results]

        else:
            # multiple products are provided so we combine the sorted sets for all the
            # products into a temporary key, do a filtering and then get suggestions.
            # here we go ...

            # 1 Generate a temporary key
            flat_ids = "".join([str(id) for id in product_ids])
            tmp_key = f"tmp_{flat_ids}"

            # 2 Combine scores of all products & store the union set in the tmp_key we created earlier
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(tmp_key, keys)

            # 3 Remove ids for the products the recommendation is for
            # since we can't recommend products for which the recomendation is asked for

            r.zrem(tmp_key, *product_ids)

            # 4 Now basically get suggestion for products by their id as we did above for a single product
            suggestions = r.zrange(tmp_key, 0, -1, desc=True)[:max_results]

            # 5 Remove the temporary key as its no longer needed
            r.delete(tmp_key)

        suggested_products_ids = [int(id) for id in suggestions]

        # Retrive products based on ids
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))

        # Sort the products based on the order of `suggested_product_ids`
        # This is needed as Django .filter query may not return shuffled results
        # TODO... VEER CHECK THIS
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))

        return suggested_products

    def clear_purchases(self):
        """
        Clears all data products bought together across all products. This is basically
        `resetting` the recommender system. We do this by deleting the redis keys for all
        the products.
        """

        for id in Product.objects.values_list("id", flat=True):
            r.delete(self.get_product_key(id))
