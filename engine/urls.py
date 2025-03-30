from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('account/', views.account, name='account'),
    path('search/', views.SearchBooksView.as_view(), name='search'),
    path('search/book/<int:id>/', views.book, name='book_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('takebook/<int:id>/', views.takeBook, name='take_book'),
    path('returnbook/<int:id>/', views.returnBook, name='return_book'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
