from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('accounts/',include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('adminpanel/',include('adminpanel.urls')),
    path('store/',include('store.urls')),


    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
