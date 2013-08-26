from music import ArtistDetail, ArtistList, SongDetail, SongList, ReleaseDetail, ReleaseList
from store import (add_to_cart, cart, update_cart, remove_from_cart, ProductDetail, ProductList,
                   checkout, shipping, shipping_methods, payment, process_payment, download,
                   process_download)
from admin import (dashboard as admin_dashboard, OrderList, OrderDetail, ship_order, refund_order,
                   hide_order, ArtistAdminList, ArtistCreate, ArtistUpdate, ArtistDelete, ImageList,
                   ImageCreate, ImageUpdate, ImageDelete, ImageJSONList)
