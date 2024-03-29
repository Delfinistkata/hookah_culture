"""
Django shortcuts and utility
imports for the 'products' app.
This module includes commonly
used functions and classes from
Django for handling views,redirects,
messages, authentication decorators,
database queries, pagination, and form
handling related to the 'products' app.
"""
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Lower
from django.db.models import Avg
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category
from .forms import ProductForm


def all_products(request):
    """
    A view to show all products, including sorting and search queries.
    """
    products = Product.objects.all().order_by('id')
    query = None
    categories = None
    sort = None
    direction = None
    paginate_by = 6

    if request.GET:
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'rating':
                products = products.annotate(
                    avg_rating=Coalesce(Avg('reviews__rating'), 0.0)
                )
                sortkey = 'avg_rating'
            if sortkey == 'name':
                sortkey = 'lower_name'
                products = products.annotate(lower_name=Lower('name'))
            if sortkey == 'category':
                sortkey = 'category__name'

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(
                    request,
                    "You didn't enter any search criteria!"
                )
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | \
                Q(description__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    # Pagination
    paginator = Paginator(products, paginate_by)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """
    A view to show individual product details.
    """
    product = get_object_or_404(Product, pk=product_id)
    category_id = product.category.id
    products_related = Product.objects.all().filter(category=category_id).order_by('id')

    # Pagination
    products_per_page = 3
    page = request.GET.get('page', 1)
    paginator = Paginator(products_related, products_per_page)
    try:
        products_related = paginator.page(page)
    except PageNotAnInteger:
        products_related = paginator.page(1)
    except EmptyPage:
        products_related = paginator.page(paginator.num_pages)

    context = {
        'product': product,
        'products_related': products_related
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def add_product(request):
    """
    Add a product to the store.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners/admins can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request,
                'Failed to add product. Please ensure the form is valid.'
            )
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """
    Edit a product in the store.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners/admins can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(
                request,
                'Failed to update product. Please ensure the form is valid.'
            )
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    """
    Delete a product from the store.
    """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners/admins can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products'))
