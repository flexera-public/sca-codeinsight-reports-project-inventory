# sca-codeinsight-reports-project-inventory

The sca-codeinsight-reports-project-inventory repository is a example report for Revenera's Code Insight product. This report allows a user to get a quick high level summary of the inventory items within a project.  This report will take into account any child projects (recursively) and roll up the associated inventory information on a project as well as an application basis.

This repository utilizes the following via CDN for the creation of the report artifacts.
- [Bootstrap](https://getbootstrap.com/)
- [DataTables](https://datatables.net/)
- [chart.js](https://www.chartjs.org/)
- [jsTree](https://www.jstree.com/)


## Prerequisites


 **Code Insight Release Requirements**
  
|Repository Tag | Minimum Code Insight Release  |
|--|--|
|1.0.x |2020R3  |
|2.0.x |2020R3  |
|2.1.x |2020R4  |
|2.2.x |2021R1  |
|3.0.x |2021R2  |



**Submodule Repositories**

This repository contains two submodules pointing to other git repos for code that can be in common to multiple projects. After the initial clone of sca-codeinsight-reports-project-inventory you will need to enter the cloned directory, link and pull down the necessary code via

    git submodule init
    git submodule update

**Python Requirements**

This repository requires the python requests module to interact with the Code Insight REST APIs.  To install this as well as the the modules it depends on the [requirements.txt](requirements.txt) file has been supplied and can be used as follows.

    pip install -r requirements.txt

## Required Configuration

There are two locations that require updates to provide the report scripts details about the host system.

The [create_report.sh](create_report.sh) or [create_report.bat](create_report.bat) file contains a **baseURL** value that should be updated to allow for project and inventory links to point to the correct system. 

For registration purposes update the **baseURL** and **adminAuthToken** values within [registration.py](registration.py) to reflect the correct values to allow the report itself to be registered on the Code Insight server.  These values can also be stored in common_config.json that resides one directory above the base report directory which can be shared for all reports. Report option default values can also be specified in [registration.py](registration.py) within the reportOptions dictionaries.

### Registering the Report


Prior to being able to call the script directly from within Code Insight it must be registered. The registration.py file can be used to directly register the report once the contents of this repository have been copied into the custom_report_script folder at the base Code Insight installation directory.

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
- CVSS Version - (2.0/3.x/False) - Specify which CVSS version for vulnerability data.

The Code Insight Custom Report Framework will provide the following to the custom report when initiated:

- Project ID
- Report ID
- Authorization Token
 

For this example report these three items are passed on to a batch or sh file which will in turn execute a python script. This script will then:

- Collect data for the report via REST API using the Project ID and Authorization Token
- Take this collected data and generated an html document with details about the project inventory
	- The *"viewable"* file   
 - Create a zip file of this html document
	  - The *"downloadable"* file
  - Create a zip file with the viewable file and the downloadable file
- Upload this combined zip file to Code Insight via REST API
- Delete the report artifacts that were created as the script ran

## License

[MIT](LICENSE.TXT)


