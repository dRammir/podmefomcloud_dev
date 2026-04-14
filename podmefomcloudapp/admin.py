from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Track, Like


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('avatar', 'bio')}),
    )


class TrackProxy(Track):
    class Meta:
        proxy = True
        verbose_name = 'Трек на модерации'
        verbose_name_plural = 'Треки на модерации'


class TrackRejectedProxy(Track):
    class Meta:
        proxy = True
        verbose_name = 'Отклонённый трек'
        verbose_name_plural = 'Отклонённые треки'


@admin.register(Track)
class ApprovedTrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'status_display', 'category', 'likes_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'artist__username')
    ordering = ('-created_at',)
    raw_id_fields = ('artist',)
    readonly_fields = ('created_at', 'updated_at', 'status_display')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'artist', 'description', 'category')
        }),
        ('Файлы', {
            'fields': ('audio', 'cover')
        }),
        ('Статистика', {
            'fields': ('likes_count',)
        }),
        ('Время', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return Track.objects.filter(status='approved')
    
    def has_add_permission(self, request):
        return False
    
    def status_display(self, obj):
        return 'Одобрен'
    status_display.short_description = 'Статус'


@admin.register(TrackProxy)
class PendingTrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'category', 'likes_count', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'artist__username')
    ordering = ('-created_at',)
    raw_id_fields = ('artist',)
    readonly_fields = ('created_at', 'updated_at', 'status_display')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'artist', 'description', 'category')
        }),
        ('Файлы', {
            'fields': ('audio', 'cover')
        }),
        ('Модерация', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Время', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_selected', 'reject_selected']
    
    def get_queryset(self, request):
        return Track.objects.filter(status='pending')
    
    def has_add_permission(self, request):
        return False
    
    def status_display(self, obj):
        return 'На рассмотрении'
    status_display.short_description = 'Статус'
    
    def approve_selected(self, request, queryset):
        count = Track.objects.filter(id__in=queryset.values_list('id', flat=True)).update(status='approved')
        self.message_user(request, f'Одобрено {count} треков')
    approve_selected.short_description = 'Одобрить выбранные'
    
    def reject_selected(self, request, queryset):
        count = Track.objects.filter(id__in=queryset.values_list('id', flat=True)).update(status='rejected', rejection_reason='Отклонён администратором')
        self.message_user(request, f'Отклонено {count} треков')
    reject_selected.short_description = 'Отклонить выбранные'


@admin.register(TrackRejectedProxy)
class RejectedTrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'status_display', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'artist__username')
    ordering = ('-created_at',)
    raw_id_fields = ('artist',)
    readonly_fields = ('created_at', 'updated_at', 'status_display')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'artist', 'description', 'category')
        }),
        ('Файлы', {
            'fields': ('audio', 'cover')
        }),
        ('Модерация', {
            'fields': ('status', 'rejection_reason')
        }),
        ('Время', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_selected']
    
    def get_queryset(self, request):
        return Track.objects.filter(status='rejected')
    
    def has_add_permission(self, request):
        return False
    
    def status_display(self, obj):
        return 'Отклонён'
    status_display.short_description = 'Статус'
    
    def approve_selected(self, request, queryset):
        count = Track.objects.filter(id__in=queryset.values_list('id', flat=True)).update(status='approved', rejection_reason='')
        self.message_user(request, f'Одобрено {count} треков')
    approve_selected.short_description = 'Одобрить выбранные'


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'track', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'track')
