FunPDBe Deposition System
=====

[![Build Status](https://travis-ci.org/funpdbe-consortium/funpdbe-deposition.svg?branch=master)](https://travis-ci.org/funpdbe-consortium/funpdbe-deposition)
[![codecov](https://codecov.io/gh/funpdbe-consortium/funpdbe-deposition/branch/master/graph/badge.svg)](https://codecov.io/gh/funpdbe-consortium/funpdbe-deposition)
[![Maintainability](https://api.codeclimate.com/v1/badges/3da9a340764fa8b0ccf1/maintainability)](https://codeclimate.com/github/funpdbe-consortium/funpdbe-deposition/maintainability)

This repository is the code base for the FunPDBe deposition system.

For more information on the FunPDBe initiative, visit https://funpdbe.org

Quick start
-----------

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

There are no prerequisites for installing the app, other than installing the requirements

### Installing

The are two main approaches to getting the client up and running.

#### Checking out this repository

```
$ git clone https://github.com/funpdbe-consortium/funpdbe-deposition
$ cd funpdbe-deposition
$ pip install -r requirements.txt
```

## Usage

Examples of usage:

```
$ python manage.py runserver
```

## Running the tests

Running tests for the client is performed simply by using
```
$ python manage.py test
```

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/funpdbe-consortium/funpdbe-deposition/tags).

## Authors

* **Mihaly Varadi** - *Initial work* - [mvaradi](https://github.com/mvaradi)

See also the list of [contributors](https://github.com/funpdbe-consortium/funpdbe-client/graphs/contributors) who participated in this project.

## License

This project is licensed under the EMBL-EBI License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

We would like to thank the PDBe team for their support and feedback, as well as all the members of the FunPDBe consortium:

* PDBe team - [team website](https://www.ebi.ac.uk/services/teams/pdbe)
* Orengo team - [CATH](http://www.cathdb.info/)
* Vranken team - [DynaMine](http://dynamine.ibsquare.be/)
* Barton team - [NoD](http://www.compbio.dundee.ac.uk/www-nod/)
* Wass team - [3DLigandSite](http://www.sbg.bio.ic.ac.uk/3dligandsite/)
* Blundell team - [CREDO](http://marid.bioc.cam.ac.uk/credo)
* Fraternali team - [POPSCOMP](https://mathbio.crick.ac.uk/wiki/POPSCOMP)