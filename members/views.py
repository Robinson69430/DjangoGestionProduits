from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count, Q, F
import re

from .models import Product, Category, StockMovement
from django.contrib.auth import get_user_model
User = get_user_model()




def index(request):
    return render(request, "index.html")



def register(request):
    if request.user.is_authenticated:
        return redirect("accueil")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name",  "").strip()
        email      = request.POST.get("email",      "").strip().lower()
        password   = request.POST.get("password",   "")
        print(password)
        errors = []

        if not first_name or not last_name:
            errors.append("Le prénom et le nom sont obligatoires.")

        try:
            validate_email(email)
        except ValidationError:
            errors.append("L'adresse email n'est pas valide.")

        if User.objects.filter(email=email).exists():
            errors.append("Cet email est déjà utilisé.")

        errors.extend(_validate_password(password))

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, "register.html", {
                "first_name": first_name,
                "last_name":  last_name,
                "email":      email,
            })

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        auth_login(request, user)
        messages.success(request, f"Bienvenue {first_name} ! Votre compte a été créé.")
        return redirect("accueil")

    return render(request, "register.html")

def login(request):
    if request.user.is_authenticated:
        return redirect("accueil")

    if request.method == "POST":
        email    = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")

        user = authenticate(request, email=email, password=password)  

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Bon retour, {user.first_name} !")
            next_url = request.GET.get("next", "accueil")
            return redirect(next_url)
        else:
            messages.error(request, "Email ou mot de passe incorrect.")

    return render(request, "login.html")


def logout(request):
    if request.method == "POST":
        auth_logout(request)
        messages.info(request, "Vous avez été déconnecté.")
    return redirect("login")



@login_required(login_url="login")
def accueil(request):
    products  = Product.objects.filter(user=request.user)
    low_stock = products.filter(quantity__lte=F("min_alert"))

    context = {
        "total_products"  : products.count(),
        "low_stock_count" : low_stock.count(),
        "low_stock"       : low_stock[:5],
        "total_value"     : products.aggregate(
                                v=Sum(F("quantity") * F("price"))
                            )["v"] or 0,
    }
    return render(request, "accueil.html", context)


@login_required(login_url="login")
def product_list(request):
    products = Product.objects.filter(user=request.user).select_related("category")
    return render(request, "products/list.html", {"products": products})


@login_required(login_url="login")
def product_create(request):
    categories = Category.objects.filter(user=request.user)

    if request.method == "POST":
        name      = request.POST.get("name", "").strip()
        quantity  = int(request.POST.get("quantity", 0))
        min_alert = int(request.POST.get("min_alert", 5))
        price     = request.POST.get("price", 0)
        cat_id    = request.POST.get("category") or None  # ← '' devient None

        if not name:
            messages.error(request, "Le nom du produit est obligatoire.")
        else:
            category = Category.objects.filter(id=cat_id, user=request.user).first() if cat_id else None

            Product.objects.create(
                user      = request.user,
                name      = name,
                quantity  = quantity,
                min_alert = min_alert,
                price     = price,
                category  = category,
            )
            messages.success(request, f"Produit « {name} » créé.")
            return redirect("product_list")

    return render(request, "products/form.html", {"categories": categories})




@login_required(login_url="login")
def product_edit(request, pk):

    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.filter(user=request.user)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        price = request.POST.get("price", 0)
        category_id = request.POST.get("category")

        product.name = name
        product.price = price

        if category_id:
            product.category_id = category_id

        product.save()


        return redirect('product_edit', pk=product.pk)

    return render(request, "products/edit.html", {"product": product, "categories":categories})

@login_required(login_url="login")
def product_delete(request, pk):
    product = Product.objects.filter(pk=pk, user=request.user).first()
    if not product:
        messages.error(request, "Produit introuvable.")
        return redirect("product_list")

    if request.method == "POST":
        product.delete()
        messages.success(request, "Produit supprimé.")
    return redirect("product_list")


@login_required(login_url="login")
def category_delete(request, pk):
    category = Product.objects.filter(pk=pk, user=request.user).first()
    if not category:
        messages.error(request, "Catgégorie introuvable")
        return redirect("category_list")

    if request.method == "POST":
        category.delete()
        messages.success(request, "Catégorie supprimé")
    return redirect("category_list")


@login_required(login_url="login")
def movement_create(request, pk):
    product = Product.objects.filter(pk=pk, user=request.user).first()
    if not product:
        messages.error(request, "Produit introuvable.")
        return redirect("product_list")

    if request.method == "POST":
        mov_type = request.POST.get("type")
        quantity = int(request.POST.get("quantity", 0))
        note     = request.POST.get("note", "").strip()

        if quantity <= 0:
            messages.error(request, "La quantité doit être supérieure à 0.")
        elif mov_type == StockMovement.EXIT and quantity > product.quantity:
            messages.error(request, "Stock insuffisant pour cette sortie.")
        else:
            StockMovement.objects.create(
                product=product, 
                type=mov_type, 
                quantity=quantity, 
                note=note
            )

            if mov_type == StockMovement.ENTRY:
                product.quantity += quantity
            else:
                product.quantity -= quantity
            product.save()
            messages.success(request, "Mouvement enregistré.")
            return redirect("product_list")

    return render(request, "products/movement.html", {"product": product})



@login_required(login_url="login")
def historique(request, pk):
    product = Product.objects.filter(pk=pk, user=request.user).first()
    if not product:
        messages.error(request, "Produit introuvable.")
        return redirect("product_list")

    mouvements = StockMovement.objects.filter(product=product).order_by("-date")

    return render(request, "products/historique.html", {
        "product"   : product,
        "mouvements": mouvements,
    })

@login_required(login_url="login")
def category_list(request):
    if request.method == "POST":
        name  = request.POST.get("name", "").strip()
        color = request.POST.get("color", "#6366f1")
        if name:
            Category.objects.create(user=request.user, name=name, color=color)
            messages.success(request, f"Catégorie « {name} » créée.")
        return redirect("category_list")

    categories = Category.objects.filter(user=request.user).annotate(
        product_count=Count("products")
    )
    return render(request, "categories/list.html", {"categories": categories})



def _validate_password(password: str) -> list[str]:
    errors = []
    if len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères.")
    if not any(c.isdigit() for c in password):
        errors.append("Le mot de passe doit contenir au moins un chiffre.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Le mot de passe doit contenir au moins un caractère spécial.")
    return errors