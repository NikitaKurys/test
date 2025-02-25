from django.contrib import admin
from django.db.models import Q
from django.utils.html import format_html
from .models import Room, MainTable


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('number_room', 'seat_number', 'occupied', 'get_occupied_by_name')
    read_only_fields = ('occupied',)
    search_fields = ('number_room', 'seat_number')
    list_filter = ('number_room',)
    ordering = ('number_room',)


@admin.register(MainTable)
class MainTableAdmin(admin.ModelAdmin):
    list_display = (
        'room', 'name', 'nationality', 'check_in_date', 'summ', 'check_out_date',
        'payment_method', 'number_phone', 'display_photo', 'description', 'update_date', 'name_user'
    )
    search_fields = ('name', 'nationality', 'organization', 'number_phone')
    list_filter = ('payment_method', 'check_in_date', 'check_out_date', 'room')
    ordering = ('room',)
    date_hierarchy = 'check_in_date'
    readonly_fields = ('update_date', 'name_user')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "room":
            obj_id = request.resolver_match.kwargs.get('object_id')
            if obj_id:
                main_table_entry = MainTable.objects.get(pk=obj_id)
                if main_table_entry.room:
                    kwargs["queryset"] = Room.objects.filter(Q(occupied=False) | Q(pk=main_table_entry.room.pk))
                else:
                    kwargs["queryset"] = Room.objects.filter(occupied=False)
            else:
                kwargs["queryset"] = Room.objects.filter(occupied=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.name_user:
            obj.name_user = request.user
        super().save_model(request, obj, form, change)

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if 'name_user' in fields:
            fields.remove('name_user')
        if 'seat_number' in fields:
            fields.remove('seat_number')
        return fields

    def display_photo(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" width="100" height="100" style="cursor: pointer; border: 1px solid #ddd; border-radius: 4px; padding: 5px; transition: transform 0.2s;" '
                'onmouseover="this.style.transform=\'scale(1.1)\'" '
                'onmouseout="this.style.transform=\'scale(1)\'" />'
                '</a>',
                obj.photo.url
            )
        return "Нет фото"

    display_photo.short_description = 'Фото паспорта'

