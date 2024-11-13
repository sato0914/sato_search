from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('search_app.urls')),
)

# メディアファイルのURL設定
if settings.DEBUG:  # 開発環境でのみメディアファイルを提供
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)