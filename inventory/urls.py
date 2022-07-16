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

    path('add-sto', views.addSTO, name='add_sto'),
    path('scan-for-out/<int:id>', views.scanForOut, name='scan_for_out'),
    path('delete-sto', views.deleteSTO, name='delete_sto'),
    # path('update-sales-order', views.updateSO, name='update_so'),
    path('sto-details/<int:id>', views.STODetail, name='sto_details'),
    path('sto-detail-list/<int:id>', views.STODetailsList, name='sto_detail_list'),

    # Floating sales...
    path('floating-item-list', views.FIList, name='fi_list'),

    path('add-fo', views.addFO, name='add_fo'),
    # path('scan-for-out/<int:id>', views.scanForOut, name='scan_for_out'),
    path('delete-fo', views.deleteFO, name='delete_fo'),
    path('fo-details/<int:id>', views.FODetail, name='fo_details'),
    path('generate_so/<int:id>', views.generateSO, name='generate_so'),
    path('re-stock/<int:id>', views.reStock, name='re_stock'),

    #stock out...
    path('stock-out/<int:id>', views.stockOut, name='stock_out'),
    path('store-stock-out', views.storeStockOut, name='store_stockout_data'),

    path('scan-barcode', views.scanBarcode, name='scan_for_stock_out'),
    path('scan-barcode-for-sto', views.scanBarcodeForSTO, name='scan_for_sto'), #scan for stock transfer
    path('store-sto', views.storeSTO, name='store_sto_data'),
    path('receive-sto', views.receiveSTChallan, name='receive_sto'), #receive stchallan from warehouse to another warehouse
    path('scan-barcode-for-fo', views.scanBarcodeForFO, name='scan_for_floating'), # scan bundle card for floating..
    # ajax method..
    path('get-responible-person',views.getResponsiblePerson, name='get_responsible_person'),
    path('get-sto-info', views.getSTOInfo, name='get_sto_info'),

    # Reports Url...
    path('daily-inventory-report', views.dailyInventoryReport, name='daily_inventory_report'),
    path('get-daily-inventory-report', views.getDailyInventoryReport, name='get_daily_inventory_report'),
    path('export-daily-inventory-report/<from_date>/<to_date>/<warehouse>/', views.exportDailyInventoryReport, name='export_daily_inventory_report'),

    path('monthly-inventory-report', views.monthlyInventoryReport, name='monthly_inventory_report'),
    path('get-monthly-inventory-report', views.getMonthlyInventoryReport, name='get_monthly_inventory_report'),
    path('export-monthly-inventory-report/<month>/<year>/<warehouse>/', views.exportMonthlyInventoryReport, name='export_monthly_inventory_report'),

    path('forecast-report', views.forecastReport, name='forecast_report'),
    path('forecast-report-info', views.forecastReportInfo, name='get_forecast_info'),
    path('forecast-report-graph-info', views.forecastReportGraphInfo, name='get_forecast_graph_info'),

    path('channel-demand/add', views.channelDemandAdd, name='add_channel_demand'),
    path('channel-demand/save', views.save_channel_demand, name='save_channel_demand'),
]
