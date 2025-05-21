"""
URL configuration for ekart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from products import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.shortcuts import render

def custom_404(request, exception):
    return render(request, '404.html', status=404)

handler404 = custom_404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name='home'),
    path('product_list/', views.product_list, name='product_list'),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('user_login/', views.user_login, name='user_login'),
    path('user_logout/',views.user_logout,name='user_logout'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete_cartitem/<int:id>/', views.delete_cartitem, name='delete_cartitem'),
    path('update_account/', views.update_account, name='update_account'),
    path('confirm_address/', views.confirm_address, name='confirm_address'),
    path('place_order/', views.place_order, name='place_order'),
    path('product_details/<int:id>/',views.product_details,name="product_details"),
    path('search/', views.search_products, name='search_products'),
    path('contact/',views.contact,name="contact"),
    path('stripe_payment/', views.stripe_payment, name='stripe_payment')




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
"""
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
"""

