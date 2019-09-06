from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

from home.views import custom_page_not_found, custom_server_error, custom_permission_denied, custom_bad_request

from django.conf.urls import include, url

urlpatterns = [
    url(r'admin/', admin.site.urls),
    url(r'', include('home.urls'), ),
    url(r'^user/', include('users.urls'), ),
    url(r'^finance/', include('finance.urls'), ),
    # url(r'^documents/', include('documents.urls'), ),
    # url(r'^message/', include('message.urls'), ),
    # url(r'^others/', include('others.urls'), ),
    # url(r'^settings/', include('settings.urls'), ),
]

handler404 = custom_page_not_found
handler500 = custom_server_error
handler403 = custom_permission_denied
handler400 = custom_bad_request

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
