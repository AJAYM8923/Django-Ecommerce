from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login as auth_login,logout
from django.contrib.auth.decorators import login_required
from products.models import Product,Cart,user_address,Order,OrderItem,contact_details
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY
# Create your views here.
def home(request):
    products=Product.objects.all()
    return render(request,'home.html',{"products":products})

    
def product_list(request):
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})

def user_signup(request):
    user=None
    error=None
    if request.POST:
        name=request.POST.get("name")
        username=request.POST.get("username")
        password=request.POST.get("password")
        

        try:
            user=User.objects.create_user(username=username, password=password)
            return redirect('user_login')
        except Exception as e:
            error="Account already exists"

    return render(request,"user_signup.html",{"error":error})

def user_login(request):
    user=None
    error=None
    if request.POST:
        username=request.POST.get("username")
        password=request.POST.get("password")

        
        user=authenticate(username=username,password=password)

        if user:
            auth_login(request,user)
            return redirect("home")
        else:
            error="Invalid credentials"

    return render(request,"user_login.html",{"error":error})

def user_logout(request):
    logout(request)
    return redirect("home")



@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, "cart.html", {"cart_items": cart_items, "total": total})
@login_required
def add_to_cart(request, product_id):
    product_obj = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product_obj)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect("cart")

def delete_cartitem(request, id):
    cart_item = get_object_or_404(Cart, id=id)
    cart_item.delete()
    return redirect("cart")


@login_required
def update_account(request):
    user = request.user
    user_profile = user_address.objects.filter(email=user.email).first()
    user_orders = Order.objects.filter(user=request.user).order_by('-date')  # Fetch user orders
    # Fetch order items for each order and include product names
    for order in user_orders:
        order.items_with_names = OrderItem.objects.filter(order=order).select_related('product')

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # Handling User Update Form (Username and Password)
        if form_type == "user_update":
            new_username = request.POST.get("username")
            new_password = request.POST.get("password")

            if new_username:  # Ensure username is not empty
                user.username = new_username
            
            if new_password:
                user.password = make_password(new_password)  # Encrypt the password

            user.save()
            
            return redirect('update_account')

        # Handling Profile Update Form (User Address Information)
        elif form_type == "profile_update":
            name = request.POST.get("name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            alt_phone = request.POST.get("alt_phone")
            address = request.POST.get("address")
            city = request.POST.get("city")
            pincode = request.POST.get("pincode")
            state = request.POST.get("state")

            if user_profile:
                # Update existing profile
                user_profile.name = name
                user_profile.email = email
                user_profile.phone = phone
                user_profile.alt_phone = alt_phone
                user_profile.address = address
                user_profile.city = city
                user_profile.pincode = pincode
                user_profile.state = state
                user_profile.save()
            else:
                # Create a new profile for the user
                user_profile = user_address.objects.create(
                    user=user,  # Link to user for better relation
                    name=name,
                    email=email,
                    phone=phone,
                    alt_phone=alt_phone,
                    address=address,
                    city=city,
                    pincode=pincode,
                    state=state
                )

            return redirect('update_account')

    return render(request, 'update_account.html', {"user_profile": user_profile,"user_orders": user_orders})

@login_required
def confirm_address(request):
    
    user = request.user
    user_profile = user_address.objects.filter(user=user).order_by('-id').first()  # Always fetch fresh data
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        if user_profile:
            request.session['order_placed'] = True
            return redirect('place_order')
    
    return render(request, 'confirm_address.html', {
        "user_profile": user_profile,
        "cart_items": cart_items,
        "total": total
    })

@login_required
def place_order(request):
    order=None
    if not request.session.get('order_placed'):
        return redirect('home')

    user_profile = user_address.objects.filter(user=request.user).order_by('-id').first()
    
    # Get cart items before clearing
    cart_items = list(Cart.objects.filter(user=request.user))
    total = sum(item.product.price * item.quantity for item in cart_items)
    delivery_date = None
    if cart_items:
        # Create an order and save the delivery date
        order = Order.objects.create(
            user=request.user,
            total=total,
            date=timezone.now(),
            delivery_date=timezone.now() + timedelta(days=10)  # Delivery after 10 days
        )

        # Add order details for each product in cart
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear cart after placing the order
        Cart.objects.filter(user=request.user).delete()

    request.session.pop('order_placed', None)

    return render(request, "place_order.html", {
        "user_profile": user_profile,
        "cart_items": cart_items,  # Pass the list of items to the template
        "total": total,
        "delivery_date": delivery_date if order else None,
        "order": order
    })
def product_details(request,id):
    Product_obj=get_object_or_404(Product,id=id)
    related_products=Product.objects.all()[:4]
    return render(request,"product_details.html",{'Product_obj':Product_obj,'related_products':related_products})

def search_products(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            name__icontains=query
        ) 
    else:
        products = Product.objects.all()

    return render(request, 'search_results.html', {'products': products, 'query': query})

def contact(request):
    if request.POST:
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        # Save the contact details to the database
        contact_obj = contact_details(name=name, email=email, message=message)
        contact_obj.save()

        return redirect('home')
    return render(request,"contact.html")

@login_required
def stripe_payment(request):
    
    cart_items = Cart.objects.filter(user=request.user)
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == "POST":
        try:
            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Stripe expects amount in cents
                currency='usd',
                automatic_payment_methods={"enabled": True},
            )
              # Set order_placed only after successful payment intent
            request.session['order_placed'] = True
            return render(request, "stripe_payment.html", {
                "client_secret": intent.client_secret,
                "total_amount": total_amount,
                "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,  # Pass the publishable key here
            })
        
        except stripe.error.StripeError as e:
            return render(request, "stripe_payment.html", {"error": str(e)})
        
    return render(request, "stripe_payment.html", {
        "total_amount": total_amount,
        "client_secret": None,
        "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,  # Pass the publishable key here
    })
