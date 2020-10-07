'''
Copyright 2020 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Fri Aug 07 2020
File : report_artifacts.py
'''

import logging
import os
from datetime import datetime
import base64
import json
from anytree.importer import DictImporter
from anytree import RenderTree, AsciiStyle

logger = logging.getLogger(__name__)

#--------------------------------------------------------------------------------#
def create_report_artifacts(reportData):
    logger.info("Entering create_report_artifacts")

    # Dict to hold the complete list of reports
    reports = {}

    htmlFile = generate_html_report(reportData)
    
    reports["viewable"] = htmlFile
    reports["allFormats"] = [htmlFile]

    logger.info("Exiting create_report_artifacts")
    
    return reports 


#------------------------------------------------------------------#
def generate_html_report(reportData):
    logger.info("    Entering generate_html_report")

    reportName = reportData["reportName"]
    baseProjectName  = reportData["baseProjectName"]
    projectID  = reportData["projectID"]
    baseURL  = reportData["baseURL"]
    inventoryData = reportData["inventoryData"]
    projectHierarchy = reportData["projectHierarchy"]
    projectData = reportData["projectData"]
    productData = reportData["productData"]
    
    scriptDirectory = os.path.dirname(os.path.realpath(__file__))
    cssFile =  os.path.join(scriptDirectory, "html-assets/css/revenera_common.css")
    logoImageFile =  os.path.join(scriptDirectory, "html-assets/images/logo_reversed.svg")
    iconFile =  os.path.join(scriptDirectory, "html-assets/images/favicon-revenera.ico")
    statusApprovedIcon = os.path.join(scriptDirectory, "html-assets/images/status_approved_selected.png")
    statusRejectedIcon = os.path.join(scriptDirectory, "html-assets/images/status_rejected_selected.png")
    statusDraftIcon = os.path.join(scriptDirectory, "html-assets/images/status_draft_ready_selected.png")

    logger.debug("cssFile: %s" %cssFile)
    logger.debug("imageFile: %s" %logoImageFile)
    logger.debug("iconFile: %s" %iconFile)
    logger.debug("statusApprovedIcon: %s" %statusApprovedIcon)
    logger.debug("statusRejectedIcon: %s" %statusRejectedIcon)
    logger.debug("statusDraftIcon: %s" %statusDraftIcon)


    #########################################################
    #  Encode the image files
    encodedLogoImage = encodeImage(logoImageFile)
    encodedfaviconImage = encodeImage(iconFile)
    encodedStatusApprovedIcon = encodeImage(statusApprovedIcon)
    encodedStatusRejectedIcon = encodeImage(statusRejectedIcon)
    encodedStatusDraftIcon = encodeImage(statusDraftIcon)

    # Grab the current date/time for report date stamp
    now = datetime.now().strftime("%B %d, %Y at %H:%M:%S")

    htmlFile = reportName + ".html"
    logger.debug("htmlFile: %s" %htmlFile)

    #---------------------------------------------------------------------------------------------------
    # Create a simple HTML file to display
    #---------------------------------------------------------------------------------------------------
    try:
        html_ptr = open(htmlFile,"w")
    except:
        logger.error("Failed to open htmlfile %s:" %htmlFile)
        raise

    html_ptr.write("<html>\n") 
    html_ptr.write("    <head>\n")

    html_ptr.write("        <!-- Required meta tags --> \n")
    html_ptr.write("        <meta charset='utf-8'>  \n")
    html_ptr.write("        <meta name='viewport' content='width=device-width, initial-scale=1, shrink-to-fit=no'> \n")

    html_ptr.write(''' 
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.1/css/bootstrap.min.css" integrity="sha384-VCmXjywReHh4PwowAiWNagnWcLhlEJLA5buUprzK8rxFgeH0kww/aWY76TfkUoSX" crossorigin="anonymous">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.1.3/css/bootstrap.css">
        <link rel="stylesheet" href="https://cdn.datatables.net/1.10.21/css/dataTables.bootstrap4.min.css">
    ''')


    html_ptr.write("        <style>\n")

    # Add the contents of the css file to the head block
    try:
        f_ptr = open(cssFile)
        logger.debug("Adding css file details")
        for line in f_ptr:
            html_ptr.write("            %s" %line)
        f_ptr.close()
    except:
        logger.error("Unable to open %s" %cssFile)
        print("Unable to open %s" %cssFile)

    html_ptr.write('''
        pre {
            display: inline;
            margin: 0;  
           }
    ''')     

    html_ptr.write("        </style>\n")  

    html_ptr.write("    	<link rel='icon' type='image/png' href='data:image/png;base64, {}'>\n".format(encodedfaviconImage.decode('utf-8')))
    html_ptr.write("        <title>%s</title>\n" %(reportName.upper()))
    html_ptr.write("    </head>\n") 

    html_ptr.write("<body>\n")
    html_ptr.write("<div class=\"container-fluid\">\n")

    #---------------------------------------------------------------------------------------------------
    # Report Header
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN HEADER -->\n")
    html_ptr.write("<div class='header'>\n")
    html_ptr.write("  <div class='logo'>\n")
    html_ptr.write("    <img src='data:image/svg+xml;base64,{}' style='width: 400px;'>\n".format(encodedLogoImage.decode('utf-8')))
    html_ptr.write("  </div>\n")
    html_ptr.write("<div class='report-title'>%s</div>\n" %reportName)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END HEADER -->\n")

    #---------------------------------------------------------------------------------------------------
    # Body of Report
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN BODY -->\n")  


    display_simple_project_hierarchy(html_ptr, projectID, baseProjectName, projectHierarchy)

    html_ptr.write("<hr class='small'>")

    display_product_summary_table(html_ptr, productData, encodedStatusApprovedIcon, encodedStatusRejectedIcon, encodedStatusDraftIcon)

    html_ptr.write("<hr class='small'>")

    display_project_summary_table(html_ptr, projectData, encodedStatusApprovedIcon, encodedStatusRejectedIcon, encodedStatusDraftIcon)

    html_ptr.write("<hr class='small'>")

    html_ptr.write("<table id='inventoryData' class='table table-hover table-sm row-border' style='width:90%'>\n")

    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th colspan='8' class='text-center'><h4>Inventory Items</h4></th>\n") 
    html_ptr.write("        </tr>\n") 
    html_ptr.write("        <tr>\n") 
    html_ptr.write("            <th style='width: 15%' class='text-center'>PROJECT</th>\n") 
    html_ptr.write("            <th style='width: 25%' class='text-center'>INVENTORY ITEM</th>\n") 
    html_ptr.write("            <th style='width: 10%' class='text-center'>PRIORITY</th>\n") 
    html_ptr.write("            <th style='width: 15%' class='text-center'>COMPONENT</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>VERSION</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>LICENSE</th>\n") 
    html_ptr.write("            <th style='width: 18%' class='text-center'>VULNERABILITIES</th>\n")
    html_ptr.write("            <th style='width: 7%' class='text-center'>REVIEW STATUS</th>\n")
    html_ptr.write("        </tr>\n")
    html_ptr.write("    </thead>\n")  
    html_ptr.write("    <tbody>\n")  

    ######################################################
    # Cycle through the inventory to create the 
    # table with the results
    for inventoryID in sorted(inventoryData):
        projectName = inventoryData[inventoryID]["projectName"]
        projectID = inventoryData[inventoryID]["projectID"]
        inventoryItemName = inventoryData[inventoryID]["inventoryItemName"]
        componentName = inventoryData[inventoryID]["componentName"]
        componentVersionName = inventoryData[inventoryID]["componentVersionName"]
        inventoryPriority = inventoryData[inventoryID]["inventoryPriority"]
        selectedLicenseName = inventoryData[inventoryID]["selectedLicenseName"]
        selectedLicensePriority = inventoryData[inventoryID]["selectedLicensePriority"]
        vulnerabilityData = inventoryData[inventoryID]["vulnerabilityData"]
        componentUrl = inventoryData[inventoryID]["componentUrl"]
        selectedLicenseUrl = inventoryData[inventoryID]["selectedLicenseUrl"]
        inventoryReviewStatus = inventoryData[inventoryID]["inventoryReviewStatus"]

        logger.debug("Reporting for inventory item %s" %inventoryID)

        numTotalVulnerabilities = 0
        numCriticalVulnerabilities = 0
        numHighVulnerabilities = 0
        numMediumVulnerabilities = 0
        numLowVulnerabilities = 0
        numNoneVulnerabilities = 0

        try:
            numTotalVulnerabilities = vulnerabilityData["numTotalVulnerabilities"]
            numCriticalVulnerabilities = vulnerabilityData["numCriticalVulnerabilities"]
            numHighVulnerabilities = vulnerabilityData["numHighVulnerabilities"]
            numMediumVulnerabilities = vulnerabilityData["numMediumVulnerabilities"]
            numLowVulnerabilities = vulnerabilityData["numLowVulnerabilities"]
            numNoneVulnerabilities = vulnerabilityData["numNoneVulnerabilities"]
        except:
            logger.debug("    No vulnerability data")

        html_ptr.write("        <tr> \n")

        html_ptr.write("            <td class='text-left'>%s</td>\n" %(projectName))
        html_ptr.write("            <td class='text-left'><a href='%s/codeinsight/FNCI#myprojectdetails/?id=%s&tab=projectInventory&pinv=%s' target='_blank'>%s</a></td>\n" %(baseURL, projectID, inventoryID, inventoryItemName))
 

        if inventoryPriority == "High":
            html_ptr.write("            <td data-sort='4' class='text-left text-nowrap'><span class='dot dot-red'></span>P1 - %s</td>\n" %(inventoryPriority))
        elif inventoryPriority == "Medium":
            html_ptr.write("            <td data-sort='3' class='text-left text-nowrap'><span class='dot dot-yellow'></span>P2 - %s</td>\n" %(inventoryPriority))
        elif inventoryPriority == "Low":
            html_ptr.write("            <td data-sort='2' class='text-left text-nowrap'><span class='dot dot-green'></span>P3 - %s</td>\n" %(inventoryPriority))
        elif inventoryPriority == "Other":
            html_ptr.write("            <td data-sort='1' class='text-left text-nowrap'><span class='dot dot-blue'></span>P4 - %s</td>\n" %(inventoryPriority))
        else:
            html_ptr.write("            <td class='text-left text-nowrap'><span class='dot dot-gray'></span>%s</td>\n" %(inventoryPriority))

        
        html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(componentUrl, componentName))
        html_ptr.write("            <td class='text-left'>%s</td>\n" %(componentVersionName))
        html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(selectedLicenseUrl, selectedLicenseName))
        html_ptr.write("            <td class='text-center text-nowrap' data-sort='%s' >\n" %numCriticalVulnerabilities)
        
        # Write in single line to remove spaces between btn spans
        if numTotalVulnerabilities > 0:
            html_ptr.write("                <span class='btn btn-vuln btn-critical'>%s</span>\n" %(numCriticalVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-high'>%s</span>\n" %(numHighVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-medium'>%s</span>\n" %(numMediumVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-low'>%s</span>\n" %(numLowVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-none'>%s</span>\n" %(numNoneVulnerabilities))
        else:
            html_ptr.write("                <span class='btn btn-vuln btn-no-vulns'>None</span>\n")

        if inventoryReviewStatus == "Approved":
            html_ptr.write("            <td class='text-left text-nowrap' style='color:green;'><img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s</td>\n" %(encodedStatusApprovedIcon.decode('utf-8'), inventoryReviewStatus))
        elif inventoryReviewStatus == "Rejected":
            html_ptr.write("            <td class='text-left text-nowrap' style='color:red;'><img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s</td>\n" %(encodedStatusRejectedIcon.decode('utf-8'), inventoryReviewStatus))
        elif inventoryReviewStatus == "Draft":
            html_ptr.write("            <td class='text-left text-nowrap' style='color:gray;'><img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s</td>\n" %(encodedStatusDraftIcon.decode('utf-8'), inventoryReviewStatus))
        else:
            html_ptr.write("            <td class='text-left text-nowrap'>%s</td>\n" %(inventoryReviewStatus))

        html_ptr.write("            </td>\n")

        html_ptr.write("        </tr>\n") 
    html_ptr.write("    </tbody>\n")


    html_ptr.write("</table>\n")  

    html_ptr.write("<!-- END BODY -->\n")  

    #---------------------------------------------------------------------------------------------------
    # Report Footer
    #---------------------------------------------------------------------------------------------------
    html_ptr.write("<!-- BEGIN FOOTER -->\n")
    html_ptr.write("<div class='report-footer'>\n")
    html_ptr.write("  <div style='float:left'>&copy; 2020 Revenera</div>\n")
    html_ptr.write("  <div style='float:right'>Generated on %s</div>\n" %now)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END FOOTER -->\n")   

    html_ptr.write("</div>\n")

    #---------------------------------------------------------------------------------------------------
    # Add javascript 
    #---------------------------------------------------------------------------------------------------

    html_ptr.write('''

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>  
    <script src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script> 
    ''')


    html_ptr.write('''
        <script>
            var table = $('#inventoryData').DataTable();

            $(document).ready(function() {
                table;
            } );

        </script>


        ''')

    html_ptr.write("</body>\n") 
    html_ptr.write("</html>\n") 
    html_ptr.close() 

    logger.info("    Exiting generate_html_report")
    return htmlFile


####################################################################
def encodeImage(imageFile):

    #############################################
    # Create base64 variable for branding image
    try:
        with open(imageFile,"rb") as image:
            logger.debug("Encoding image: %s" %imageFile)
            encodedImage = base64.b64encode(image.read())
            return encodedImage
    except:
        logger.error("Unable to open %s" %imageFile)
        raise

#----------------------------------------------------------------------------------------#
def display_simple_project_hierarchy(html_ptr, projectID, projectName, projectChildren):

    logger.debug("Entering display_simple_project_hierarchy for %s" %projectName) 

    importer = DictImporter()
    # Clean up the dictionary for anytree
    updatedProjectChildren = json.loads(json.dumps(projectChildren).replace('"childProject":', '"children":'))
    root = importer.import_(updatedProjectChildren)

    for row in RenderTree(root, style=AsciiStyle(), childiter=project_sort):

        projectName = row.node.name
        projectID = row.node.id

        html_ptr.write("<pre>%s</pre>%s<br>\n" %(row.pre, projectName))

#----------------------------------------------------------------------------------------#
def project_sort(projects):
    return sorted(projects, key=lambda projects: projects.name)

#----------------------------------------------------------------------------------------#
def display_project_summary_table(html_ptr, projectData, encodedStatusApprovedIcon, encodedStatusRejectedIcon, encodedStatusDraftIcon):
   
    html_ptr.write("<table id='projectSummaryData' class='table table-hover table-sm row-border' style='width:90%'>\n")

    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th colspan='8' class='text-center'><h4>Project Summary</h4></th>\n") 
    html_ptr.write("        </tr>\n") 
    html_ptr.write("        <tr>\n") 
    html_ptr.write("            <th style='width: 15%' class='text-center'>PROJECT NAME</th>\n") 
    html_ptr.write("            <th style='width: 10%' class='text-center'>LICENSE PRIORITIES</th>\n") 
    html_ptr.write("            <th style='width: 15%' class='text-center'>VULNERABILITIES</th>\n")
    html_ptr.write("            <th style='width: 15%' class='text-center'>REVIEW SUMMARY</th>\n")
    html_ptr.write("        </tr>\n")
    html_ptr.write("    </thead>\n")  
    html_ptr.write("    <tbody>\n")

    for project in projectData:
        projectName = projectData[project]["projectName"]
        numApproved = projectData[project]["numApproved"]
        numRejected = projectData[project]["numRejected"] 
        numDraft = projectData[project]["numDraft"] 
        P1Licenses = projectData[project]["P1Licenses"]
        P2Licenses = projectData[project]["P2Licenses"] 
        P3Licenses = projectData[project]["P3Licenses"] 
        NALicenses = projectData[project]["NALicenses"]
        numTotalVulnerabilities = projectData[project]["numTotalVulnerabilities"]
        numCriticalVulnerabilities = projectData[project]["numCriticalVulnerabilities"]
        numHighVulnerabilities = projectData[project]["numHighVulnerabilities"]
        numMediumVulnerabilities = projectData[project]["numMediumVulnerabilities"]
        numLowVulnerabilities = projectData[project]["numLowVulnerabilities"]
        numNoneVulnerabilities = projectData[project]["numNoneVulnerabilities"]
                
        
        html_ptr.write("        <tr> \n")
        html_ptr.write("            <td class='text-left'>%s</td>\n" %(projectName))

        html_ptr.write("            <td class='text-center text-nowrap' data-sort='%s' >\n" %P1Licenses)
        html_ptr.write("                <span class='btn btn-vuln btn-high'>%s</span>\n" %(P1Licenses))
        html_ptr.write("                <span class='btn btn-vuln btn-medium'>%s</span>\n" %(P2Licenses))
        html_ptr.write("                <span class='btn btn-vuln btn-low'>%s</span>\n" %(P3Licenses))
        html_ptr.write("                <span class='btn btn-vuln btn-none'>%s</span>\n" %(NALicenses))
        html_ptr.write("            </td>\n")


        html_ptr.write("            <td class='text-center text-nowrap' data-sort='%s' >\n" %numCriticalVulnerabilities)
        # Write in single line to remove spaces between btn spans
        if numTotalVulnerabilities > 0:
            html_ptr.write("                <span class='btn btn-vuln btn-critical'>%s</span>\n" %(numCriticalVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-high'>%s</span>\n" %(numHighVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-medium'>%s</span>\n" %(numMediumVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-low'>%s</span>\n" %(numLowVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-none'>%s</span>\n" %(numNoneVulnerabilities))
        else:
            html_ptr.write("                <span class='btn btn-vuln btn-no-vulns'>None</span>\n")
        html_ptr.write("            </td> \n")
        
        html_ptr.write("            <td class='text-center text-nowrap' style='color:gray;'>")
        html_ptr.write("                <img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s" %(encodedStatusApprovedIcon.decode('utf-8'), numApproved))
        html_ptr.write("                &nbsp &nbsp \n")
        html_ptr.write("                <img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s" %(encodedStatusRejectedIcon.decode('utf-8'), numRejected))
        html_ptr.write("                &nbsp &nbsp \n")
        html_ptr.write("                <img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s" %(encodedStatusDraftIcon.decode('utf-8'), numDraft))
        html_ptr.write("            </td> \n")
        
        html_ptr.write("        </tr> \n")

    html_ptr.write("    </tbody>\n")


    html_ptr.write("</table>\n")  


#----------------------------------------------------------------------------------------#
def display_product_summary_table(html_ptr, productData, encodedStatusApprovedIcon, encodedStatusRejectedIcon, encodedStatusDraftIcon):


    numApproved = productData["numApproved"]
    numRejected = productData["numRejected"] 
    numDraft = productData["numDraft"] 

    P1Licenses = productData["P1Licenses"]
    P2Licenses = productData["P2Licenses"] 
    P3Licenses = productData["P3Licenses"] 
    NALicenses = productData["NALicenses"]
    numTotalVulnerabilities = productData["numTotalVulnerabilities"]
    numCriticalVulnerabilities = productData["numCriticalVulnerabilities"]
    numHighVulnerabilities = productData["numHighVulnerabilities"]
    numMediumVulnerabilities = productData["numMediumVulnerabilities"]
    numLowVulnerabilities = productData["numLowVulnerabilities"]
    numNoneVulnerabilities = productData["numNoneVulnerabilities"]
   
    html_ptr.write("<table id='productSummaryData' class='table table-hover table-sm row-border' style='width:90%'>\n")

    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th colspan='8' class='text-center'><h4>Product Summary</h4></th>\n") 
    html_ptr.write("        </tr>\n") 
    html_ptr.write("        <tr>\n") 
    html_ptr.write("            <th style='width: 10%' class='text-center'>LICENSE PRIORITIES</th>\n") 
    html_ptr.write("            <th style='width: 15%' class='text-center'>VULNERABILITIES</th>\n")
    html_ptr.write("            <th style='width: 15%' class='text-center'>REVIEW SUMMARY</th>\n")
    html_ptr.write("        </tr>\n")
    html_ptr.write("    </thead>\n")  
    html_ptr.write("    <tbody>\n")
               
    
    html_ptr.write("        <tr> \n")
    html_ptr.write("            <td class='text-center text-nowrap' data-sort='%s' >\n" %P1Licenses)
    html_ptr.write("                <span class='btn btn-vuln btn-high'>%s</span>\n" %(P1Licenses))
    html_ptr.write("                <span class='btn btn-vuln btn-medium'>%s</span>\n" %(P2Licenses))
    html_ptr.write("                <span class='btn btn-vuln btn-low'>%s</span>\n" %(P3Licenses))
    html_ptr.write("                <span class='btn btn-vuln btn-none'>%s</span>\n" %(NALicenses))
    html_ptr.write("            </td>\n")


    html_ptr.write("            <td class='text-center text-nowrap' data-sort='%s' >\n" %numCriticalVulnerabilities)
    # Write in single line to remove spaces between btn spans
    if numTotalVulnerabilities > 0:
        html_ptr.write("                <span class='btn btn-vuln btn-critical'>%s</span>\n" %(numCriticalVulnerabilities))
        html_ptr.write("                <span class='btn btn-vuln btn-high'>%s</span>\n" %(numHighVulnerabilities))
        html_ptr.write("                <span class='btn btn-vuln btn-medium'>%s</span>\n" %(numMediumVulnerabilities))
        html_ptr.write("                <span class='btn btn-vuln btn-low'>%s</span>\n" %(numLowVulnerabilities))
        html_ptr.write("                <span class='btn btn-vuln btn-none'>%s</span>\n" %(numNoneVulnerabilities))
    else:
        html_ptr.write("                <span class='btn btn-vuln btn-no-vulns'>None</span>\n")
    html_ptr.write("            </td> \n")

   
    html_ptr.write("            <td class='text-center text-nowrap' style='color:gray;'>")
    html_ptr.write("<img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px; padding-left: -10px;'> %s" %(encodedStatusApprovedIcon.decode('utf-8'), numApproved))
    html_ptr.write("            &nbsp &nbsp \n")
    html_ptr.write("<img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px; padding-left: -10px'> %s" %(encodedStatusRejectedIcon.decode('utf-8'), numRejected))
    html_ptr.write("            &nbsp &nbsp \n")
    html_ptr.write("<img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px; padding-left: -10px'> %s" %(encodedStatusDraftIcon.decode('utf-8'), numDraft))
    html_ptr.write("            </td> \n")
    html_ptr.write("        </tr> \n")

    html_ptr.write("    </tbody>\n")


    html_ptr.write("</table>\n")  