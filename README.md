# Relatório de Análise de Imagem Sentinel-2

Este é um relatório de análise de imagem do Sentinel-2, realizado como parte de uma bolsa de iniciação científica. O objetivo desse trabalho foi aprender a criar um algoritmo para calcular o NDWI de uma imagem do Sentinel-2, e gerar uma imagem colorida com as bandas RGB.

## Dados Utilizados

Foram utilizados os seguintes dados para a análise:

- Imagem Sentinel-2: T23LQE_20230401T131241
- Bandas utilizadas: B03, B08

| Banda | Nome | Resolução Espacial | Comprimento de Onda | Utilização |
|-------|------|-------------------|---------------------|------------|
| B03 | Verde | 10m | 0.53 - 0.59 μm | Discriminar entre tipos de vegetação, monitorar saúde da vegetação |
| B08 | NIR | 10m | 0.78 - 0.84 μm | Mapear vegetação, estimar produtividade agrícola, identificar superfícies impermeáveis |

## Pré-processamento dos Dados

Os dados foram pré-processados da seguinte maneira:

- As bandas foram lidas usando a biblioteca Rasterio do Python
- Foi criado duas matrizes, um com a banda NIR (B08) e outro com a banda Verde (B08) 
- Foi calculado o NDWI a partir das matrizes de banda usando a fórmula NDWI = (Verde - NIR) / (Verde + NIR)
- Foi realizado uma plotagem da matriz resultante.
## Resultados

A imagem colorida é mostrada abaixo:

![Imagem colorida](https://github.com/jaderAdriel/calculo-ndwi/blob/main/imagens/S2A_MSIL1C_20230401T131241_N0509_R138_T23LQE_20230401T180900-ql.jpg?raw=true)

A imagem NDWI resultante do calculo é mostrada abaixo:

![Imagem NDWI](https://github.com/jaderAdriel/calculo-ndwi/blob/main/imagens/imagemNDWI.png?raw=true)

A partir da imagem NDWI, é possível identificar áreas de água em cinza, e áreas de vegetação em branco. Podemos identificar como pontos importantes a barragem de ceraíma e a barragem do poço magro.

## Conclusão

A análise da imagem Sentinel-2 utilizando o algoritmo de cálculo de NDWI mostrou que é possível identificar áreas de água e vegetação a partir de imagens multiespectrais. Essas informações podem ser usadas em diversas aplicações, como monitoramento ambiental e gestão de recursos naturais.
