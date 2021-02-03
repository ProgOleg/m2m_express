from django.urls import path
from . import views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index_view, name='index_url'),
    path('registration/', views.registration_view, name='registration_url'),
    path('log_out/', views.LogOut.as_view(), name='logout_url'),
    path('login/', views.AuthUser.as_view(), name='login_url'),
    path('password_restoring/', views.password_restoring_view, name='password_restoring_url'),
    path('user_info/', views.UserInfoView.as_view(), name='user_info_url'),
    path('inn_individual_entrepreneur_info/', views.individual_entrepreneur_info, name='indi_entrepr_inn_url'),
    path('select_tariff/', views.select_tariff, name='select_tariff_url'),
    path('delivery/', views.delivery, name='delivery_url'),
    path('get_point_geolocation_pvz/', views.get_point_geolocation_pvz, name='geolocation_pvz'),
    path('get_delivery_cost/', views.get_delivery_cost, name='get_delivery_cost_url'),
    path('order_approval/', views.order_approval, name="order_approval_url"),
    path('order_history/', views.order_history, name="order_history_url"),
    path('repeat_order/', views.repeat_order, name="repeat_order_url"),
    path('context_load/', views.get_context, name="context_loader_url")
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
