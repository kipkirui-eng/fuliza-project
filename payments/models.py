from django.db import models


class BorrowRequest(models.Model):
    id_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15)
    amount = models.PositiveIntegerField()
    fee = models.PositiveIntegerField()
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed')
    ]
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.phone_number} - {self.amount} - {self.payment_status}"