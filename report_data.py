'''
Copyright 2020 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Fri Aug 07 2020
File : report_data.py
'''

import logging

import CodeInsight_RESTAPIs.project.get_child_projects
import CodeInsight_RESTAPIs.project.get_project_inventory
import CodeInsight_RESTAPIs.project.get_project_information
import CodeInsight_RESTAPIs.project.get_inventory_summary

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------#
def gather_data_for_report(baseURL, projectID, authToken, reportName):
    logger.info("Entering gather_data_for_report")

    projectList = [] # List to hold parent/child details for report
    inventoryData = {}  # Create a dictionary containing the inventory data using inventoryID as keys
    projectData = {} # Create a dictionary containing the project level summary data using projectID as keys

    # Get the list of parent/child projects start at the base project
    projectHierarchy = CodeInsight_RESTAPIs.project.get_child_projects.get_child_projects_recursively(baseURL, projectID, authToken)

    # Create a list of project data sorted by the project name at each level for report display  
    # Add details for the parent node
    nodeDetails = {}
    nodeDetails["parent"] = "#"  # The root node
    nodeDetails["projectName"] = projectHierarchy["name"]
    nodeDetails["projectID"] = projectHierarchy["id"]
    nodeDetails["projectLink"] = baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(projectHierarchy["id"]) + "&tab=projectInventory"

    projectList.append(nodeDetails)

    projectList = create_project_hierarchy(projectHierarchy, projectHierarchy["id"], projectList, baseURL)

    #  Gather the details for each project and summerize the data
    for project in projectList:

        projectID = project["projectID"]
        projectName = project["projectName"]
        projectLink = project["projectLink"]

        # Get project information with rollup summary data
        try:
            projectInformation = CodeInsight_RESTAPIs.project.get_project_information.get_project_information_summary(baseURL, projectID, authToken)
        except:
            logger.error("    No Project Information Returned!")
            print("No Project Information Returned.")
            return -1

        # Get project summary information with v3 vulnerability roll up at inventory level
        try:
            projectInventorySummary = CodeInsight_RESTAPIs.project.get_inventory_summary.get_project_inventory_with_v3_summary(baseURL, projectID, authToken)
        except:
            logger.error("    No Project Information Returned!")
            print("No Project Information Returned.")
            return -1

        # Get details for  project
        try:
            projectInventoryResponse = CodeInsight_RESTAPIs.project.get_project_inventory.get_project_inventory_details(baseURL, projectID, authToken)
        except:
            logger.error("    No project ineventory response!")
            print("No project inventory response.")
            return -1



        # Create empty dictionary for project level data for this project
        projectData[projectName] = {}

        #############################################
        #  This area will be replaced by 2020R4 APIs
        numApproved = 0
        numRejected = 0
        numDraft = 0

        inventoryItems = projectInventoryResponse["inventoryItems"]
        currentItem=0

        for inventoryItem in projectInventorySummary:
            currentItem +=1

            inventoryItemName = inventoryItem["name"]
            componentName = inventoryItem["componentName"]
            inventoryPriority = inventoryItem["priority"]
            componentVersionName = inventoryItem["componentVersionName"]
            selectedLicenseID = inventoryItem["selectedLicenseId"]
            selectedLicenseSPDXIdentifier = inventoryItem["selectedLicenseSPDXIdentifier"]
            selectedLicenseUrl = "www.revenera.com"  # Retreive from license API
            componentUrl = inventoryItem["url"]
            
            inventoryID = inventoryItem["id"]
            inventoryReviewStatus = inventoryItem["reviewStatus"]          
            inventoryLink = baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(projectID) + "&tab=projectInventory&pinv=" + str(inventoryID)
            
            logger.debug("Processing inventory items %s of %s" %(currentItem, len(inventoryItems)))
            logger.debug("    %s" %(inventoryItemName))
            
            try:
                vulnerabilities = inventoryItem["vulnerabilitySummary"][0]["CVSS3.0"]
                vulnerabilityData = create_inventory_summary_dict(vulnerabilities)
            except:
                logger.debug("No vulnerabilies for %s - %s" %(componentName, componentVersionName))
                vulnerabilityData = ""

            # If there is a SPDX value use that otherwise use the full name based on the             
            if selectedLicenseSPDXIdentifier == "":
                selectedLicenseName = selectedLicenseID
            else:
                selectedLicenseName = selectedLicenseSPDXIdentifier

            inventoryData[inventoryID] = {
                "projectName" : projectName,
                "inventoryItemName" : inventoryItemName,
                "componentName" : componentName,
                "componentVersionName" : componentVersionName,
                "selectedLicenseName" : selectedLicenseName,
                "vulnerabilityData" : vulnerabilityData,
                "inventoryPriority" : inventoryPriority,
                "componentUrl" : componentUrl,
                "selectedLicenseUrl" : selectedLicenseUrl,
                "inventoryReviewStatus" : inventoryReviewStatus,
                "inventoryLink" : inventoryLink,
                "projectLink" : projectLink
            }

            #############################################
            # Sum up inventory review status data
            if inventoryReviewStatus == "Approved":
                numApproved += 1
            elif inventoryReviewStatus == "Rejected":
                numRejected += 1
            elif inventoryReviewStatus == "Draft":
                numDraft += 1
            else:
                logger.error("Unknown inventoryReview Status: %s" %inventoryReviewStatus)

        # Group all inventory based data into a dict wit the project name as the key
        projectData[projectName]["numApproved"] = numApproved
        projectData[projectName]["numRejected"] = numRejected
        projectData[projectName]["numDraft"] = numDraft
        projectData[projectName]["numP1Licenses"] = projectInformation["licenses"]["P1"]
        projectData[projectName]["numP2Licenses"] = projectInformation["licenses"]["P2"]
        projectData[projectName]["numP3Licenses"] = projectInformation["licenses"]["P3"]
        projectData[projectName]["numNALicenses"] = projectInformation["licenses"]["Unknown"]
        projectData[projectName]["numCriticalVulnerabilities"] = projectInformation["vulnerabilities"]["CVSS3.0"]["Critical"]
        projectData[projectName]["numHighVulnerabilities"] = projectInformation["vulnerabilities"]["CVSS3.0"]["High"]
        projectData[projectName]["numMediumVulnerabilities"] = projectInformation["vulnerabilities"]["CVSS3.0"]["Medium"]
        projectData[projectName]["numLowVulnerabilities"] = projectInformation["vulnerabilities"]["CVSS3.0"]["Low"]
        projectData[projectName]["numNoneVulnerabilities"] = projectInformation["vulnerabilities"]["CVSS3.0"]["None"]
        projectData[projectName]["projectLink"] = projectLink

    # Roll up the inventortory data at a project level for display charts
    projectSummaryData = create_project_summary_data_dict(projectData)

    # Roll up the individual project data to the application level
    applicationSummaryData = create_application_summary_data_dict(projectSummaryData)

    # Build up the data to return for the
    reportData = {}
    reportData["reportName"] = reportName
    reportData["projectName"] = projectHierarchy["name"]
    reportData["inventoryData"] = inventoryData
    reportData["projectList"] =projectList
    reportData["projectSummaryData"] = projectSummaryData
    reportData["applicationSummaryData"] = applicationSummaryData


    logger.info("Exiting gather_data_for_report")

    return reportData
  
#----------------------------------------------------------------------
def create_inventory_summary_dict(vulnerabilities):
    logger.info("Entering create_inventory_summary_dict")
    
    vulnerabilityData = {}
    vulnerabilityData["numTotalVulnerabilities"] = sum(vulnerabilities.values())
    vulnerabilityData["numCriticalVulnerabilities"] = vulnerabilities["Critical"]
    vulnerabilityData["numHighVulnerabilities"] = vulnerabilities["High"]
    vulnerabilityData["numMediumVulnerabilities"] = vulnerabilities["Medium"]
    vulnerabilityData["numLowVulnerabilities"] = vulnerabilities["Low"]
    vulnerabilityData["numNoneVulnerabilities"] = vulnerabilities["None"]

    return vulnerabilityData

#----------------------------------------------#
def create_project_hierarchy(project, parentID, projectList, baseURL):
    logger.debug("Entering create_project_hierarchy")

    # Are there more child projects for this project?
    if len(project["childProject"]):

        # Sort by project name of child projects
        for childProject in sorted(project["childProject"], key = lambda i: i['name'] ) :

            nodeDetails = {}
            nodeDetails["projectID"] = childProject["id"]
            nodeDetails["parent"] = parentID
            nodeDetails["projectName"] = childProject["name"]
            nodeDetails["projectLink"] = baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(childProject["id"]) + "&tab=projectInventory"

            projectList.append( nodeDetails )

            create_project_hierarchy(childProject, childProject["id"], projectList, baseURL)

    return projectList


#----------------------------------------------------------------------------------------#
def create_project_summary_data_dict(projectData):
    logger.debug("Entering get_project_summary_data")

   # For the chart data we need to create lists where each element is in the correct order based on the 
   # project name order.  i.e. one list will # of approved items for each project in the correct order
    projectSummaryData = {}

    # Create empty lists for each metric that we need for the report
    for projectName in projectData:
        for metric in projectData[projectName]:
            if metric not in  ["P1InventoryItems", "projectLink"]:  # We don't care about these for now
                projectSummaryData[metric] = []

    # Grab the data for each project and add it in the correct order
    for projectName in projectData:
        for metric in projectData[projectName]:
            if metric not in  ["P1InventoryItems", "projectLink"]:  # We don't care about these for now
                projectSummaryData[metric].append(projectData[projectName][metric])

    projectSummaryData["projectNames"] = list(projectData.keys())
    
    logger.debug("Exiting get_project_summary_data")
    return projectSummaryData
    
#----------------------------------------------------------------------------------------#
def create_application_summary_data_dict(projectSummaryData):
    logger.debug("Entering get_application_summary_data")

    applicationSummaryData = {}

    # For each metric sum the data up
    for metric in projectSummaryData:
        if metric != "projectNames":
            applicationSummaryData[metric] = sum(projectSummaryData[metric])

    logger.debug("Exiting get_application_summary_data")
    return applicationSummaryData




    