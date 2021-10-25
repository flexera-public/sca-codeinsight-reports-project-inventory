# sca-codeinsight-reports-project-inventory

The sca-codeinsight-reports-project-inventory repository is a example report for Revenera's Code Insight product. This report allows a user to get a quick high level summary of the inventory items within a project. This report will take into account any child projects (recursively) and roll up the associated inventory information on a project as well as an application basis.

This repository utilizes the following via CDN for the creation of the report artifacts.

-  [Bootstrap](https://getbootstrap.com/)
-  [DataTables](https://datatables.net/)
-  [chart.js](https://www.chartjs.org/)
-  [jsTree](https://www.jstree.com/)

## Prerequisites

**Code Insight Release Requirements**

|Repository Tag | Minimum Code Insight Release |

|--|--|

|1.0.x |2020R3 |

|2.0.x |2020R3 |

|2.1.x |2020R4 |

|2.2.x |2021R1 |

|3.0.x |2021R2 |

|4.0.x |2021R2 |

|5.0.x |2021R2 |

|6.0.x |2021R4 |

**Repository Cloning**

This repository should be cloned directly into the **$CODEINSIGHT_INSTALLDIR/custom_report_scripts** directory. If no prior custom reports has been installed, this directory will need to be created prior to cloning.

**Submodule Repositories**

This repository contains two submodules pointing to other git repos for code that are used across multiple projects. After the initial repository clone, you will need to enter the cloned directory and pull down the necessary submodules code via

	git submodule init
	git submodule update

**Python Requirements**

The required python modules can be installed with the use of the [requirements.txt](requirements.txt) file which can be loaded via.

	pip install -r requirements.txt

## Configuration and Report Registration
 
For registration purposes the file **core.server.properties** should be ceated and located in the **$CODEINSIGHT_INSTALLDIR/custom_report_scripts/** directory.  This file contains a json with information required to register the report within Code Insight as shown  here:

>     {
>         "core.server.url": "http://localhost:8888" ,
>         "core.server.token" : "Admin authorization token from Code Insight"
>     }

The value for core.server.url is also used within [create_report.py](create_report.py) for any project or inventory based links back to the Code Insight server within a generated report.

If the common **core.server.properties** files is not used then the information the the following files will need to be updated:

[registration.py](registration.py)  -  Update the **baseURL** and **adminAuthToken** values. These settings allow the report itself to be registered on the Code Insight server.

[create_report.py](create_report.py)  -  Update the **baseURL** value. This URL is used for links within the reports.

Report option default values can also be specified in [registration.py](registration.py) within the reportOptions dictionaries.

### Registering the Report

Prior to being able to call the script directly from within Code Insight it must be registered. The [registration.py](registration.py) file can be used to directly register the report once the contents of this repository have been added to the custom_report_script folder at the base Code Insight installation directory.

To register this report:

	python registration.py -reg

To unregister this report:
	
	python registration.py -unreg

To update this report configuration:
	
	python registration.py -update

## Usage

This report is executed directly from within Revenera's Code Insight product. From the project reports tab of each Code Insight project it is possible to *generate* the **Project Inventory Report** via the Custom Report Framework.

The following report options can be set once the report generation has been initiated:

- Including child projects (True/False) - Determine if child project data will be included or not.
- Include compliance information - (True/False) - Include compliance related data.
- Maximum number of versions back - (Integer value) - The number of newer released versions of a component which is acceptable for compliance purposes.
- CVSS Version - (2.0/3.x) - Specify which CVSS version for vulnerability data.

The Code Insight Custom Report Framework will provide the following to the custom report when initiated:

- Project ID
- Report ID
- Authorization Token

For this example report these three items are passed on to a batch or sh file which will in turn execute a python script. This script will then:

- Collect data for the report via REST API using the Project ID and Authorization Token
- Take this collected data and generate an html as well as an xlsx file with details about the project inventory
- The html files will be marked as the *"viewable"* file
- A zip file will be created containing the html and xlsx files which will be the *"downloadable"* file.
- Create a zip file with the viewable file and the downloadable file
- Upload this combined zip file to Code Insight via REST API
- Delete the report artifacts that were created as the script ran

## License

[MIT](LICENSE)