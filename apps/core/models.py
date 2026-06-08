from django.db import models
from django.utils.translation import gettext_lazy as _


class ContentPage(models.Model):
    PAGE_TYPES = [
        ('about', _('About')),
        ('news', _('News')),
        ('vacancy', _('Vacancy')),
        ('review', _('Review')),
        ('press', _('Press')),
        ('tender', _('Tender')),
        ('faq', _('FAQ')),
    ]
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    title_en = models.CharField(max_length=255, blank=True, verbose_name=_('Title (EN)'))
    content = models.TextField(verbose_name=_('Content'))
    content_en = models.TextField(blank=True, verbose_name=_('Content (EN)'))
    meta_description = models.CharField(max_length=500, blank=True, verbose_name=_('Meta description'))
    is_published = models.BooleanField(default=False, verbose_name=_('Published'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, verbose_name=_('Page type'))

    class Meta:
        verbose_name = _('Content page')
        verbose_name_plural = _('Content pages')

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=500, verbose_name=_('Question'))
    question_en = models.CharField(max_length=500, blank=True, verbose_name=_('Question (EN)'))
    answer = models.TextField(verbose_name=_('Answer'))
    answer_en = models.TextField(blank=True, verbose_name=_('Answer (EN)'))
    category = models.CharField(max_length=100, blank=True, verbose_name=_('Category'))
    order = models.IntegerField(default=0, verbose_name=_('Order'))
    is_published = models.BooleanField(default=True, verbose_name=_('Published'))

    class Meta:
        verbose_name = _('FAQ')
        verbose_name_plural = _('FAQs')
        ordering = ['order']

    def __str__(self):
        return self.question


class Review(models.Model):
    author_name = models.CharField(max_length=255, verbose_name=_('Author name'))
    author_company = models.CharField(max_length=255, blank=True, verbose_name=_('Author company'))
    text = models.TextField(verbose_name=_('Text'))
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name=_('Rating'))
    is_approved = models.BooleanField(default=False, verbose_name=_('Approved'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    source = models.CharField(max_length=255, blank=True, verbose_name=_('Source'))

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.author_name} - {self.rating}/5'


class NewsItem(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    title_en = models.CharField(max_length=255, blank=True, verbose_name=_('Title (EN)'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    short_text = models.TextField(verbose_name=_('Short text'))
    short_text_en = models.TextField(blank=True, verbose_name=_('Short text (EN)'))
    full_text = models.TextField(verbose_name=_('Full text'))
    full_text_en = models.TextField(blank=True, verbose_name=_('Full text (EN)'))
    image = models.ImageField(upload_to='uploads/news/', blank=True, verbose_name=_('Image'))
    published_at = models.DateTimeField(verbose_name=_('Published at'))
    is_published = models.BooleanField(default=False, verbose_name=_('Published'))
    is_pinned = models.BooleanField(default=False, verbose_name=_('Pinned to homepage'))

    class Meta:
        verbose_name = _('News item')
        verbose_name_plural = _('News items')
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Vacancy(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    title_en = models.CharField(max_length=255, blank=True, verbose_name=_('Title (EN)'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    department = models.CharField(max_length=255, verbose_name=_('Department'))
    city = models.ForeignKey('geo.City', on_delete=models.SET_NULL, null=True, verbose_name=_('City'))
    short_description = models.TextField(verbose_name=_('Short description'))
    full_description = models.TextField(verbose_name=_('Full description'))
    requirements = models.TextField(verbose_name=_('Requirements'))
    salary_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Salary from'))
    salary_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Salary to'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    published_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Published at'))

    class Meta:
        verbose_name = _('Vacancy')
        verbose_name_plural = _('Vacancies')
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    email = models.EmailField(verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))
    subject = models.CharField(max_length=500, verbose_name=_('Subject'))
    message = models.TextField(verbose_name=_('Message'))
    is_read = models.BooleanField(default=False, verbose_name=_('Read'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    class Meta:
        verbose_name = _('Contact message')
        verbose_name_plural = _('Contact messages')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.subject}'


class Tender(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    description = models.TextField(verbose_name=_('Description'))
    deadline = models.DateTimeField(verbose_name=_('Deadline'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    published_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Published at'))

    class Meta:
        verbose_name = _('Tender')
        verbose_name_plural = _('Tenders')
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Promotion(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    title_en = models.CharField(max_length=255, blank=True, verbose_name=_('Title (EN)'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    short_description = models.TextField(verbose_name=_('Short description'))
    full_description = models.TextField(verbose_name=_('Full description'))
    image = models.ImageField(upload_to='uploads/promotions/', blank=True, verbose_name=_('Image'))
    start_date = models.DateTimeField(verbose_name=_('Start date'))
    end_date = models.DateTimeField(verbose_name=_('End date'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Promotion')
        verbose_name_plural = _('Promotions')
        ordering = ['-start_date']

    def __str__(self):
        return self.title
