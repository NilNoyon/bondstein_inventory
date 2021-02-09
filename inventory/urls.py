from django.conf.urls import url
from django.urls import path
from inventory import views


urlpatterns = [
    # client...
    path('client-list', views.clientList, name='client_list'),

    path('add-client', views.addClient, name='add_client'),
    path('get-client', views.getClient, name='get_client'),
    path('update-client', views.updateClient, name='update_client'),
    path('delete-client', views.deleteClient, name='delete_client'),

    # sales order...
    path('sales-order-list', views.SOList, name='so_list'),

    path('add-sales-order', views.addSO, name='add_so'),
    path('get-sales-order', views.getSO, name='get_so'),
    path('update-sales-order', views.updateSO, name='update_so'),
    path('delete-sales-order', views.deleteSO, name='delete_so'),
    path('sales-order-details/<int:id>', views.SODetail, name='so_details'),
    path('so-detail-list/<int:id>', views.SODetailsList, name='so_detail_list'),

    # stock transfer warehouse to warehouse...
    path('transfered-item-list', views.STOList, name='sto_list'),

    path('add-transfer-order', views.addSTO, name='add_sto'),
    # path('get-sales-order', views.getSO, name='get_so'),
    # path('update-sales-order', views.updateSO, name='update_so'),
    # path('delete-sales-order', views.deleteSO, name='delete_so'),
    # path('sales-order-details/<int:id>', views.SODetail, name='so_details'),
    # path('so-detail-list/<int:id>', views.SODetailsList, name='so_detail_list'),

    #stock out...
    path('stock-out/<int:id>', views.stockOut, name='stock_out'),
    path('store-stock-out', views.storeStockOut, name='store_stockout_data'),

    path('scan-barcode', views.scanBarcode, name='scan_for_stock_out'),
    # ajax method..
    path('get-responible-person',views.getResponsiblePerson, name='get_responsible_person'),
]
