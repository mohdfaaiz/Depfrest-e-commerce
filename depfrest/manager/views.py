from django.shortcuts import render,redirect
from accounts.models import Account
from store.models import Product,Variation
from orders.models import Order
from category.models import Category
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ProductForm,VariationForm
from django.contrib.auth.hashers import make_password,check_password
from django.contrib import messages

# Create your views here.
@never_cache
@login_required(login_url='login')
def manager_dashboard(request):
    if request.user.is_superadmin:

        user_count = Account.objects.filter(is_superadmin=False).count()
        product_count = Product.objects.all().count()
        order_count = Order.objects.filter(is_ordered=True).count()
        category_count = Category.objects.all().count

        context = {
            'user_count': user_count,
            'product_count': product_count,
            'order_count' : order_count,
            'category_count' : category_count
        }

        return render(request,'manager/manager_dashboard.html',context)
    else:
        return redirect('home')
    
@never_cache
@login_required(login_url='login')
def user_management(request):
    if request.method == "POST":
      key = request.POST['key']
      users = Account.objects.filter(Q(first_name__startswith=key) | Q(last_name__startswith=key) | Q(username__startswith=key) | Q(email__startswith=key)).order_by('id')
    else:
      users = Account.objects.filter(is_superadmin=False).order_by('id')

    paginator = Paginator(users,10)
    page = request.GET.get('page')
    paged_users = paginator.get_page(page)
    context = {
        'users' : paged_users
    }
    return render(request, 'manager/user_management.html',context)

def user_ban(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = False
    user.save()
    return redirect('user_management')

def user_unban(request, user_id):
    user = Account.objects.get(id=user_id)
    user.is_active = True
    user.save()
    return redirect('user_management')

# Product Management
@never_cache
@login_required(login_url='login')
def product_management(request):
  if request.method == "POST":
    key = request.POST['key']
    products = Product.objects.filter(Q(product_name__startswith=key) | Q(slug__startswith=key) | Q(category__category_name__startswith=key)).order_by('id')
  else:
    products = Product.objects.all().order_by('id')

  paginator = Paginator(products, 10)
  page = request.GET.get('page')
  paged_products = paginator.get_page(page)
  
  context = {
    'products': paged_products
  }
  return render(request, 'manager/product_management.html', context)

# Add Product
@never_cache
@login_required(login_url='login')
def add_product(request):
  if request.method == 'POST':
    form = ProductForm(request.POST, request.FILES)
    if form.is_valid():
        form.save()
        return redirect('product_management')
  else:
    form = ProductForm()
    context = {
      'form': form
    }
    return render(request, 'manager/add_product.html', context)

# Edit Product
@never_cache
@login_required(login_url='manager_login')
def edit_product(request, product_id):
  product = Product.objects.get(id=product_id)
  form = ProductForm(instance=product)
  
  if request.method == 'POST':
    try:
      form = ProductForm(request.POST, request.FILES, instance=product)
      if form.is_valid():
        form.save()
        
        return redirect('product_management')
    
    except Exception as e:
      raise e

  context = {
    'product': product,
    'form': form
  }
  return render(request, 'manager/edit_product.html', context)

# Delete Product
@never_cache
@login_required(login_url='manager_login')
def delete_product(request, product_id):
  product = Product.objects.get(id=product_id)
  product.delete()
  return redirect('product_management')

# Admin change password
@never_cache
@login_required(login_url='login')
def admin_change_password(request):
  if request.method == 'POST':
    current_user = request.user
    current_password = request.POST['current_password']
    password = request.POST['password']
    confirm_password = request.POST['confirm_password']
    
    if password == confirm_password:
      if check_password(current_password, current_user.password):
        if check_password(password, current_user.password):
          messages.warning(request, 'Current password and new password is same')
        else:
          hashed_password = make_password(password)
          current_user.password = hashed_password
          current_user.save()
          messages.success(request, 'Password changed successfully')
      else:
        messages.error(request, 'Wrong password')
    else:
      messages.error(request, 'Passwords does not match')
  
  return render(request, 'manager/admin_password.html')

# Manage Order
@never_cache
@login_required(login_url='login')
def order_management(request):
  if request.method =="POST":
    key = request.POST['key']
    orders = Order.objects.filter(Q(is_ordered=True), Q(order_number_startswith=key) | Q(useremailstartswith=key) | Q(first_name_startswith=key)).order_by('id')
  else:
    orders = Order.objects.filter(is_ordered=True).order_by('id')
    

  context = {
    'orders': orders
  }
  return render(request, 'manager/order_management.html', context)

# Cancel Order
@never_cache
@login_required(login_url='login')
def manager_cancel_order(request, order_number):
  order = Order.objects.get(order_number=order_number)
  order.status = 'Cancelled'
  order.save()
  
  return redirect('order_management')
  

# Accept Order
@never_cache
@login_required(login_url='login')
def accept_order(request, order_number):
  order = Order.objects.get(order_number=order_number)
  order.status = 'Accepted'
  order.save()
  
  return redirect('order_management')

# Complete Order
@never_cache
@login_required(login_url='login')
def complete_order(request, order_number):
  order = Order.objects.get(order_number=order_number)
  order.status = 'Completed'
  order.save()
  
  return redirect('order_management')

def category_management(request):
    categories = Category.objects.all().order_by('id')

    context = {
        'categories' :categories
    }

    return render(request, 'manager/category_management.html',context)


def add_category(request):
    if request.method == 'POST':
        try:
            category_name = request.POST['category_name']
            category_slug = request.POST['category_slug']
            category_description = request.POST['category_description']
            
            categories = Category(
                category_name = category_name,
                slug = category_slug,
                description = category_description
            )
            
            categories.save()
            return redirect('category_management')
        except Exception as e:
            raise e
    return render(request, 'manager/add_category.html')

# Update Category
@never_cache
@login_required(login_url='login')
def update_category(request, category_id):
  try:
    categories = Category.objects.get(id=category_id)
    
    if request.method == 'POST':
      category_name = request.POST['category_name']
      category_slug = request.POST['category_slug']
      category_description = request.POST['category_description']
      
      categories.category_name = category_name
      categories.slug = category_slug
      categories.description = category_description
      categories.save()
      
      return redirect('category_management')
    
    context = {
      'category': categories
    }
    return render(request, 'manager/update_category.html', context)
    
  except Exception as e:
    raise e
    
       

@never_cache
@login_required(login_url='login')
def delete_category(request,category_id):
    categories = Category.objects.get(id=category_id)
    categories.delete()

    return redirect('category_management')
  
  # Manage Variation
@never_cache
@login_required(login_url='login')
def variation_management(request):
  if request.method == 'POST':
    keyword = request.POST['keyword']
    variations = Variation.objects.filter(Q(product_product_namestartswith=keyword) | Q(variation_categorystartswith=keyword) | Q(variation_value_startswith=keyword)).order_by('id')
  
  else:
    variations = Variation.objects.all().order_by('id')
  
  paginator = Paginator(variations, 10)
  page = request.GET.get('page')
  paged_variations = paginator.get_page(page)
  
  context = {
    'variations': paged_variations
  }
  return render(request, 'manager/variation_management.html', context)


# Add Variation
@never_cache
@login_required(login_url='login')
def add_variation(request):
  
  if request.method == 'POST':
    form = VariationForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('variation_management')
  
  else:
    form = VariationForm()
  
  context = {
    'form': form
  }
  return render(request, 'manager/add_variation.html', context)


# Update Variation
@never_cache
@login_required(login_url='login')
def update_variation(request, variation_id):
  variation = Variation.objects.get(id=variation_id)
  
  if request.method == 'POST':
    form = VariationForm(request.POST ,instance=variation)
    if form.is_valid():
      form.save()
      return redirect('variation_management')
  
  else:
    form = VariationForm(instance=variation)
  
  context = {
    'variation': variation,
    'form': form
  }
  return render(request, 'manager/update_variation.html', context)

  #Delete variation
@never_cache
@login_required(login_url='login')
def delete_variation(request, variation_id):
  variation = Variation.objects.get(id=variation_id)
  variation.delete()
  return redirect('variation_management')

# My orders
@login_required(login_url='login')
def admin_order(request):
  current_user = request.user
  
  if request.method == 'POST':
    keyword = request.POST['keyword']
    orders = Order.objects.filter(Q(user=current_user), Q(is_ordered=True), Q(order_number_startswith=keyword) | Q(useremailstartswith=keyword) | Q(first_namestartswith=keyword) | Q(last_namestartswith=keyword) | Q(phone_startswith=keyword)).order_by('-created_at')
    
  else:
    orders = Order.objects.filter(user=current_user, is_ordered=True).order_by('-created_at')
  
  paginator = Paginator(orders, 10)
  page = request.GET.get('page')
  paged_orders = paginator.get_page(page)
  context = {
    'orders': paged_orders,
  }
  return render(request, 'manager/admin_orders.html', context)

# Cancel Order
@never_cache
@login_required(login_url='login')
def cancel_order(request, order_number):
  order = Order.objects.get(order_number=order_number)
  order.status = 'Cancelled'
  order.save()
  
  return redirect('order_management')