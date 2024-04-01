from datetime import datetime
from typing import Dict
from django.views import generic
from django.db.models import Q

from product.models import ProductVariant, Variant, Product


class CreateProductView(generic.CreateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ListProductView(generic.ListView):
    template_name = 'products/list.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.filter(self.get_filter()).prefetch_related("productvariantprice_set").distinct().order_by("-created_at")

    def get_filter(self) -> Dict:
        qs_filter = Q()

        if title := self.title:
            qs_filter &= Q(title__icontains=title)

        if variant := self.variant:
            print(variant)
            qs_filter &= Q(
                Q(productvariantprice__product_variant_one__variant_title=variant)
                | Q(productvariantprice__product_variant_two__variant_title=variant)
                | Q(productvariantprice__product_variant_three__variant_title=variant)
            )

        if price_from := self.price_from:
            qs_filter &= Q(productvariantprice__price__gte=price_from)

        if price_to := self.price_to:
            qs_filter &= Q(productvariantprice__price__lte=price_to)

        if self.date:
            qs_filter &= Q(created_at__date=datetime.strptime(self.date, '%Y-%m-%d').date())

        return qs_filter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["paginate_by"] = self.paginate_by
        context["variant_options"] = self.get_select_options()

        return context

    def get_select_options(self):
        """
        Note that this solution is not advisable as it will cause performance issues when Product Variant
        table becomes too large. Using distinct() would help but is not a proper solution. Would require
        changing the models or use enums  to define variant types.
        """

        variants = Variant.objects.filter(active=True).values_list("title", flat=True)
        product_variants = ProductVariant.objects.all().select_related("variant").values("variant__title", "variant_title")
        distinct_product_variants = [dict(t_pv) for t_pv in {tuple(pv.items()) for pv in product_variants}]
        select_options = {variant: [] for variant in variants}

        for product_variant in distinct_product_variants:
            select_options[product_variant["variant__title"]].append(product_variant["variant_title"])

        return select_options

    @property
    def title(self):
        return self.request.GET.get("title", "")

    @property
    def variant(self):
        return self.request.GET.get("variant", "")

    @property
    def price_from(self):
        return self.request.GET.get("price_from", "")

    @property
    def price_to(self):
        return self.request.GET.get("price_to", "")

    @property
    def date(self):
        return self.request.GET.get("date", "")
