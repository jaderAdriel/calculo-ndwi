import tarfile
import os
import warnings
import glob
import fiona
import rasterio
import numpy as np
from rasterio.plot import show
from rasterio.mask import mask
import pandas as pd
from shapely.geometry import shape
from rasterio.features import shapes
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import mapping


def get_band_path(year, band):
    base_path = f"./IMAGES/"

    for subdir in os.listdir(base_path):
        subdir_path = os.path.join(base_path, subdir)
        year_image = subdir.split('-')[0]
        if os.path.isdir(subdir_path) and str(year) == year_image:
            for file in os.listdir(subdir_path):
                if file.endswith(f"{band}.TIF"):
                    return os.path.join(subdir_path, file)
    return None

# Função para carregar e recortar uma banda
def load_and_crop_band(band_path, shapes):
    with rasterio.open(band_path) as src:
        if src.crs != shapes.crs:
            shapes = shapes.to_crs(src.crs)
        band, transform = mask(src, shapes.geometry, crop=True)
        meta = src.meta.copy()
        meta.update({"driver": "GTiff", "height": band.shape[1], "width": band.shape[2], "transform": transform})
    return band[0], meta

# Função para calcular o NDWI
def calculate_ndwi(green, nir):
    np.seterr(divide='ignore', invalid='ignore')
    green_norm = green / 255.0
    nir_norm = nir / 255.0
    ndwi = (green_norm - nir_norm) / (green_norm + nir_norm)
    return ndwi

# Função para extrair polígonos de água
def extract_water_polygons(ndwi, meta, threshold=-10):
    water_mask = ndwi > threshold
    transform = meta['transform']
    water_mask = water_mask.astype(np.int16)
    shape_list = []
    for shape_obj, value in shapes(water_mask, transform=transform):
        if value == 1:
            shape_list.append(shape(shape_obj))
    
    print(f"Total water polygons extracted: {len(shape_list)}")

    return shape_list


# Função para salvar os polígonos em um shapefile

def save_polygons_to_shapefile(polygons, crs, year=None):
    # Use o ano fornecido ou o ano atual
    satellite = ""
    date = ""
    for file_name in os.listdir(f"./IMAGES/{year}"):
        landsat = file_name.split("_")[0]
        date = file_name.split("_")[3]
        break
    
    print(date, satellite, sep=" -> ")
    metadata = {
        'Date': date,
        'Satellite': landsat,
    }

    # Definir o caminho do diretório e do arquivo
    output_directory = f"./output_shapefile/{year}"
    output_shapefile_path = f"{output_directory}/shape_{year}.shp"
    
    # Criar o diretório se ele não existir
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Criar um GeoDataFrame com os polígonos
    polygons_gdf = gpd.GeoDataFrame(geometry=polygons, crs=crs)
    
    # Salvar o GeoDataFrame como um shapefile com metadados
    schema = {
        'geometry': 'Polygon',
        'properties': {'Date': 'str', 'Satellite': 'str'}
    }
    
    with fiona.open(output_shapefile_path, 'w', driver='ESRI Shapefile', crs=crs, schema=schema) as shapefile:
        for polygon in polygons:
            shapefile.write({
                'geometry': mapping(polygon),
                'properties': metadata,
            })

    print(f"Shapefile saved with metadata: {metadata}")


    

# Função principal para processar as imagens de um determinado ano
def process_landsat_ndwi(year, threshold=0.1):
    area_of_interest_path = "./area_of_interest/area.shp"
    aoi_gdf = gpd.read_file(area_of_interest_path)

    green_band_path = get_band_path(year, 'B3')
    nir_band_path = get_band_path(year, 'B6')

    green_band, green_meta = load_and_crop_band(green_band_path, aoi_gdf)
    nir_band, _ = load_and_crop_band(nir_band_path, aoi_gdf)

    # Calcular NDWI
    print(f"Fazendo cálculo NDWI {year}...", end="", flush=True)
    ndwi = calculate_ndwi(green_band, nir_band)
    print(" Ok")


    # plt.figure(figsize=(8, 6))
    # plt.imshow(ndwi, cmap='gray')
    # plt.colorbar(label='NDWI')
    # plt.title(f'Índice de Água Normalizado (NDWI) - {year}')
    # plt.xlabel('Coluna')
    # plt.ylabel('Linha')
    # plt.grid(False)
    # plt.show()

    # # Extrair polígonos de água
    print("Extraindo os polígonos de água...", end="", flush=True)
    water_polygons = extract_water_polygons(ndwi, green_meta, threshold)
    print(" Ok")
    # Salvar os polígonos de água
    print("Salvando os polígonos de água...", end="", flush=True)
    save_polygons_to_shapefile(water_polygons, green_meta['crs'], year)
    print(" Ok")

    print(f"Processamento {year} concluído.\n")


years = [2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013]

for year in years:
    process_landsat_ndwi(year)