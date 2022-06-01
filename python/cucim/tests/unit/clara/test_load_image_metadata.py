#
# Copyright (c) 2021-2022, NVIDIA CORPORATION.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from ...util.io import open_image_cucim


def test_load_image_metadata(testimg_tiff_stripe_32x24_16):
    import numpy as np

    img = open_image_cucim(testimg_tiff_stripe_32x24_16)

    # True if image data is loaded & available.
    assert img.is_loaded
    # A device type.
    assert str(img.device) == 'cpu'
    # The number of dimensions.
    assert img.ndim == 3
    # A string containing a list of dimensions being requested.
    assert img.dims == 'YXC'
    # A tuple of dimension sizes (in the order of `dims`).
    assert img.shape == [24, 32, 3]
    # Returns size as a tuple for the given dimension order.
    assert img.size('XYC') == [32, 24, 3]
    # The data type of the image.
    dtype = img.dtype
    assert dtype.code == 1
    assert dtype.bits == 8
    assert dtype.lanes == 1
    # The typestr of the image.
    assert np.dtype(img.typestr) == np.uint8
    # A channel name list.
    assert img.channel_names == ['R', 'G', 'B']
    # Returns physical size in tuple.
    assert img.spacing() == [1.0, 1.0, 1.0]
    # Units for each spacing element (size is same with `ndim`).
    assert img.spacing_units() == ['micrometer', 'micrometer', 'color']
    # Physical location of (0, 0, 0) (size is always 3).
    assert img.origin == [0.0, 0.0, 0.0]
    # Direction cosines (size is always 3x3).
    assert img.direction == [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    # Coordinate frame in which the direction cosines are measured.
    # Available Coordinate frame is not finalized yet.
    assert img.coord_sys == 'LPS'
    # Returns a set of associated image names.
    assert img.associated_images == set()
    # Returns a dict that includes resolution information.
    assert img.resolutions == {
        'level_count': 1,
        'level_dimensions': ((32, 24),),
        'level_downsamples': (1.0,),
        'level_tile_sizes': ((16, 16),)
    }
    # A metadata object as `dict`
    metadata = img.metadata
    print(metadata)
    assert isinstance(metadata, dict)
    assert len(metadata) == 2  # 'cucim' and 'tiff'
    # A raw metadata string.
    assert img.raw_metadata == '{"axes": "YXC", "shape": [24, 32, 3]}'


def test_load_rgba_image_metadata(tmpdir):
    """Test accessing RGBA image's metadata.

    - https://github.com/rapidsai/cucim/issues/262
    """
    import numpy as np
    from tifffile import imwrite
    from cucim import CuImage

    # Test with a 4-channel image
    img_array = np.ones((32, 32, 3)).astype(np.uint8)
    print(f'RGB image shape: {img_array.shape}')
    img_array = np.concatenate(
        [img_array, 255 * np.ones_like(img_array[..., 0])[..., np.newaxis]],
        axis=2)
    print(f'RGBA image shape: {img_array.shape}')

    file_path_4ch = str(tmpdir.join("small_rgba_4ch.tiff"))
    imwrite(file_path_4ch, img_array, shape=img_array.shape, tile=(16, 16))

    obj = CuImage(file_path_4ch)
    assert obj.metadata["cucim"]["channel_names"] == ["R", "G", "B", "A"]
    obj2 = obj.read_region((0, 0), (16, 16))
    assert obj2.metadata["cucim"]["channel_names"] == ["R", "G", "B", "A"]

    # Test with a 1-channel image
    img_1ch_array = np.ones((32, 32, 1)).astype(np.uint8)
    file_path_1ch = str(tmpdir.join("small_rgba_1ch.tiff"))
    imwrite(file_path_1ch, img_1ch_array,
            shape=img_1ch_array.shape, tile=(16, 16))

    obj = CuImage(file_path_1ch)
    assert obj.shape == [32, 32, 4]
    assert obj.metadata["cucim"]["channel_names"] == ["R", "G", "B", "A"]
    obj2 = obj.read_region((0, 0), (16, 16))
    assert obj2.metadata["cucim"]["channel_names"] == ["R", "G", "B", "A"]
