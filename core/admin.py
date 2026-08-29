from django.contrib import admin

from .models import Appointment, Client, ContactMessage, Master, Review, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "duration", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "description"]
    list_editable = ["is_active"]
    readonly_fields = ["created_at"]


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "specialty",
        "experience",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "specialty"]
    search_fields = ["first_name", "last_name", "specialty"]
    list_editable = ["is_active"]
    readonly_fields = ["created_at"]


class AppointmentInline(admin.TabularInline):
    model = Appointment
    extra = 0
    fields = ["service", "master", "appointment_date", "status"]
    readonly_fields = fields
    can_delete = False
    show_change_link = True


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "appointments_count", "created_at"]
    search_fields = ["name", "phone", "email"]
    readonly_fields = ["created_at", "updated_at"]
    inlines = [AppointmentInline]

    @admin.display(description="Записей")
    def appointments_count(self, client):
        return client.appointments.count()


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = [
        "client",
        "service",
        "master",
        "appointment_date",
        "status",
        "created_at",
    ]
    list_filter = ["status", "service", "appointment_date"]
    search_fields = [
        "client__name",
        "client__phone",
        "client__email",
        "client_name",
        "client_phone",
        "client_email",
    ]
    list_editable = ["status"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "appointment_date"
    fieldsets = (
        (
            "Клиент",
            {
                "fields": (
                    "client",
                    "client_name",
                    "client_phone",
                    "client_email",
                )
            },
        ),
        (
            "Услуга и специалист",
            {"fields": ("service", "master", "appointment_date")},
        ),
        ("Статус и комментарий", {"fields": ("status", "comment")}),
        (
            "Системная информация",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["author_name", "rating", "is_published", "created_at"]
    list_filter = ["is_published", "rating"]
    search_fields = ["author_name", "text"]
    list_editable = ["is_published"]
    readonly_fields = ["created_at"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "is_read", "created_at"]
    list_filter = ["is_read", "created_at"]
    search_fields = ["name", "phone", "email", "message"]
    list_editable = ["is_read"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
