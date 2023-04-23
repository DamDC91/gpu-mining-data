# Production d'une ressource en données ouvertes et FAIR

Corentin BOIREAU  
Damien DE CAMPOS  
Frédéric POTIER  
Ryan PERSÉE

---

Nous voulons obtenir un dataset qui répertorie pour chaque mois, les meilleurs cartes graphiques pour miner du Bitcoin.
Le dataset doit suivre les principes FAIR.

## 1) Description critique des caractéristiques du projet
### Sources de données utilisées
 - Page Wikipedia sur les GPU Nvidia pour connaître le prix à la sortie, le TDP (thermal design power), date de sortie (https://en.wikipedia.org/wiki/List_of_Nvidia_graphics_processing_units). On utilise la page HTML, les données qui nous intéressent se trouve dans des tableaux, on les récupère on effectuant un scrapping pour les sortir en format JSON.
 - Blockchain.com pour connaître la difficulté de minage du bitcoin ainsi que son prix (https://www.blockchain.com/explorer/charts/hash-rate?fbclid=IwAR0OOsNWFV8wxENYofvCbyo8AAfu-H7Gln3W7pbaT4gp9kqKi0VqLwCCAr8)
 - Le site du gouvernement américain pour connaître le prix de l'électricité chaque mois aux USA (https://www.eia.gov/electricity/data/browser/?src=-f10#/topic/7?agg=0,1&geo=g&endsec=vg&linechart=~ELEC.PRICE.US-RES.M~~&columnchart=ELEC.PRICE.US-ALL.M~ELEC.PRICE.US-RES.M~ELEC.PRICE.US-COM.M~ELEC.PRICE.US-IND.M&map=ELEC.PRICE.US-ALL.M&freq=M&start=200901&end=202211&ctype=linechart&ltype=pin&rtype=s&pin=&rse=0&maptype=0)

### Ingestion des données
Pour récupérer les données de la page Wikipedia, nous avons utilisé le langage Python avec la librairie BeautifulSoup. Une fois le contenu de la page récupéré, nous avons utilisé la bibliothèque Pandas pour convertir les tableaux HTML en dataframe. Une fois les données dans un dataframe, elles peuvent facilement être converties en JSON.

Une fois cette passe d'extraction remplie, il nous a fallu nettoyer les données. C'est la phase la plus importante, car les données récupérées ne sont pas toujours dans le bon format. Par exemple, la puissance de la carte est donnée parfois en TFLOPS, parfois en GFLOPS : il a donc fallu convertir les données pour qu'elles soient toutes dans la même unité. Nous avons également dû convertir les dates à partir de différents formats (jour présent ou non, virgule supplémentaire, etc.).

Pour récupérer les données de Blockchain.com, nous avons téléchargé un fichier JSON depuis le site. Pour récupérer les données de prix de l'électricité chaque mois aux États-Unis, nous avons téléchargé un fichier CSV depuis le site du gouvernement américain. Nous avons ensuite lu le fichier CSV en Python.

Nous avons fusionné les données en utilisant la date (le mois plus précisément) comme clé de fusion. Nous avons appliqué des transformations aux données pour les convertir en unités cohérentes et calculer le bénéfice net pour chaque GPU. Nous avons ensuite trié les GPU par ordre décroissant de bénéfice net pour chaque mois, sélectionné les 5 meilleurs et créé le fichier JSON final.

### Format produit
Le document produit a pour but de déterminer quels sont les 5 meilleurs GPU pour miner du Bitcoin, chaque mois depuis le 1er juin 2015.

Nous avons choisi d'utiliser le format JSON pour représenter le dataset produit car contrairement au CSV, il permet de facilement représenter des objets complexes (ici les GPUs), il est facilement exploitable dans de nombreux langages et reste relativement lisible pour un humain.

Le fichier JSON produit est un tableau d'objets.
Ces objets contiennent:
- une date au format ISO 8601 qui représente un mois
- une liste des 5 meilleurs GPUs pour ce mois (le meilleur en premier)

Un GPU est décrit par:
- un nom (string)
- un thermal design power (tdp) strictement positif en Watt 
- une date de sortie format ISO 8601
- un hashrate (calculé via grâce à cette [formule](https://www.quora.com/How-do-you-convert-m-flop-s-to-hash-s?share=1)) en hash/seconde
- un bénéfice net (prix en dollars des bitcoins créés - prix de l'électricité nécessaire) en dollars

Exemple de données valides :
```
[
  {
    "month": "2023-04-01",
    "gpus": [
      {
        "name": "NVIDIA GeForce RTX 4080 Ti",
        "tdp": 350,
        "release_date": "2023-03-15",
        "hash_rate": 160.5,
        "net_worth": 1499
      },
      {
        "name": "AMD Radeon RX 7800 XT",
        "tdp": 300,
        "release_date": "2023-02-28",
        "hash_rate": 145.2,
        "net_worth": 1099
      },
      {
        "name": "NVIDIA Quadro RTX 8000",
        "tdp": 260,
        "release_date": "2022-09-01",
        "hash_rate": 100.8,
        "net_worth": 5999
      },
      {
        "name": "AMD Radeon Pro VII",
        "tdp": 250,
        "release_date": "2020-05-18",
        "hash_rate": 95.5,
        "net_worth": 1999
      },
      {
        "name": "NVIDIA GeForce GTX 1650",
        "tdp": 75,
        "release_date": "2019-04-23",
        "hash_rate": 20.3,
        "net_worth": 149
      }
    ]
  }
]
```

### Métadonnées
Les métadonnées sont des informations qui décrivent le dataset produit et aident à comprendre son contenu, son contexte et sa qualité. Elles sont importantes pour que les utilisateurs potentiels puissent évaluer si le dataset répond à leurs besoins et s'ils peuvent l'utiliser en toute confiance.  
Nous avons ajouté des métadonnées indiquant la date de crawling pour le [dataset intermédiaire sur les cartes graphiques NVIDIA](./data-src/gpus.json).  
Il s'agit du minimum nécessaire pour que les utilisateurs potentiels puissent comprendre le contexte et la provenance des données.  

### Pérennité de la stratégie de la construction de la ressource
Les risques ou les limites liés à la stratégie automatique de la construction de la ressource peuvent inclure des modifications apportées aux sources de données, telles que des changements de format, de contenu ou d'accessibilité. Pour garantir la pérennité du dataset produit, il est important de surveiller régulièrement les sources de données pour détecter les changements et les anomalies. Les solutions pour assurer la pérennité de la stratégie automatique peuvent inclure l'automatisation de la mise à jour du dataset produit et la documentation de tous les changements ou anomalies constatés.

### Questions liées à la qualité/fiabilité de la ressource produite
Pour évaluer la qualité et la fiabilité du dataset produit, il est important de mesurer différents critères tels que la complétude, l'exactitude, la cohérence, l'actualité, la pertinence ou l'utilité des données produites. Les sources d'erreur ou d'incertitude qui peuvent affecter la qualité et la fiabilité du dataset produit peuvent inclure des données manquantes, erronées, contradictoires ou obsolètes provenant des sources de données. Pour augmenter la qualité et la fiabilité du dataset produit, il est possible de contrôler ou de valider les données produites, de corriger ou d'enrichir les données produites et de fournir des informations complémentaires ou contextuelles aux utilisateurs potentiels du dataset.

## 2) Discussion (principalement théorique) de l’applicabilité des principes FAIR au projet
### Objectifs poursuivis par la mise à disposition des données
Le dataset produit peut être mis à disposition pour diverses raisons, telles que favoriser la recherche scientifique ou permettre l'accès à des données publiques. Les bénéfices attendus pour la communauté scientifique ou pour la société en général peuvent inclure l'amélioration de la compréhension d'un phénomène, l'aide à la prise de décision ou la création de nouveaux produits ou services. Les utilisateurs potentiels du dataset produit peuvent inclure des chercheurs, des entreprises, des gouvernements ou des organisations non gouvernementales ayant des besoins ou des attentes spécifiques.

### Plan de gestion des données (ce qu'il faudrait faire pour être FAIR)
Pour que le dataset produit respecte les principes FAIR, il est important de mettre en place des actions ou des mesures telles que la traçabilité, la documentation, la standardisation, la pérennisation ou la réutilisation des données. Les acteurs ou les partenaires impliqués dans la gestion des données peuvent inclure des scientifiques, des gestionnaires de données, des développeurs de logiciels ou des utilisateurs finaux. Les ressources ou les coûts nécessaires pour la gestion des données peuvent inclure des moyens humains, techniques ou financiers mobilisés et des sources de financement ou de soutien disponibles.

### Faisabilité à discuter des possibilités suivantes:
La mise à jour périodique des données peut être réalisée en automatisant la récupération de données auprès des sources ou en permettant aux utilisateurs de soumettre des mises à jour via une interface en ligne.
La mise à jour du schéma des données peut être effectuée en documentant les modifications apportées aux données et en fournissant des informations sur les changements de schéma.
