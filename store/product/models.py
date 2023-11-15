
from django.db import models


class HistoryProducts(models.Model):
    ean = models.BigIntegerField()
    qty = models.IntegerField()
    date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'history_products'

    def __str__(self):
        return f"{self.ean} -{self.qty} - {self.date}"



class Products(models.Model):
    ean = models.BigIntegerField(primary_key=True)
    symbol = models.CharField(max_length=13, blank=True, null=True)
    qty = models.IntegerField(blank=True, null=True)
    model = models.CharField(max_length=16, blank=True, null=True)
    sizechart = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'

    def __str__(self):
        return f"{self.ean} - {self.symbol} - {self.model} - {self.qty} -{self.sizechart}"


