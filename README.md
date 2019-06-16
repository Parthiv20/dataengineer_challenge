# dataengineer_challenge

## Clip and Sharpen

### Requirements

* To run this repo host machine must have docker and docker-compose installed

### Data

 * For this challenge Pléiades Projected WGS84 Pansharpened (GEOTIFF 8bits) image has been used
 * More info about the image
   * Lcation: Venise, Italy
   * File format: Geotiff 8 bits
   * Resolution: 0.5 m
   * Spectral mode: Pan-sharpened 3 bands
 * The image can be downloaded by clicking the following link (curl or wget can also be used)
 * https://www.intelligence-airbusds.com/en/8290-download-sample-imagery?product=43232&name=pleiades-projected-wgs84-pansharpened-geotiff-8bits
 * The downloded compressed file should be saved at base directory of this repo
 * Then extract the compressed file
 * If every thing goes well, There should be new directory with name FCGC600435537
 * On my machine repo directory structure is
   *  image path ```/dataengineer_challenge/FCGC600435537/IMG_PHR1B_PMS-N_001```
   *  clip_sharp container contents  contents ```/dataengineer_challenge/clip_sharp```
   *  result path ```/dataengineer_challenge/results```
   *  jupyter container contents ```/dataengineer_challenge/jupyter```


### Commands

* First run ```docker-compose build``` it takes a while. As it needs to pull the base images from docker hub
* Once build is successful, then run ```docker-compose up```
* The above command runs and tests the application.
* If every thing goes well, clipped.tif and sharpened.tif should be created at ```/FCGC600435537/IMG_PHR1B_PMS-N_001```
* Print screens of clip and shparpened images can be found at ```/results```

### Jupyter