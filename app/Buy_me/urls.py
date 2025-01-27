"""
URL configuration for rest_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from django.conf import settings
from django.conf.urls.static import static
from apps.shop.views import ShopApiDetailView, ShopApiList, BasketViewSet, BasketShowApi
from rest_framework import routers

router = routers.SimpleRouter()
router.register(r'', BasketViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path("api/v1/shopslist", ShopApiList.as_view()),
    path("api/v1/shopsdetail/<int:pk>/", ShopApiDetailView.as_view()),
    path("api/v1/basket/", include(router.urls)),
    path("api/v1/basketadd/<int:pk>/", BasketViewSet.as_view({'post':'add_basket_item'})),
    path("api/v1/basketupdate/<int:pk>/", BasketViewSet.as_view({'put':'update_basket_item'})),
    path("api/v1/basketshow/", BasketViewSet.as_view({'get':"show_basket"})),
    path("api/v1/basketdelete/<int:pk>/", BasketViewSet.as_view({'delete':'delete_basket_item'})),
    path("api-auth/", include("rest_framework.urls")),
    path("users/", include("apps.users.urls")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)