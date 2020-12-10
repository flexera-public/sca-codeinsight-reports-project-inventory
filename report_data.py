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
        numP1Licenses = 0
        numP2Licenses = 0
        numP3Licenses = 0
        numNALicenses = 0
        numTotalVulnerabilities = 0
        numCriticalVulnerabilities = 0
        numHighVulnerabilities = 0
        numMediumVulnerabilities = 0
        numLowVulnerabilities = 0
        numNoneVulnerabilities = 0

        inventoryItems = projectInventoryResponse["inventoryItems"]
        currentItem=0

        for inventoryItem in inventoryItems:
            currentItem +=1

            inventoryItemName = inventoryItem["name"]
            componentName = inventoryItem["componentName"]
            inventoryPriority = inventoryItem["priority"]
            componentVersionName = inventoryItem["componentVersionName"]
            selectedLicenseName = inventoryItem["selectedLicenseName"]
            selectedLicenseSPDXIdentifier = inventoryItem["selectedLicenseSPDXIdentifier"]
            selectedLicensePriority = inventoryItem["selectedLicensePriority"]
            componentUrl = inventoryItem["componentUrl"]
            selectedLicenseUrl = inventoryItem["selectedLicenseUrl"]
            inventoryID = inventoryItem["id"]
            inventoryReviewStatus = inventoryItem["inventoryReviewStatus"]          
            inventoryLink = baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(projectID) + "&tab=projectInventory&pinv=" + str(inventoryID)
            
            logger.debug("Processing inventory items %s of %s" %(currentItem, len(inventoryItems)))
            logger.debug("    %s" %(inventoryItemName))
            
            try:
                vulnerabilities = inventoryItem["vulnerabilities"]
                vulnerabilityData = create_inventory_summary_dict(vulnerabilities)
            except:
                logger.debug("No vulnerabilies for %s - %s" %(componentName, componentVersionName))
                vulnerabilityData = ""

            if selectedLicenseSPDXIdentifier != "":
                selectedLicenseName = selectedLicenseSPDXIdentifier

            inventoryData[inventoryID] = {
                "projectName" : projectName,
                "projectID" : projectID,
                "inventoryItemName" : inventoryItemName,
                "componentName" : componentName,
                "componentVersionName" : componentVersionName,
                "selectedLicenseName" : selectedLicenseName,
                "vulnerabilityData" : vulnerabilityData,
                "selectedLicensePriority" : selectedLicensePriority,
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


            #############################################
            #  This area will be replaced by 2020R4 APIs

            if selectedLicensePriority == 1:
                numP1Licenses += 1
            elif selectedLicensePriority == 2:
                numP2Licenses += 1
            elif selectedLicensePriority == 3:
                numP3Licenses += 1
            elif selectedLicensePriority == "N/A":
                numNALicenses += 1
            else:
                logger.error("Unknown license priority: %s" %selectedLicensePriority)

            if vulnerabilityData != "":
                numTotalVulnerabilities += vulnerabilityData["numTotalVulnerabilities"]  # Used to determine if there are any vuln at all for display purposes
                numCriticalVulnerabilities += vulnerabilityData["numCriticalVulnerabilities"]
                numHighVulnerabilities += vulnerabilityData["numHighVulnerabilities"]
                numMediumVulnerabilities += vulnerabilityData["numMediumVulnerabilities"]
                numLowVulnerabilities += vulnerabilityData["numLowVulnerabilities"]
                numNoneVulnerabilities += vulnerabilityData["numNoneVulnerabilities"]

        # Group all inventory based data into a dict wit the project name as the key
        projectData[projectName]["numApproved"] = numApproved
        projectData[projectName]["numRejected"] = numRejected
        projectData[projectName]["numDraft"] = numDraft
        projectData[projectName]["numP1Licenses"] = numP1Licenses
        projectData[projectName]["numP2Licenses"] = numP2Licenses
        projectData[projectName]["numP3Licenses"] = numP3Licenses
        projectData[projectName]["numNALicenses"] = numNALicenses
        projectData[projectName]["numTotalVulnerabilities"] = numTotalVulnerabilities
        projectData[projectName]["numCriticalVulnerabilities"] = numCriticalVulnerabilities
        projectData[projectName]["numHighVulnerabilities"] = numHighVulnerabilities
        projectData[projectName]["numMediumVulnerabilities"] = numMediumVulnerabilities
        projectData[projectName]["numLowVulnerabilities"] = numLowVulnerabilities
        projectData[projectName]["numNoneVulnerabilities"] = numNoneVulnerabilities
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
    logger.info("Entering get_vulnerability_summary")

    numCriticalVulnerabilities = 0
    numHighVulnerabilities = 0
    numMediumVulnerabilities = 0
    numLowVulnerabilities = 0
    numNoneVulnerabilities = 0
    vulnerabilityData = {}

    numTotalVulnerabilities = len(vulnerabilities)

    for vulnerability in vulnerabilities:

        vulnerabilityCvssV3Severity = vulnerability["vulnerabilityCvssV3Severity"]

        if vulnerabilityCvssV3Severity == "CRITICAL":
            numCriticalVulnerabilities +=1
        elif vulnerabilityCvssV3Severity == "HIGH":
            numHighVulnerabilities +=1
        elif vulnerabilityCvssV3Severity == "MEDIUM":
            numMediumVulnerabilities +=1
        elif vulnerabilityCvssV3Severity == "LOW":
            numLowVulnerabilities +=1
        elif vulnerabilityCvssV3Severity == "N/A" or vulnerabilityCvssV3Severity == "NONE":
            numNoneVulnerabilities +=1       
        else:
            logger.error("Unknown vulnerability severity: %s" %vulnerabilityCvssV3Severity)

    vulnerabilityData["numTotalVulnerabilities"] = numTotalVulnerabilities
    vulnerabilityData["numCriticalVulnerabilities"] = numCriticalVulnerabilities
    vulnerabilityData["numHighVulnerabilities"] = numHighVulnerabilities
    vulnerabilityData["numMediumVulnerabilities"] = numMediumVulnerabilities
    vulnerabilityData["numLowVulnerabilities"] = numLowVulnerabilities
    vulnerabilityData["numNoneVulnerabilities"] = numNoneVulnerabilities

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




    