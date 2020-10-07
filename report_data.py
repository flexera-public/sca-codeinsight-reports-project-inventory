'''
Copyright 2020 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Fri Aug 07 2020
File : report_data.py
'''

import logging
from operator import itemgetter
import CodeInsight_RESTAPIs.project.get_child_projects
import CodeInsight_RESTAPIs.project.get_project_inventory

logger = logging.getLogger(__name__)

#-------------------------------------------------------------------#
def gather_data_for_report(baseURL, projectID, authToken, reportName):
    logger.info("Entering gather_data_for_report")

    projectIDs = [] # Create a list to contain a list of all project IDs
    childProjectMappings = {}  # Create a dictionary to map parent to child projects wtih parent ID as key
    inventoryData = {}  # Create a dictionary containing the inventory data using inventoryID as keys
    projectData = {} # Create a dictionary containing the project level summary data using projectID as keys

    # Get the list of parent/child projects start at the base project
    projectHierarchy = CodeInsight_RESTAPIs.project.get_child_projects.get_child_projects_recursively(baseURL, projectID, authToken)
    baseProjectName = projectHierarchy["name"]

    projectIDs, childProjectMappings = get_direct_child_project_details(projectHierarchy, projectIDs, childProjectMappings)

    for projectID in projectIDs:
        # Get details for  project
        try:
            projectInventoryResponse = CodeInsight_RESTAPIs.project.get_project_inventory.get_project_inventory_details(baseURL, projectID, authToken)
        except:
            logger.error("    No project ineventory response!")
            print("No project inventory response.")
            return -1

        # Create empty dictionary for project level data for this project
        projectData[projectID] = {}

        #############################################
        #  This area will be replaced by 2020R4 APIs
        P1InventoryItems = 0
        numApproved = 0
        numRejected = 0
        numDraft = 0
        P1Licenses = 0
        P2Licenses = 0
        P3Licenses = 0
        NALicenses = 0
        numTotalVulnerabilities = 0
        numCriticalVulnerabilities = 0
        numHighVulnerabilities = 0
        numMediumVulnerabilities = 0
        numLowVulnerabilities = 0
        numNoneVulnerabilities = 0

        projectName = projectInventoryResponse["projectName"]
        inventoryItems = projectInventoryResponse["inventoryItems"]
        totalNumberIventory = len(inventoryItems)
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
            projectLink = baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(projectID) + "&tab=projectInventory"
            

            logger.debug("Processing iventory items %s of %s" %(currentItem, totalNumberIventory))
            logger.debug("    %s" %(inventoryItemName))
            
            try:
                vulnerabilities = inventoryItem["vulnerabilities"]
                vulnerabilityData = get_vulnerability_summary(vulnerabilities)
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
            if inventoryPriority == "High":  # this is P1 inventory item
                P1InventoryItems +=1

            if selectedLicensePriority == 1:
                P1Licenses += 1
            elif selectedLicensePriority == 2:
                P2Licenses += 1
            elif selectedLicensePriority == 3:
                P3Licenses += 1
            elif selectedLicensePriority == "N/A":
                NALicenses += 1
            else:
                logger.error("Unknown license priority: %s" %selectedLicensePriority)

            if vulnerabilityData != "":
                numTotalVulnerabilities += vulnerabilityData["numTotalVulnerabilities"]
                numCriticalVulnerabilities += vulnerabilityData["numCriticalVulnerabilities"]
                numHighVulnerabilities += vulnerabilityData["numHighVulnerabilities"]
                numMediumVulnerabilities += vulnerabilityData["numMediumVulnerabilities"]
                numLowVulnerabilities += vulnerabilityData["numLowVulnerabilities"]
                numNoneVulnerabilities += vulnerabilityData["numNoneVulnerabilities"]

        projectData[projectID]["projectName"] = projectName
        projectData[projectID]["P1InventoryItems"] = P1InventoryItems
        projectData[projectID]["numApproved"] = numApproved
        projectData[projectID]["numRejected"] = numRejected
        projectData[projectID]["numDraft"] = numDraft
        projectData[projectID]["P1Licenses"] = P1Licenses
        projectData[projectID]["P2Licenses"] = P2Licenses
        projectData[projectID]["P3Licenses"] = P3Licenses
        projectData[projectID]["NALicenses"] = NALicenses
        projectData[projectID]["numTotalVulnerabilities"] = numTotalVulnerabilities
        projectData[projectID]["numCriticalVulnerabilities"] = numCriticalVulnerabilities
        projectData[projectID]["numHighVulnerabilities"] = numHighVulnerabilities
        projectData[projectID]["numMediumVulnerabilities"] = numMediumVulnerabilities
        projectData[projectID]["numLowVulnerabilities"] = numLowVulnerabilities
        projectData[projectID]["numNoneVulnerabilities"] = numNoneVulnerabilities
        projectData[projectID]["projectLink"] = baseURL + "/codeinsight/FNCI#myprojectdetails/?id=" + str(projectID) + "&tab=projectInventory"


    # Roll up the project summarys for the full product
    productData = calculate_product_summary(projectData)
                

    reportData = {}
    reportData["reportName"] = reportName
    reportData["projectID"] = projectID
    reportData["baseProjectName"] = baseProjectName
    reportData["projectHierarchy"] =projectHierarchy
    reportData["inventoryData"] = inventoryData
    reportData["projectData"] = projectData
    reportData["productData"] = productData
    reportData["baseURL"] = baseURL

    logger.info("Exiting gather_data_for_report")

    return reportData


#----------------------------------------------------------------------------------------#
def project_sort(projects):
    return sorted(projects, key=lambda projects: projects.name)
   
#----------------------------------------------------------------------------------------#
def get_direct_child_project_details(projectHierarchy, projectIDs, childProjectMappings):
    
    # Recursive function to get the required data from a child project
    projectID = projectHierarchy["id"]
    projectIDs.append(projectID)
    childProjects = projectHierarchy["childProject"]

    if len(childProjects) > 0:
        childProjectMappings[projectID] = []
      
        for childProject in childProjects:
            childProjectID = childProject["id"]
            childProjectMappings[projectID].append(childProjectID)

            projectIDs, childProjectMappings = get_direct_child_project_details(childProject, projectIDs, childProjectMappings)

    return projectIDs, childProjectMappings

#----------------------------------------------------------------------
def get_vulnerability_summary(vulnerabilities):
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
        elif vulnerabilityCvssV3Severity == "N/A":
            numNoneVulnerabilities +=1
        elif vulnerabilityCvssV3Severity == "NONE":
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


#----------------------------------------------------------------------
def calculate_product_summary(projectData):

    productData = {}
    productData["numApproved"] = 0
    productData["numRejected"] = 0
    productData["numDraft"] = 0
    productData["P1Licenses"] = 0
    productData["P2Licenses"] = 0
    productData["P3Licenses"] = 0
    productData["NALicenses"] = 0
    productData["numTotalVulnerabilities"] = 0
    productData["numCriticalVulnerabilities"] = 0
    productData["numHighVulnerabilities"] = 0
    productData["numMediumVulnerabilities"] = 0
    productData["numLowVulnerabilities"] = 0
    productData["numNoneVulnerabilities"] = 0

    for project in projectData:

        productData["numApproved"] += projectData[project]["numApproved"]
        productData["numRejected"] += projectData[project]["numRejected"] 
        productData["numDraft"] += projectData[project]["numDraft"] 

        productData["P1Licenses"] += projectData[project]["P1Licenses"]
        productData["P2Licenses"] += projectData[project]["P2Licenses"] 
        productData["P3Licenses"]  += projectData[project]["P3Licenses"] 
        productData["NALicenses"] += projectData[project]["NALicenses"]
        productData["numTotalVulnerabilities"] += projectData[project]["numTotalVulnerabilities"]
        productData["numCriticalVulnerabilities"] += projectData[project]["numCriticalVulnerabilities"]
        productData["numHighVulnerabilities"] += projectData[project]["numHighVulnerabilities"]
        productData["numMediumVulnerabilities"] += projectData[project]["numMediumVulnerabilities"]
        productData["numLowVulnerabilities"] += projectData[project]["numLowVulnerabilities"]
        productData["numNoneVulnerabilities"] += projectData[project]["numNoneVulnerabilities"]

    return productData
    