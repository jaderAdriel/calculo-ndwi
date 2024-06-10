import rasterio
from rasterio.mask import mask
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import warnings
import os

def get_band_path(year, band):
    base_path = f"./"
    for subdir in os.listdir(base_path):
        subdir_path = os.path.join(base_path, subdir)
        year_image = subdir.split('-')[0]
        if os.path.isdir(subdir_path) and str(year) == year_image:
            for file in os.listdir(subdir_path):
                if file.endswith(f"{band}.TIF"):
                    return os.path.join(subdir_path, file)
    return None

def load_and_crop_band(band_path, shapes):
    with rasterio.open(band_path) as src:
        if src.crs != shapes.crs:
            shapes = shapes.to_crs(src.crs)
        band, transform = mask(src, shapes.geometry, crop=True)
        meta = src.meta.copy()
        meta.update({"driver": "GTiff", "height": band.shape[1], "width": band.shape[2], "transform": transform})
    return band[0], meta

def adjust_band_contrast(band, scale=1.5):
    # Ajuste o contraste normalizando e escalando os valores da banda
    band_min, band_max = np.percentile(band, (1, 99))
    band = np.clip((band - band_min) / (band_max - band_min) * 255, 0, 255)
    return np.clip(band * scale, 0, 255)

def process_landsat_composition(year, bands, shapes):
    green_band_path = get_band_path(year, bands['GREEN'])
    red_band_path = get_band_path(year, bands['RED'])
    nir_band_path = get_band_path(year, bands['NIR'])
    
    if green_band_path and red_band_path and nir_band_path:
        green_band, _ = load_and_crop_band(green_band_path, shapes)
        red_band, _ = load_and_crop_band(red_band_path, shapes)
        nir_band, _ = load_and_crop_band(nir_band_path, shapes)
        
        # Ajuste de contraste para realçar a água
        green_band = adjust_band_contrast(green_band)
        red_band = adjust_band_contrast(red_band)
        nir_band = adjust_band_contrast(nir_band)
        
        # Combinar as bandas em uma única imagem de composição RGB
        composition_rgb = np.stack([nir_band, red_band, green_band], axis=0)
        
        # Normalizar os valores da composição para o intervalo [0, 255]
        composition_rgb = composition_rgb.astype(np.float32)
        composition_rgb = (composition_rgb - composition_rgb.min()) / (composition_rgb.max() - composition_rgb.min()) * 255
        composition_rgb = composition_rgb.astype(np.uint8)
        
        # Salvar a imagem de composição resultante
        
        
        return np.transpose(composition_rgb, (1, 2, 0))
    else:
        warnings.warn(f"Algumas bandas não foram encontradas para o ano {year}.")
        return None

# Área de interesse
area_of_interest_path = "./area_of_interest/area.shp"
aoi_gdf = gpd.read_file(area_of_interest_path)

# Dicionário de bandas para cada ano
x = {
    '1989': {
        'GREEN': 'B2',
        'RED': 'B3',
        'NIR': 'B4',
    },
    '1999': {
        'GREEN': 'B2',
        'RED': 'B3',
        'NIR': 'B4',
    },
    '2007': {
        'GREEN': 'B2',
        'RED': 'B3',
        'NIR': 'B4',
    },
    '2013': {
        'GREEN': 'B3',
        'RED': 'B4',
        'NIR': 'B5',
    }
}

compositions = []
for year, bands in x.items():
    comp = process_landsat_composition(int(year), bands, aoi_gdf)
    if comp is not None:
        compositions.append((year, comp))

# Plotar as imagens
fig, axes = plt.subplots(2, 2, figsize=(20, 20))
axes = axes.flatten()

for ax, (year, comp) in zip(axes, compositions):
    ax.imshow(comp)
    ax.set_title(f"Composição RGB Landsat - {year}")
    ax.axis('off')

# Ajustar espaçamento entre subplots
plt.subplots_adjust(wspace=0.2, hspace=0.2)
plt.show()