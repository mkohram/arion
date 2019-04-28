## installation steps
1 - setup conda with R available
```
conda create -n -c conda-forge arion_r r-essentials r-base numpy pandas jupyterlab networkx python-levenshtein matplotlib
conda activate arion_r
conda install -c conda-forge jupyterlab
```

2 - install R
```
brew tap homebrew/science
brew install r
```

3 - Link R and jupyter kernels 

Open R command line:
```
install.packages('IRkernel')
IRkernel::installspec(user = FALSE)
```

4 - Open jupyter lab
```
jupyter lab
```

5 - install R requirements
Open the `notebooks/speaq.R.ipynb` notebook, uncomment the first cell and run!


Notes:
1- if opening one of the R kernels for the first time, you will need to switch the kernel to R from the default which 
is python. This can be done by clicking on the kernel on the top right hand side of the jupyter lab notebook.

2- To test that R is set up correctly open `notebooks/speaq.R.ipynb` and run through the commands.

R setup resources:

https://docs.anaconda.com/anaconda/user-guide/tasks/use-r-language/
https://irkernel.github.io/installation/
https://richpauloo.github.io/2018-05-16-Installing-the-R-kernel-in-Jupyter-Lab/
