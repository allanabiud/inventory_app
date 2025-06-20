import os
import uuid
from datetime import datetime


def item_image_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    item_sku = instance.item.sku.replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = uuid.uuid4().hex[:6]
    filename = f"{item_sku}_{timestamp}_{unique_id}.{ext}"
    return os.path.join("item_images", item_sku, filename)
