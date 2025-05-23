import logging
import os
from typing import Optional, Tuple

import pystac
from pystac.extensions.eo import EOExtension

from stactools.sentinel1.constants import SENTINEL_POLARIZATIONS
from stactools.sentinel1.slc.constants import SENTINEL_SLC_SWATHS

logger = logging.getLogger(__name__)


def image_asset_from_href(
    asset_href: str,
    item: pystac.Item,
    # resolution_to_shape: Dict[int, Tuple[int, int]],
    # proj_bbox: List[float],
    media_type: Optional[str] = None,
    slc_swaths: Optional[bool] = False,
) -> Tuple[str, pystac.Asset]:
    logger.debug(f"Creating asset for image {asset_href}")

    _, ext = os.path.splitext(asset_href)
    if media_type is not None:
        asset_media_type = media_type
    else:
        if ext.lower() in [".tiff", ".tif"]:
            asset_media_type = pystac.MediaType.GEOTIFF
        else:
            raise Exception(f"Must supply a media type for asset : {asset_href}")

    # Handle band image
    asset_parts = os.path.basename(asset_href).split(".")[0].split("-")
    if len(asset_parts) == 2:
        band_id = asset_parts[-1]
    else:
        band_id = asset_parts[3]

    if band_id is not None:
        band = SENTINEL_POLARIZATIONS[band_id]

        # Create asset
        desc = "Actual SAR data that have been processed into an image"
        asset = pystac.Asset(
            href=asset_href,
            media_type=asset_media_type,
            title=f"{band.name} Data",
            roles=["data"],
            description=desc,
        )

        asset_eo = EOExtension.ext(asset)
        asset_eo.bands = [SENTINEL_POLARIZATIONS[band_id]]

        if slc_swaths:
            swath = asset_parts[1].upper()
            if swath in SENTINEL_SLC_SWATHS:
                band_id = f"{swath.lower()}-{band_id}"

        return (band_id, asset)

    else:

        raise ValueError(f"Unexpected asset: {asset_href}")
