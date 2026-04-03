from django.contrib import admin

# Register the BorrowRequest model
from .models import BorrowRequest

@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'id_number', 'amount', 'fee', 'payment_status', 'created_at')
    list_filter = ('payment_status',)
    search_fields = ('phone_number', 'id_number')
