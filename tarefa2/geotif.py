import os
import rasterio

def generate_band_mapping_txt(directory, year):
    # List all .TIF files in the directory
    band_files = [f for f in os.listdir(directory) if f.endswith('.TIF')]
    
    # Open the first band to get metadata
    first_band_path = os.path.join(directory, band_files[0])
    with rasterio.open(first_band_path) as src:
        meta = src.meta.copy()
        bands = [src.read(1)]

    # Read each band and store the data
    for band_file in band_files[1:]:
        band_path = os.path.join(directory, band_file)
        with rasterio.open(band_path) as src:
            bands.append(src.read(1))

    # Update metadata for multiband
    meta.update(count=len(bands))

    # Create output directory if it doesn't exist
    output_directory = f"./Multiband_Compositions/{year}"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Define output paths
    output_path = os.path.join(output_directory, f"multiband_{year}.tif")
    mapping_txt_path = os.path.join(output_directory, f"band_mapping_{year}.txt")

    # Create band mapping text file
    with open(mapping_txt_path, 'w') as f:
        for i, band_file in enumerate(band_files, start=1):
            f.write(f"Band {i}: {band_file}\n")

    print(f"Multiband GeoTIFF saved for year {year} at {output_path}")
    print(f"Band mapping saved at {mapping_txt_path}")
    return output_path, mapping_txt_path

# Example usage


generate_band_mapping_txt("2007/", "2007")
generate_band_mapping_txt("2013/", "2013")