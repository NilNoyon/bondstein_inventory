from django.conf.urls import url
from django.urls import path
from pre_order import views


urlpatterns = [
    # supplier...
    path('supplier-list', views.supplierList, name='supplier_list'),

    path('add-supplier', views.addSupplier, name='add_supplier'),
    path('get-supplier', views.getSupplier, name='get_supplier'),
    path('update-supplier', views.updateSupplier, name='update_supplier'),
    path('delete-supplier', views.deleteSupplier, name='delete_supplier'),

    # items and categories...
    path('item-categories', views.itemCategories, name='item_categories'),
    
    path('add-category', views.addCategory, name='add_category'),
    path('get-category', views.getCategory, name='get_category'),
    path('update-category', views.updateCategory, name='update_category'),
    path('delete-category', views.deleteCategory, name='delete_category'),

    path('add-item', views.addItem, name='add_item'),
    path('get-item', views.getItem, name='get_item'),
    path('update-item', views.updateItem, name='update_item'),
    path('delete-item', views.deleteItem, name='delete_item'),

    # items details...
    path('item-list', views.itemList, name='items'),
    
    path('add-item-details', views.addItemDetails, name='add_item_details'),
    path('get-item-details', views.getItemDetails, name='get_item_details'),
    path('update-item-details', views.updateItemDetails, name='update_item_details'),
    path('delete-item-details', views.deleteItemDetails, name='delete_item_details'),

    # add manual po
    path('upload-pdf', views.uploadPDF, name='upload_pdf'),
    path('save-pdf', views.savePDF, name='save_pdf'),
    path('add-manual-po', views.add_manual_po, name='add_manual_po'),
    path('list', views.preOrderList, name='pre_order_list'),
    path('details-list/<int:id>', views.preOrderDetailsList, name='pre_order_details_list'),
    path('save-manual-po', views.save_preorder, name='save_preorder'),
    path('delete-po', views.deletePO, name='delete_po'),

    # generate barcode..
    path('generate-barcode', views.generateBarcode, name='generate_barcode'),
    path('generate-manual-barcode', views.generateManualBarcode, name='generate_manual_barcode'),
    path('scan-barcode', views.scan, name='scan_barcode'),

    ## stock list..
    path('stock-list', views.stockList, name='stock_list'),
    path('stock-log', views.stockLog, name='stock_log'),
    path('scanned-product-list', views.scannedProductList, name='scanned_product_list'),
    path('stock-in/<int:id>', views.stockIn, name='stock_in'),
    # path('generate-barcode/<int:id>', views.generateBarcode, name='generate_barcode'),
    path('scan-form-barcode', views.scanBCB, name='scan_form_bcb'),
    path('store-scan-data', views.storeScanData, name='store_scan_data'),

    # ajax method..
    path('get-order-wise-item', views.getOrderWiseItem, name='ajax_get_order_wise_item'),
    path('get-item-details-for-item', views.getItemDetailsForItem, name='ajax_get_item_details'),
    path('get-item-quantity', views.getItemQuantity, name='ajax_get_quantity'),
    path('get-item-barcode', views.getItemBarcode, name='ajax_get_barcode'),
]