from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from members import views


urlpatterns = [

    # ── Publiques ──────────────────────────────
    path("",                views.index,           name="index"),
    path("register/",       views.register,        name="register"),
    path("login/",          views.login,           name="login"),
    path("logout/",         views.logout,          name="logout"),

    # ── Dashboard ──────────────────────────────
    path("accueil/",        views.accueil,         name="accueil"),

    # ── Produits ───────────────────────────────
    path("produits/",                       views.product_list,     name="product_list"),
    path("produits/nouveau/",              views.product_create,   name="product_create"),
    path("produits/<int:pk>/modifier/",    views.product_edit,   name="product_edit"),
    path("produits/<int:pk>/supprimer/",   views.product_delete,   name="product_delete"),
    path("produits/<int:pk>/mouvement/",   views.movement_create,  name="movement_create"),
    path("produits/<int:pk>/historique/",   views.historique,  name="historique"),

    # ── Catégories ─────────────────────────────
    path("categories/",     views.category_list,   name="category_list"),
    path("categories/<int:pk>/supprimer/",   views.category_delete,   name="category_delete"),

]