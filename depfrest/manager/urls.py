from django.urls import path
from .import views

urlpatterns = [
    path('manager_dashboard/',views.manager_dashboard,name='manager_dashboard'),
    path('user_management/',views.user_management,name='user_management'),
    path('category_management/',views.category_management,name='category_management'),
    path('add_category',views.add_category,name='add_category'),
    path('order_management/',views.order_management,name='order_management'),
    path('product_management/',views.product_management,name='product_management'),
    path('variation_management',views.variation_management,name='variation_management'),
    path('admin_orders/', views.admin_order, name='admin_orders'),
    
    path('add_variation/', views.add_variation, name='add_variation'),
    path('update_variation/<int:variation_id>/',views.update_variation,name='update_variation'),
    path('delete_variation/<int:variation_id>/', views.delete_variation, name='delete_variation'),
    
    path('admin_change_password/', views.admin_change_password, name='admin_change_password'),
    
    path('user_ban/<int:user_id>/',views.user_ban,name='user_ban'),
    path('user_unban/<int:user_id>/',views.user_unban,name='user_unban'),
    path('delete_category/<int:category_id>/',views.delete_category,name='delete_category'),
    path('update_category/<int:category_id>/', views.update_category, name="update_category"),
    path('manager_cancel_order/<int:order_number>/', views.manager_cancel_order, name='manager_cancel_order'),
    path('accept_order/<int:order_number>/', views.accept_order, name='accept_order'),
    path('complete_order/<int:order_number>/', views.complete_order, name='complete_order'),
    path('cancel_order/<int:order_number>/', views.cancel_order, name='cancel_order'),
    path('add_product/',views.add_product,name='add_product'),
    path('delete_product/<int:product_id>/',views.delete_product,name='delete_product'),
    path('edit_product/<int:product_id>/',views.edit_product,name='edit_product'),
    
    

    
    
    
   
    


    
    
    
     
]
