from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import ContentPage, FAQ, Review, NewsItem, Vacancy, ContactMessage, Tender, Promotion


@admin.register(ContentPage)
class ContentPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'page_type', 'slug', 'is_published', 'created_at']
    list_filter = ['page_type', 'is_published']
    search_fields = ['title', 'title_en', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {'fields': ['slug', 'page_type', 'is_published']}),
        (_('Russian'), {'fields': ['title', 'content']}),
        (_('English'), {'fields': ['title_en', 'content_en']}),
        (_('SEO'), {'fields': ['meta_description']}),
    ]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_published']
    list_filter = ['category', 'is_published']
    search_fields = ['question', 'question_en', 'answer']
    list_editable = ['order', 'is_published']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author_name', 'author_company', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved']
    search_fields = ['author_name', 'author_company', 'text']
    actions = ['approve_reviews']

    @admin.action(description=_('Approve selected reviews'))
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)


@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'published_at', 'is_published']
    list_filter = ['is_published']
    search_fields = ['title', 'title_en', 'short_text']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    fieldsets = [
        (None, {'fields': ['slug', 'image', 'is_published']}),
        (_('Russian'), {'fields': ['title', 'short_text', 'full_text']}),
        (_('English'), {'fields': ['title_en', 'short_text_en', 'full_text_en']}),
        (_('Publishing'), {'fields': ['published_at']}),
    ]


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'city', 'salary_from', 'salary_to', 'is_active']
    list_filter = ['department', 'is_active']
    search_fields = ['title', 'title_en', 'department']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {'fields': ['slug', 'department', 'city', 'is_active']}),
        (_('Russian'), {'fields': ['title', 'short_description', 'full_description', 'requirements']}),
        (_('English'), {'fields': ['title_en']}),
        (_('Salary'), {'fields': ['salary_from', 'salary_to']}),
    ]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['name', 'email', 'subject', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['name', 'email', 'phone', 'subject', 'message', 'created_at']

    def has_add_permission(self, request):
        return False


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ['title', 'deadline', 'is_active', 'published_at']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'title_en', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = [
        (None, {'fields': ['slug', 'image', 'is_active']}),
        (_('Russian'), {'fields': ['title', 'short_description', 'full_description']}),
        (_('English'), {'fields': ['title_en']}),
        (_('Period'), {'fields': ['start_date', 'end_date']}),
    ]
