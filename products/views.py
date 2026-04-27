from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.forms import CategoryForm, ProductForm
from products.models import Category, Product
from products.repositories.product_repository import ProductRepository
from users.decorators import admin_required


@login_required
def product_list(request):
    term = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "").strip()
    queryset = ProductRepository.search(term)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    paginator = Paginator(queryset, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "products/product_list.html",
        {
            "page_obj": page_obj,
            "term": term,
            "category_id": category_id,
            "categories": Category.objects.filter(is_active=True),
        },
    )


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk)
    return render(request, "products/product_detail.html", {"product": product})


@admin_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"Producto creado: {product.name}")
        return redirect(product)
    return render(request, "products/product_form.html", {"form": form, "title": "Nuevo producto"})


@admin_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"Producto actualizado: {product.name}")
        return redirect(product)
    return render(request, "products/product_form.html", {"form": form, "title": "Editar producto"})


@admin_required
@require_POST
def product_deactivate(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = False
    product.save(update_fields=["is_active", "updated_at"])
    messages.success(request, f"Producto desactivado: {product.name}")
    return redirect("product_list")


@admin_required
def category_list(request):
    categories = Category.objects.prefetch_related("products").order_by("name")
    return render(request, "products/category_list.html", {"categories": categories})


@admin_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"Categoria creada: {category.name}")
        return redirect("category_list")
    return render(request, "products/category_form.html", {"form": form})

