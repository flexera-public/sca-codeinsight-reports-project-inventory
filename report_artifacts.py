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
import re
import xlsxwriter


logger = logging.getLogger(__name__)

#--------------------------------------------------------------------------------#
def create_report_artifacts(reportData):
    logger.info("Entering create_report_artifacts")

    # Dict to hold the complete list of reports
    reports = {}

    htmlFile = generate_html_report(reportData)
    xlsxFile = generate_xlsx_report(reportData)

    reports["viewable"] = htmlFile
    reports["allFormats"] = [htmlFile, xlsxFile]

    logger.info("Exiting create_report_artifacts")
    
    return reports 

#------------------------------------------------------------------#
def generate_xlsx_report(reportData):
    logger.info("    Entering generate_xlsx_report")

    reportName = reportData["reportName"]
    projectName = reportData["projectName"] 
    projectID = reportData["projectID"] 
    fileNameTimeStamp = reportData["fileNameTimeStamp"] 
    inventoryData = reportData["inventoryData"]
    projectList = reportData["projectList"]
    projectSummaryData = reportData["projectSummaryData"]
    applicationSummaryData = reportData["applicationSummaryData"]
    projectHierarchy = reportData["projectHierarchy"]
    
    cvssVersion = projectSummaryData["cvssVersion"]  # 2.0/3.x
    includeComplianceInformation = projectSummaryData["includeComplianceInformation"]  # True/False

    # Colors for report
    reveneraGray = '#323E48'
    white = '#FFFFFF'
    p1LicenseColor = "#C00000"
    p2LicenseColor = "#FFFF00"
    p3LicenseColor= "#008000"
    NALicenseColor = "#D3D3D3"
    criticalVulnColor = "#400000"
    highVulnColor = "#C00000"
    mediumVulnColor = "#FFA500"
    lowVulnColor = "#FFFF00"
    noneVulnColor = "#D3D3D3"
    approvedColor = "#008000"
    rejectedColor = "#C00000"
    draftColor = "#D3D3D3"

    projectNameForFile = re.sub(r"[^a-zA-Z0-9]+", '-', projectName )

    if len(projectList)==1:
        xlsxFile = projectNameForFile + "-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".xlsx"
    else:
        xlsxFile = projectNameForFile + "-with-children-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".xlsx" 

    logger.debug("xlsxFile: %s" %xlsxFile)

    # Create the workbook/worksheet for storying the data
    workbook = xlsxwriter.Workbook(xlsxFile)

    # If there is more than one project in hierarchy create sep tabs 
    # for summary data and include project hierarchy
    if len(projectList) > 1:
        licenseSummaryWorksheet = workbook.add_worksheet('License Summary')
        licenseSummaryWorksheet.hide_gridlines(2)
        vulnerabilitySummaryWorksheet = workbook.add_worksheet('Vulnerability Summary')
        vulnerabilitySummaryWorksheet.hide_gridlines(2)
        reviewSummaryWorksheet = workbook.add_worksheet('Review Summary')
        reviewSummaryWorksheet.hide_gridlines(2)
    else:
        projectSummaryWorksheet = workbook.add_worksheet('Project Summary')
        projectSummaryWorksheet.hide_gridlines(2)

    detailsWorksheet = workbook.add_worksheet('Inventory Details') 
    dataWorksheet = workbook.add_worksheet('Chart Data')

    tableHeaderFormat = workbook.add_format()
    tableHeaderFormat.set_text_wrap()
    tableHeaderFormat.set_bold()
    tableHeaderFormat.set_bg_color(reveneraGray)
    tableHeaderFormat.set_font_color(white)
    tableHeaderFormat.set_font_size('12')
    tableHeaderFormat.set_align('center')
    tableHeaderFormat.set_align('vcenter')

    cellFormat = workbook.add_format()
    cellFormat.set_text_wrap()
    cellFormat.set_align('center')
    cellFormat.set_align('vcenter')
    cellFormat.set_font_size('10')
    cellFormat.set_border()

    cellLinkFormat = workbook.add_format()
    cellLinkFormat.set_text_wrap()
    cellLinkFormat.set_font_size('10')
    cellLinkFormat.set_align('center')
    cellLinkFormat.set_align('vcenter')
    cellLinkFormat.set_font_color('blue')
    cellLinkFormat.set_underline()
    cellLinkFormat.set_border()

    boldCellFormat = workbook.add_format()
    boldCellFormat.set_align('vcenter')
    boldCellFormat.set_font_size('12')
    boldCellFormat.set_bold()

    criticalVulnerabilityCellFormat = workbook.add_format()
    criticalVulnerabilityCellFormat.set_text_wrap()
    criticalVulnerabilityCellFormat.set_font_size('12')
    criticalVulnerabilityCellFormat.set_align('center')
    criticalVulnerabilityCellFormat.set_align('vcenter')
    criticalVulnerabilityCellFormat.set_bg_color(criticalVulnColor)
    criticalVulnerabilityCellFormat.set_font_color('white')
    criticalVulnerabilityCellFormat.set_border()

    highVulnerabilityCellFormat = workbook.add_format()
    highVulnerabilityCellFormat.set_text_wrap()
    highVulnerabilityCellFormat.set_font_size('12')
    highVulnerabilityCellFormat.set_align('center')
    highVulnerabilityCellFormat.set_align('vcenter')
    highVulnerabilityCellFormat.set_bg_color(highVulnColor)
    highVulnerabilityCellFormat.set_font_color('white')
    highVulnerabilityCellFormat.set_border()

    mediumVulnerabilityCellFormat = workbook.add_format()
    mediumVulnerabilityCellFormat.set_text_wrap()
    mediumVulnerabilityCellFormat.set_font_size('12')
    mediumVulnerabilityCellFormat.set_align('center')
    mediumVulnerabilityCellFormat.set_align('vcenter')
    mediumVulnerabilityCellFormat.set_bg_color(mediumVulnColor)
    mediumVulnerabilityCellFormat.set_border()

    lowVulnerabilityCellFormat = workbook.add_format()
    lowVulnerabilityCellFormat.set_text_wrap()
    lowVulnerabilityCellFormat.set_font_size('12')
    lowVulnerabilityCellFormat.set_align('center')
    lowVulnerabilityCellFormat.set_align('vcenter')
    lowVulnerabilityCellFormat.set_bg_color(lowVulnColor)
    lowVulnerabilityCellFormat.set_border()

    unknownVulnerabilityCellFormat = workbook.add_format()
    unknownVulnerabilityCellFormat.set_text_wrap()
    unknownVulnerabilityCellFormat.set_font_size('12')
    unknownVulnerabilityCellFormat.set_align('center')
    unknownVulnerabilityCellFormat.set_align('vcenter')
    unknownVulnerabilityCellFormat.set_bg_color(noneVulnColor)
    unknownVulnerabilityCellFormat.set_border()

    approvedCellFormat = workbook.add_format()
    approvedCellFormat.set_text_wrap()
    approvedCellFormat.set_font_size('10')
    approvedCellFormat.set_align('center')
    approvedCellFormat.set_align('vcenter')
    approvedCellFormat.set_font_color(approvedColor)
    approvedCellFormat.set_border()

    rejectedCellFormat = workbook.add_format()
    rejectedCellFormat.set_text_wrap()
    rejectedCellFormat.set_font_size('10')
    rejectedCellFormat.set_align('center')
    rejectedCellFormat.set_align('vcenter')
    rejectedCellFormat.set_font_color(rejectedColor)
    rejectedCellFormat.set_border()

    draftCellFormat = workbook.add_format()
    draftCellFormat.set_text_wrap()
    draftCellFormat.set_font_size('10')
    draftCellFormat.set_align('center')
    draftCellFormat.set_align('vcenter')
    draftCellFormat.set_border()

    complianceCellFormat = workbook.add_format()
    complianceCellFormat.set_text_wrap()
    complianceCellFormat.set_font_color(rejectedColor)
    complianceCellFormat.set_align('vcenter')
    complianceCellFormat.set_font_size('10')
    complianceCellFormat.set_border()


    # Populate the summary data for the charts
    dataWorksheet.write('A3', "Application Summary")
    dataWorksheet.write_column('A4', projectSummaryData["projectNames"])

    dataWorksheet.merge_range('B1:E1', 'License Summary', tableHeaderFormat)
    
    dataWorksheet.write('B2', "P1 Licenses")
    dataWorksheet.write('B3', applicationSummaryData["numP1Licenses"])
    dataWorksheet.write_column('B4', projectSummaryData["numP1Licenses"])  

    dataWorksheet.write('C2', "P2 Licenses")
    dataWorksheet.write('C3', applicationSummaryData["numP2Licenses"])
    dataWorksheet.write_column('C4', projectSummaryData["numP2Licenses"])  

    dataWorksheet.write('D2', "P3 Licenses")
    dataWorksheet.write('D3', applicationSummaryData["numP3Licenses"])
    dataWorksheet.write_column('D4', projectSummaryData["numP3Licenses"]) 

    dataWorksheet.write('E2', "NA Licenses")
    dataWorksheet.write('E3', applicationSummaryData["numNALicenses"])
    dataWorksheet.write_column('E4', projectSummaryData["numNALicenses"]) 

    dataWorksheet.merge_range('F1:J1', 'Vulnerabilities', tableHeaderFormat)

    if cvssVersion == "3.x": 
        dataWorksheet.write('F2', "Critical")
        dataWorksheet.write('F3', applicationSummaryData["numCriticalVulnerabilities"])
        dataWorksheet.write_column('F4', projectSummaryData["numCriticalVulnerabilities"])  

    dataWorksheet.write('G2', "High")
    dataWorksheet.write('G3', applicationSummaryData["numHighVulnerabilities"])
    dataWorksheet.write_column('G4', projectSummaryData["numHighVulnerabilities"])  

    dataWorksheet.write('H2', "Medium")
    dataWorksheet.write('H3', applicationSummaryData["numMediumVulnerabilities"])
    dataWorksheet.write_column('H4', projectSummaryData["numMediumVulnerabilities"])  

    dataWorksheet.write('I2', "Low")
    dataWorksheet.write('I3', applicationSummaryData["numLowVulnerabilities"])
    dataWorksheet.write_column('I4', projectSummaryData["numLowVulnerabilities"])  

    dataWorksheet.write('J2', "None")
    dataWorksheet.write('J3', applicationSummaryData["numNoneVulnerabilities"])
    dataWorksheet.write_column('J4', projectSummaryData["numNoneVulnerabilities"])  

    dataWorksheet.merge_range('K1:M1', 'Review Status', tableHeaderFormat)

    dataWorksheet.write('K2', "Approved")
    dataWorksheet.write('K3', applicationSummaryData["numApproved"])
    dataWorksheet.write_column('K4', projectSummaryData["numApproved"])  

    dataWorksheet.write('L2', "Rejected")
    dataWorksheet.write('L3', applicationSummaryData["numRejected"])
    dataWorksheet.write_column('L4', projectSummaryData["numRejected"])  

    dataWorksheet.write('M2', "Draft")
    dataWorksheet.write('M3', applicationSummaryData["numDraft"])
    dataWorksheet.write_column('M4', projectSummaryData["numDraft"])  

    catagoryHeaderRow = 1
    defaultChartWidth = 700
    summaryChartHeight = 150

    ###############################################################################################
    # Do we need application level summary charts?
    if len(projectList) > 1:

        # Add project hierarchy view for each summary tab
        for summaryWorksheet in [licenseSummaryWorksheet, vulnerabilitySummaryWorksheet, reviewSummaryWorksheet]:

            summaryWorksheet.merge_range('B2:M2', "Project Hierarchy", tableHeaderFormat)
            summaryWorksheet.set_column('A:Z', 2)
            summaryWorksheet.hide_gridlines(2)
            
            summaryWorksheet.write('C4', projectName, boldCellFormat) # Row 3, column 2
            display_project_hierarchy(summaryWorksheet, projectHierarchy, 3, 2, boldCellFormat)


        # Create the charts now
        applicationSummaryRow = 2  
        
        applicationLicenseSummaryChart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})
        applicationLicenseSummaryChart.set_title({'name': 'Application License Summary'})

        applicationLicenseSummaryChart.set_size({'width': defaultChartWidth, 'height': summaryChartHeight})
        applicationLicenseSummaryChart.set_legend({'position': 'bottom'})
        applicationLicenseSummaryChart.set_y_axis({'reverse': True})

        licenseBarColors = [p1LicenseColor, p2LicenseColor, p3LicenseColor, NALicenseColor]
        licenseDataStartColumn = 1 # B Column is where the data starts

        for columnIndex in range(0, 4):
            applicationLicenseSummaryChart.add_series({ 
                'name':       ['Chart Data', catagoryHeaderRow, columnIndex+licenseDataStartColumn], 
                'categories': ['Chart Data', applicationSummaryRow, columnIndex, applicationSummaryRow, columnIndex], 
                'values':     ['Chart Data', applicationSummaryRow, columnIndex+licenseDataStartColumn, applicationSummaryRow, columnIndex+licenseDataStartColumn],
                'fill':       {'color': licenseBarColors[columnIndex]}            }) 

        ############################################################################################################
        #  Vulnerability Summary Chart
        applicationVulnerabilitySummaryChart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

        applicationVulnerabilitySummaryChart.set_title({'name': 'Application Vulnerabilty Summary'})

        applicationVulnerabilitySummaryChart.set_size({'width': defaultChartWidth, 'height': summaryChartHeight})
        applicationVulnerabilitySummaryChart.set_legend({'position': 'bottom'})
        applicationVulnerabilitySummaryChart.set_y_axis({'reverse': True})

        if cvssVersion == "3.x": 
            vulnerabilityBarColors = [criticalVulnColor, highVulnColor, mediumVulnColor, lowVulnColor, noneVulnColor]
            vulnerabiltyDataStartColumn = 5 # Start data in Column F
        else:
            vulnerabilityBarColors = [highVulnColor, mediumVulnColor, lowVulnColor, noneVulnColor]
            vulnerabiltyDataStartColumn = 6 # Start data in Column G
        
        for columnIndex in range(0, len(vulnerabilityBarColors)):

            applicationVulnerabilitySummaryChart.add_series({ 
                'name':       ['Chart Data', catagoryHeaderRow, columnIndex+vulnerabiltyDataStartColumn], 
                'categories': ['Chart Data', applicationSummaryRow, columnIndex, applicationSummaryRow, columnIndex], 
                'values':     ['Chart Data', applicationSummaryRow, columnIndex+vulnerabiltyDataStartColumn, applicationSummaryRow, columnIndex+vulnerabiltyDataStartColumn],
                'fill':       {'color': vulnerabilityBarColors[columnIndex]}            }) 

        ############################################################################################################
        #  Review Status Summary Chart
        applicationReviewStatusSummaryChart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

        applicationReviewStatusSummaryChart.set_title({'name': 'Application Review Status Summary'})

        applicationReviewStatusSummaryChart.set_size({'width': defaultChartWidth, 'height': summaryChartHeight})
        applicationReviewStatusSummaryChart.set_legend({'position': 'bottom'})
        applicationReviewStatusSummaryChart.set_y_axis({'reverse': True})

        reviewStatusBarColors = [approvedColor, rejectedColor, draftColor]
        reviewStatusDataStartColumn = 10 # Start data in Column K

        for columnIndex in range(0, len(reviewStatusBarColors)):

            applicationReviewStatusSummaryChart.add_series({ 
                'name':       ['Chart Data', catagoryHeaderRow, columnIndex+reviewStatusDataStartColumn], 
                'categories': ['Chart Data', applicationSummaryRow, columnIndex, applicationSummaryRow, columnIndex], 
                'values':     ['Chart Data', applicationSummaryRow, columnIndex+reviewStatusDataStartColumn, applicationSummaryRow, columnIndex+reviewStatusDataStartColumn],
                'fill':       {'color': reviewStatusBarColors[columnIndex]}            }) 

        licenseSummaryWorksheet.insert_chart('AA2', applicationLicenseSummaryChart)
        vulnerabilitySummaryWorksheet.insert_chart('AA2', applicationVulnerabilitySummaryChart)
        reviewSummaryWorksheet.insert_chart('AA2', applicationReviewStatusSummaryChart)

    # Now print the project level data
    projectDataStartRow = 3 
    
    projectLicenseSummaryChart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

    if len(projectList) == 1:
        projectLicenseSummaryChart.set_title({'name': 'Project Level License Summary'})
    else:
        projectLicenseSummaryChart.set_title({'name': 'Project Level License Summaries'})

    projectLicenseSummaryChart.set_size({'width': defaultChartWidth, 'height': summaryChartHeight + (len(projectList)* 30)})
    projectLicenseSummaryChart.set_legend({'position': 'bottom'})
    projectLicenseSummaryChart.set_y_axis({'reverse': True})

    licenseBarColors = [p1LicenseColor, p2LicenseColor, p3LicenseColor, NALicenseColor]
    licenseDataStartColumn = 1 # B Column is where the data starts

    for columnIndex in range(0, 4):
        projectLicenseSummaryChart.add_series({ 
            'name':       ['Chart Data', catagoryHeaderRow, columnIndex+licenseDataStartColumn], 
            'categories': ['Chart Data', projectDataStartRow, columnIndex, projectDataStartRow+len(projectList), columnIndex], 
            'values':     ['Chart Data', projectDataStartRow, columnIndex+licenseDataStartColumn, projectDataStartRow+len(projectList), columnIndex+licenseDataStartColumn],
            'fill':       {'color': licenseBarColors[columnIndex]}        }) 


    ############################################################################################################
    #  Vulnerability Summary Chart
    projectVulnerabilitySummaryChart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

    if len(projectList) == 1:
        projectVulnerabilitySummaryChart.set_title({'name': 'Project Level Vulnerabilty Summary'})
    else:
        projectVulnerabilitySummaryChart.set_title({'name': 'Project Level Vulnerabilty Summaries'})

    projectVulnerabilitySummaryChart.set_size({'width': defaultChartWidth, 'height': summaryChartHeight + (len(projectList)* 30)})
    projectVulnerabilitySummaryChart.set_legend({'position': 'bottom'})
    projectVulnerabilitySummaryChart.set_y_axis({'reverse': True})

    if cvssVersion == "3.x": 
        vulnerabilityBarColors = [criticalVulnColor, highVulnColor, mediumVulnColor, lowVulnColor, noneVulnColor]
        vulnerabiltyDataStartColumn = 5 # Start data in Column F
    else:
        vulnerabilityBarColors = [highVulnColor, mediumVulnColor, lowVulnColor, noneVulnColor]
        vulnerabiltyDataStartColumn = 6 # Start data in Column G
    
    for columnIndex in range(0, len(vulnerabilityBarColors)):

        projectVulnerabilitySummaryChart.add_series({ 
            'name':       ['Chart Data', catagoryHeaderRow, columnIndex+vulnerabiltyDataStartColumn], 
            'categories': ['Chart Data', projectDataStartRow, columnIndex, projectDataStartRow+len(projectList), columnIndex], 
            'values':     ['Chart Data', projectDataStartRow, columnIndex+vulnerabiltyDataStartColumn, projectDataStartRow+len(projectList), columnIndex+vulnerabiltyDataStartColumn],
            'fill':       {'color': vulnerabilityBarColors[columnIndex]}        }) 

    ############################################################################################################
    #  Review Status Summary Chart
    projectReviewStatusSummaryChart = workbook.add_chart({'type': 'bar', 'subtype': 'stacked'})

    if len(projectList) == 1:
        projectReviewStatusSummaryChart.set_title({'name': 'Project Level Review Status Summary'})
    else:
        projectReviewStatusSummaryChart.set_title({'name': 'Project Level Review Status Summaries'})

    projectReviewStatusSummaryChart.set_size({'width': defaultChartWidth, 'height': summaryChartHeight + (len(projectList)* 30)})
    projectReviewStatusSummaryChart.set_legend({'position': 'bottom'})
    projectReviewStatusSummaryChart.set_y_axis({'reverse': True})

    reviewStatusBarColors = [approvedColor, rejectedColor, draftColor]
    reviewStatusDataStartColumn = 10 # Start data in Column K
    
    for columnIndex in range(0, len(reviewStatusBarColors)):

        projectReviewStatusSummaryChart.add_series({ 
            'name':       ['Chart Data', catagoryHeaderRow, columnIndex+reviewStatusDataStartColumn], 
            'categories': ['Chart Data', projectDataStartRow, columnIndex, projectDataStartRow+len(projectList), columnIndex], 
            'values':     ['Chart Data', projectDataStartRow, columnIndex+reviewStatusDataStartColumn, projectDataStartRow+len(projectList), columnIndex+reviewStatusDataStartColumn],
            'fill':       {'color': reviewStatusBarColors[columnIndex]}        }) 

    if len(projectList) == 1:
        projectSummaryWorksheet.insert_chart('A2', projectLicenseSummaryChart)
        projectSummaryWorksheet.insert_chart('A11', projectVulnerabilitySummaryChart)
        projectSummaryWorksheet.insert_chart('A20', projectReviewStatusSummaryChart)
    else:
        licenseSummaryWorksheet.insert_chart('AA9', projectLicenseSummaryChart)
        vulnerabilitySummaryWorksheet.insert_chart('AA9', projectVulnerabilitySummaryChart)
        reviewSummaryWorksheet.insert_chart('AA9', projectReviewStatusSummaryChart) 
        
            

    # Fill out the inventory details worksheet
    column=0
    row=0

    # Set the default column widths
    tableHeaders = []
    
    if len(projectList) > 1:
        detailsWorksheet.set_column(column, column, 25)  # Project Name
        tableHeaders.append("PROJECT NAME")
        column+=1     

    detailsWorksheet.set_column(column, column, 25)  # Inventory Item
    tableHeaders.append("INVENTORY ITEM")
    column+=1

    detailsWorksheet.set_column(column, column, 15)  # Priority
    tableHeaders.append("PRIORITY")
    column+=1

    detailsWorksheet.set_column(column, column, 25)  # Component
    tableHeaders.append("COMPONENT")
    column+=1

    detailsWorksheet.set_column(column, column, 15)  # Version
    tableHeaders.append("VERSION")
    column+=1

    detailsWorksheet.set_column(column, column, 15)  # License (SPDX ID)
    tableHeaders.append("LICENSE")
    column+=1
   
    if cvssVersion == "3.x": 
        detailsWorksheet.set_column(column, column, 15)  # Critical
        tableHeaders.append("CRITICAL")
        column+=1
    
    detailsWorksheet.set_column(column, column, 10)  # High
    tableHeaders.append("HIGH")
    column+=1
    
    detailsWorksheet.set_column(column, column, 15)  # Medium
    tableHeaders.append("MEDIUM")
    column+=1
    
    detailsWorksheet.set_column(column, column, 10)  # Low
    tableHeaders.append("LOW")
    column+=1
    
    detailsWorksheet.set_column(column, column, 15)  # Unnknown
    tableHeaders.append("UNKNOWN")
    column+=1
    
    detailsWorksheet.set_column(column, column, 15)  # Review Status
    tableHeaders.append("REVIEW STATUS")
    column+=1

    if includeComplianceInformation:
        detailsWorksheet.set_column(column, column, 80)  # Compliance Information
        tableHeaders.append("COMPLIANCE INFORMATION")
        column+=1

    detailsWorksheet.write_row(row, 0, tableHeaders, tableHeaderFormat)
    row+=1

    ######################################################
    # Cycle through the inventory to create the 
    # table with the results
    for inventoryID in sorted(inventoryData):
        logger.debug("Reporting for inventory item %s" %inventoryID)

        projectName = inventoryData[inventoryID]["projectName"]
        inventoryItemName = inventoryData[inventoryID]["inventoryItemName"]
        componentName = inventoryData[inventoryID]["componentName"]
        componentVersionName = inventoryData[inventoryID]["componentVersionName"]
        inventoryPriority = inventoryData[inventoryID]["inventoryPriority"]
        selectedLicenseName = inventoryData[inventoryID]["selectedLicenseName"]
        vulnerabilityData = inventoryData[inventoryID]["vulnerabilityData"]
        componentUrl = inventoryData[inventoryID]["componentUrl"]
        selectedLicenseUrl = inventoryData[inventoryID]["selectedLicenseUrl"]
        inventoryReviewStatus = inventoryData[inventoryID]["inventoryReviewStatus"]
        inventoryLink = inventoryData[inventoryID]["inventoryLink"]
        projectLink = inventoryData[inventoryID]["projectLink"]
        complianceIssues = inventoryData[inventoryID]["complianceIssues"]

       
        # Now write each cell
        column=0
        if len(projectList) > 1:
            detailsWorksheet.write_url(row, column, projectLink, cellLinkFormat, string=projectName)
            column+=1

        detailsWorksheet.write_url(row, column, inventoryLink, cellLinkFormat, string=inventoryItemName)
        column+=1
        detailsWorksheet.write(row, column, inventoryPriority, cellFormat)
        column+=1
        detailsWorksheet.write(row, column, componentName, cellFormat)
        column+=1

        # Highlight the version if it is old
        if "Old version" in complianceIssues.keys():
            detailsWorksheet.write(row, column, componentVersionName, rejectedCellFormat)
            cellComment = "Old Version - " + complianceIssues["Old version"]
            detailsWorksheet.write_comment(row, column, cellComment, {'width' : 400, 'height' : 30})

        else:
            detailsWorksheet.write(row, column, componentVersionName, cellFormat)
        column+=1

        detailsWorksheet.write(row, column, selectedLicenseName, cellFormat)
        column+=1

        if cvssVersion == "3.x": 
            detailsWorksheet.write(row, column, vulnerabilityData["numCriticalVulnerabilities"], criticalVulnerabilityCellFormat)
            column+=1
        detailsWorksheet.write(row, column, vulnerabilityData["numHighVulnerabilities"], highVulnerabilityCellFormat)
        column+=1
        detailsWorksheet.write(row, column, vulnerabilityData["numMediumVulnerabilities"], mediumVulnerabilityCellFormat)
        column+=1
        detailsWorksheet.write(row, column, vulnerabilityData["numLowVulnerabilities"], lowVulnerabilityCellFormat)
        column+=1
        detailsWorksheet.write(row, column, vulnerabilityData["numNoneVulnerabilities"], unknownVulnerabilityCellFormat)
        column+=1

        # Check review status and set font color accordingly
        if inventoryReviewStatus == "Approved":
            detailsWorksheet.write(row, column, inventoryReviewStatus, approvedCellFormat)
        elif inventoryReviewStatus == "Rejected":
            detailsWorksheet.write(row, column, inventoryReviewStatus, rejectedCellFormat)
        else:
            detailsWorksheet.write(row, column, inventoryReviewStatus, draftCellFormat)
        column+=1

        if includeComplianceInformation:
            if len(complianceIssues):
                complianceString = ""
                for issue in complianceIssues:
                    complianceString += issue + "  -  " + complianceIssues[issue] +  "\n"
                complianceString=complianceString[:-2]  # Remove the last newline
                detailsWorksheet.write(row, column, complianceString, complianceCellFormat)
            else:
                detailsWorksheet.write(row, column, "None", cellFormat)

            column+=1
        row+=1

    # Automatically create the filter sort options
    detailsWorksheet.autofilter(0,0, 0 + len(inventoryData)-1, len(tableHeaders)-1)

    workbook.close()

    return xlsxFile

#------------------------------------------------------------#
def display_project_hierarchy(worksheet, parentProject, row, column, boldCellFormat):

    column +=1 #  We are level down so we need to indent
    row +=1
    # Are there more child projects for this project?

    if len(parentProject["childProject"]):
        for childProject in parentProject["childProject"]:
            projectID = childProject["id"]
            projectName = childProject["name"]
            # Add this ID to the list of projects with other child projects
            # and get then do it again
            worksheet.write( row, column, projectName, boldCellFormat)

            row =  display_project_hierarchy(worksheet, childProject, row, column, boldCellFormat)
    return row


#------------------------------------------------------------------#
def generate_html_report(reportData):
    logger.info("    Entering generate_html_report")

    reportName = reportData["reportName"]
    projectName = reportData["projectName"] 
    projectID = reportData["projectID"] 
    fileNameTimeStamp = reportData["fileNameTimeStamp"] 
    inventoryData = reportData["inventoryData"]
    projectList = reportData["projectList"]
    projectSummaryData = reportData["projectSummaryData"]
    applicationSummaryData = reportData["applicationSummaryData"]
    projectInventoryCount = reportData["projectInventoryCount"]

    cvssVersion = projectSummaryData["cvssVersion"]  # 2.0/3.x
    includeComplianceInformation = projectSummaryData["includeComplianceInformation"]  # True/False
   
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
    
    projectNameForFile = re.sub(r"[^a-zA-Z0-9]+", '-', projectName )

    if len(projectList)==1:
        htmlFile = projectNameForFile + "-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".html"
    else:
        htmlFile = projectNameForFile + "-with-children-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".html" 

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
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.2.1/themes/default/style.min.css">
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

    #######################################################################
    #  Create table to hold the application summary charts.
    #  js script itself is added later
    html_ptr.write("<table id='applicationSummary' class='table' style='width:90%'>\n")
    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    if len(projectList) > 1:
        html_ptr.write("            <th colspan='8' class='text-center'><h4>Application Summary</h4></th>\n") 
    else:
        html_ptr.write("            <th colspan='8' class='text-center'><h4>%s Summary</h4></th>\n" %projectName) 
    html_ptr.write("        </tr>\n") 
    html_ptr.write("    </thead>\n")
    html_ptr.write("</table>\n")
    
    html_ptr.write("<div class='container'>\n")
    html_ptr.write("    <div class='row'>\n")
    html_ptr.write("        <div class='col-sm'>\n")
    html_ptr.write("            <canvas id='applicationLicenses'></canvas>\n")
    html_ptr.write("        </div>\n")
    html_ptr.write("        <div class='col-sm'>\n")
    html_ptr.write("            <canvas id='applicationVulnerabilities'></canvas>\n")
    html_ptr.write("         </div>\n")
    html_ptr.write("        <div class='col-sm'>\n")
    html_ptr.write("            <canvas id='applicationReviewStatus'></canvas>\n")
    html_ptr.write("        </div>\n")
    html_ptr.write("    </div>\n")
    html_ptr.write("</div>\n")
 
    # If there is some sort of hierarchy then show specific project summaries
    if len(projectList) > 1:
        
        # How much space to we need to give each canvas
        # based on the amount of projects in the hierarchy
        canvasHeight = len(projectList) * 20   

        # We need a minimum size to cover font as well
        if canvasHeight < 180:
            canvasHeight = 180
        # The entire column needs to hold the three canvas items
        columnHeight = canvasHeight *3

        html_ptr.write("<hr class='small'>\n")

        #######################################################################
        #  Create table to hold the project summary charts.
        #  js script itself is added later

        html_ptr.write("<table id='projectSummary' class='table' style='width:90%'>\n")
        html_ptr.write("    <thead>\n")
        html_ptr.write("        <tr>\n")
        html_ptr.write("            <th colspan='8' class='text-center'><h4>Project Summaries</h4></th>\n") 
        html_ptr.write("        </tr>\n") 
        html_ptr.write("    </thead>\n")
        html_ptr.write("</table>\n")

        html_ptr.write("<div class='container'>\n")
        html_ptr.write("    <div class='row'>\n")

        html_ptr.write("        <div class='col-sm'>\n")
        html_ptr.write("<h6 class='gray' style='padding-top: 10px;'><center>Project Hierarchy</center></h6>") 
        html_ptr.write("            <div id='project_hierarchy'></div>\n")
        
        html_ptr.write("        </div>\n")
        html_ptr.write("        <div class='col-sm' style='height: %spx;'>\n" %(columnHeight) )
        html_ptr.write("            <div class='col-sm' style='height: %spx'>\n"%(canvasHeight))
        html_ptr.write("                <canvas id='projectLicenses'></canvas>\n")
        html_ptr.write("            </div>\n")
        html_ptr.write("            <div class='col-sm' style='height: %spx'>\n"%(canvasHeight))
        html_ptr.write("               <canvas id='projectVulnerabilities'></canvas>\n")
        html_ptr.write("             </div>\n")
        html_ptr.write("            <div class='col-sm' style='height: %spx'>\n"%(canvasHeight))
        html_ptr.write("               <canvas id='projectReviewStatus'></canvas>\n")
        html_ptr.write("           </div>\n")
        html_ptr.write("        </div>\n")
        html_ptr.write("    </div>\n")
        html_ptr.write("</div>\n")

        html_ptr.write("<hr class='small'>")

 
    html_ptr.write("<table id='inventoryData' class='table table-hover table-sm row-border' style='width:90%'>\n")

    html_ptr.write("    <thead>\n")
    html_ptr.write("        <tr>\n")
    html_ptr.write("            <th colspan='9' class='text-center'><h4>Inventory Items</h4></th>\n") 
    html_ptr.write("        </tr>\n") 
    html_ptr.write("        <tr>\n")
    if len(projectList) > 1: 
        html_ptr.write("            <th style='width: 15%' class='text-center'>PROJECT</th>\n") 
    html_ptr.write("            <th style='width: 25%' class='text-center text-nowrap'>INVENTORY ITEM</th>\n") 
    html_ptr.write("            <th style='width: 10%' class='text-center'>PRIORITY</th>\n") 
    html_ptr.write("            <th style='width: 15%' class='text-center'>COMPONENT</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>VERSION</th>\n")
    html_ptr.write("            <th style='width: 5%' class='text-center'>LICENSE</th>\n") 
    html_ptr.write("            <th style='width: 18%' class='text-center'>VULNERABILITIES</th>\n")
    html_ptr.write("            <th style='width: 7%' class='text-center text-nowrap'>REVIEW STATUS</th>\n")

    if includeComplianceInformation:
        html_ptr.write("            <th style='width: 10%' class='text-center text-nowrap'>COMPLIANCE ISSUES</th>\n")

    html_ptr.write("        </tr>\n")
    html_ptr.write("    </thead>\n")  
    html_ptr.write("    <tbody>\n")  


    ######################################################
    # Cycle through the inventory to create the 
    # table with the results
    for inventoryID in sorted(inventoryData):
        projectName = inventoryData[inventoryID]["projectName"]
        inventoryItemName = inventoryData[inventoryID]["inventoryItemName"]
        componentName = inventoryData[inventoryID]["componentName"]
        componentVersionName = inventoryData[inventoryID]["componentVersionName"]
        inventoryPriority = inventoryData[inventoryID]["inventoryPriority"]
        selectedLicenseName = inventoryData[inventoryID]["selectedLicenseName"]
        vulnerabilityData = inventoryData[inventoryID]["vulnerabilityData"]
        componentUrl = inventoryData[inventoryID]["componentUrl"]
        selectedLicenseUrl = inventoryData[inventoryID]["selectedLicenseUrl"]
        inventoryReviewStatus = inventoryData[inventoryID]["inventoryReviewStatus"]
        inventoryLink = inventoryData[inventoryID]["inventoryLink"]
        projectLink = inventoryData[inventoryID]["projectLink"]
        complianceIssues = inventoryData[inventoryID]["complianceIssues"]

        logger.debug("Reporting for inventory item %s" %inventoryID)

        numTotalVulnerabilities = 0
        numCriticalVulnerabilities = 0
        numHighVulnerabilities = 0
        numMediumVulnerabilities = 0
        numLowVulnerabilities = 0
        numNoneVulnerabilities = 0

        try:
            numTotalVulnerabilities = vulnerabilityData["numTotalVulnerabilities"]
            if cvssVersion == "3.x":
                numCriticalVulnerabilities = vulnerabilityData["numCriticalVulnerabilities"]
            numHighVulnerabilities = vulnerabilityData["numHighVulnerabilities"]
            numMediumVulnerabilities = vulnerabilityData["numMediumVulnerabilities"]
            numLowVulnerabilities = vulnerabilityData["numLowVulnerabilities"]
            numNoneVulnerabilities = vulnerabilityData["numNoneVulnerabilities"]
        except:
            logger.debug("    No vulnerability data")

        html_ptr.write("        <tr> \n")
        if len(projectList) > 1:
            html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(projectLink, projectName))
        html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(inventoryLink, inventoryItemName))
 

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

        # Highlight the version if it is old
        if "Old version" in complianceIssues.keys():
            html_ptr.write("<td class='text-left' style='color:red;'><span title='%s'>%s</span></td>\n" %(complianceIssues["Old version"], componentVersionName))
        else:
            html_ptr.write("            <td class='text-left'>%s</td>\n" %(componentVersionName))

        html_ptr.write("            <td class='text-left'><a href='%s' target='_blank'>%s</a></td>\n" %(selectedLicenseUrl, selectedLicenseName))
       
        # Write in single line to remove spaces between btn spans
        if numTotalVulnerabilities > 0:
            if cvssVersion == "3.x":
                html_ptr.write("            <td class='text-center text-nowrap' data-sort='%s' >\n" %numCriticalVulnerabilities)
                html_ptr.write("                <span class='btn btn-vuln btn-critical'>%s</span>\n" %(numCriticalVulnerabilities))
            else:
                html_ptr.write("            <td class='text-center text-nowrap' data-sort='%s' >\n" %numHighVulnerabilities)

            html_ptr.write("                <span class='btn btn-vuln btn-high'>%s</span>\n" %(numHighVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-medium'>%s</span>\n" %(numMediumVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-low'>%s</span>\n" %(numLowVulnerabilities))
            html_ptr.write("                <span class='btn btn-vuln btn-none'>%s</span>\n" %(numNoneVulnerabilities))
        else:
            html_ptr.write("            <td class='text-center text-nowrap' data-sort='-1' >\n" )
            html_ptr.write("                <span class='btn btn-vuln btn-no-vulns'>None</span>\n")

        if inventoryReviewStatus == "Approved":
            html_ptr.write("            <td class='text-left text-nowrap' style='color:green;'><img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s</td>\n" %(encodedStatusApprovedIcon.decode('utf-8'), inventoryReviewStatus))
        elif inventoryReviewStatus == "Rejected":
            html_ptr.write("            <td class='text-left text-nowrap' style='color:red;'><img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s</td>\n" %(encodedStatusRejectedIcon.decode('utf-8'), inventoryReviewStatus))
        elif inventoryReviewStatus == "Draft":
            html_ptr.write("            <td class='text-left text-nowrap' style='color:gray;'><img src='data:image/png;base64, %s' width='15px' height='15px' style='margin-top: -2px;'> %s</td>\n" %(encodedStatusDraftIcon.decode('utf-8'), inventoryReviewStatus))
        else:
            html_ptr.write("            <td class='text-left text-nowrap'>%s</td>\n" %(inventoryReviewStatus))

        if includeComplianceInformation:
            if len(complianceIssues):
                html_ptr.write("            <td class='text-left text-nowrap'>")
                for issue in complianceIssues:
                    html_ptr.write("<span class='dot dot-red'></span><span title='%s'>%s</span><br/>\n" %(complianceIssues[issue], issue))
                html_ptr.write("</td>\n")
            else:
                html_ptr.write("            <td title='This item does not have any compliance issues.'><span class='dot dot-green'></span>None</td>\n")


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
    html_ptr.write("  <div style='float:left'>&copy; %s Flexera</div>\n" %fileNameTimeStamp[0:4])
    html_ptr.write("  <div style='float:right'>Generated on %s</div>\n" %now)
    html_ptr.write("</div>\n")
    html_ptr.write("<!-- END FOOTER -->\n")   

    html_ptr.write("</div>\n")

    #---------------------------------------------------------------------------------------------------
    # Add javascript 
    #---------------------------------------------------------------------------------------------------

    html_ptr.write('''

    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js" integrity="sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>  
    <script src="https://cdn.datatables.net/1.10.21/js/dataTables.bootstrap4.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jstree/3.3.10/jstree.min.js"></script>
 
    ''')

    html_ptr.write("<script>\n")
    
    # Logic for datatable for inventory details
    add_inventory_datatable(html_ptr)
    # Add the common chartjs config
    add_default_chart_options(html_ptr)
    # Add the js for the application summary stacked bar charts
    generate_application_summary_chart(html_ptr, applicationSummaryData)

    if len(projectList) > 1:
        # Add the js for the project summary stacked bar charts
        generate_project_hierarchy_tree(html_ptr, projectList, projectInventoryCount)
        # Add the js for the project summary stacked bar charts
        generate_project_summary_charts(html_ptr, projectSummaryData)
    
    html_ptr.write("</script>\n")

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
def add_inventory_datatable(html_ptr):
    # Add the js for inventory datatable
    html_ptr.write('''

            $(document).ready(function (){
                var table = $('#inventoryData').DataTable({
                    "order": [[ 2, "desc" ]],
                    "lengthMenu": [ [25, 50, 100, -1], [25, 50, 100, "All"] ],
                });
            });
        ''')    

#----------------------------------------------------------------------------------------#
def add_default_chart_options(html_ptr):
    # Add commont defaults for display charts
    html_ptr.write('''  
        var defaultBarChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
            padding: {
                bottom: 25  //set that fits the best
            }
        },
        tooltips: {
            enabled: true,
            yAlign: 'center'
        },
        title: {
            display: true,
            fontColor: "#323E48"
        },

        scales: {
            xAxes: [{
                ticks: {
                    beginAtZero:true,
                    fontSize:11,
                    fontColor: "#323E48",
                    precision:0

                },
                scaleLabel:{
                    display:false
                },
                gridLines: {
                }, 
                stacked: true
            }],
            yAxes: [{
                gridLines: {
                    display:false,
                    color: "#fff",
                    zeroLineColor: "#fff",
                    zeroLineWidth: 0,
                    fontColor: "#323E48"
                },
                ticks: {
                    fontSize:11,
                    fontColor: "#323E48"
                },

                stacked: true
            }]
        },
        legend:{
            display:false
        },
        
    };  ''')

#----------------------------------------------------------------------------------------#
def generate_application_summary_chart(html_ptr, applicationSummaryData):
    logger.info("Entering generate_application_summary_chart")

    cvssVersion = applicationSummaryData["cvssVersion"]

    html_ptr.write('''  
        var applicationLicenses = document.getElementById("applicationLicenses");
        var applicationLicensesChart = new Chart(applicationLicenses, {
            type: 'horizontalBar',
            data: {
                datasets: [{
                    // P1 items
                    label: 'Strong Copyleft',
                    data: [%s],
                    backgroundColor: "#C00000"
                },{
                    // P2 items
                    label: 'Weak Copyleft/Commercial',
                    data: [%s],
                    backgroundColor: "#FFFF00"
                },{
                    // P3 items
                    label: 'Permissive/Public Domain',
                    data: [%s],
                    backgroundColor: "#008000"
                },{
                    // Unknown Licenses
                    label: 'Unknown',
                    data: [%s],
                    backgroundColor: "#D3D3D3"
                }]
            },

            options: defaultBarChartOptions,
        });
        applicationLicensesChart.options.title.text = "License Summary"
        applicationLicensesChart.options.tooltips.titleFontSize = 0

        ''' %(applicationSummaryData["numP1Licenses"], applicationSummaryData["numP2Licenses"], applicationSummaryData["numP3Licenses"], applicationSummaryData["numNALicenses"])  )

   
    html_ptr.write(''' 
    
    var applicationVulnerabilities= document.getElementById("applicationVulnerabilities");
    var applicationVulnerabilityChart = new Chart(applicationVulnerabilities, {
        type: 'horizontalBar',
        data: {
            datasets: [''')

    if cvssVersion == "3.x":
        html_ptr.write(''' {       
                // Critical Vulnerabilities
                label: 'Critical',
                data: [%s],
                backgroundColor: "#400000"
                },''' %applicationSummaryData["numCriticalVulnerabilities"])

     
    html_ptr.write('''        
            {
                // High Vulnerabilities
                label: 'High',
                data: [%s],
                backgroundColor: "#C00000"
            },{
                // Medium Vulnerabilities
                label: 'Medium',
                data: [%s],
                backgroundColor: "#FFA500"
            },{
                // Low Vulnerabilities
                label: 'Low',
                data: [%s],
                backgroundColor: "#FFFF00"
            },{
                // N/A Vulnerabilities
                label: 'N/A',
                data: [%s],
                backgroundColor: "#D3D3D3"
            },
            ]
        },

        options: defaultBarChartOptions,
        
    });
    applicationVulnerabilityChart.options.title.text = "Vulnerability Summary"
    applicationVulnerabilityChart.options.tooltips.titleFontSize = 0
    
    ''' %(applicationSummaryData["numHighVulnerabilities"], applicationSummaryData["numMediumVulnerabilities"], applicationSummaryData["numLowVulnerabilities"], applicationSummaryData["numNoneVulnerabilities"]) )
    

    html_ptr.write('''  
    var applicationReviewStatus = document.getElementById("applicationReviewStatus");
    var applicationReviewStatusChart = new Chart(applicationReviewStatus, {
        type: 'horizontalBar',
        data: {
            datasets: [{
                label: 'Approved',
                data: [%s],
                backgroundColor: "#008000"
            },{
                label: 'Rejected',
                data: [%s],
                backgroundColor: "#C00000"
            },{
                label: 'Unreviewed',
                data: [%s],
                backgroundColor: "#d0d0d0"
            }]
        },

        options: defaultBarChartOptions,
        
    });

    applicationReviewStatusChart.options.title.text = "Review Status Summary"
    applicationReviewStatusChart.options.tooltips.titleFontSize = 0
    
    ''' %(applicationSummaryData["numApproved"], applicationSummaryData["numRejected"], applicationSummaryData["numDraft"]) )

#----------------------------------------------------------------------------------------#
def generate_project_hierarchy_tree(html_ptr, projectHierarchy, projectInventoryCount):
    logger.info("Entering generate_project_hierarchy_tree")

    html_ptr.write('''var hierarchy = [\n''')

    for project in projectHierarchy:

        inventoryCount = projectInventoryCount[project["projectName"]]

        html_ptr.write('''{
            'id': '%s', 
            'parent': '%s', 
            'text': '%s',
            'a_attr': {
                'href': '%s'
            }
        },\n'''  %(project["projectID"], project["parent"], project["projectName"] + " (" + str(inventoryCount) + " items)" , project["projectLink"]))

    html_ptr.write('''\n]''')

    html_ptr.write('''

        $('#project_hierarchy').jstree({ 'core' : {
            'data' : hierarchy
        } });

        $('#project_hierarchy').on('ready.jstree', function() {
            $("#project_hierarchy").jstree("open_all");               

        $("#project_hierarchy").on("click", ".jstree-anchor", function(evt)
        {
            var link = $(evt.target).attr("href");
            window.open(link, '_blank');
        });


        });

    ''' )


#----------------------------------------------------------------------------------------#
def generate_project_summary_charts(html_ptr, projectSummaryData):
    logger.info("Entering generate_project_summary_charts")

    cvssVersion = projectSummaryData["cvssVersion"]

    html_ptr.write('''  
        var projectLicenses = document.getElementById("projectLicenses");
        var projectLicensesChart = new Chart(projectLicenses, {
            type: 'horizontalBar',
            data: {
                labels: %s,
                
                datasets: [{
                    // P1 items
                    label: 'Strong Copyleft',
                    data: %s,
                    backgroundColor: "#C00000"
                },{
                    // P2 items
                    label: 'Weak Copyleft/Commercial',
                    data: %s,
                    backgroundColor: "#FFFF00"
                },{
                    // P3 items
                    label: 'Permissive/Public Domain',
                    data: %s,
                    backgroundColor: "#008000"
                },{
                    // Unknown Licenses
                    label: 'Unknown',
                    data: %s,
                    backgroundColor: "#D3D3D3"
                }]
            },

            options: defaultBarChartOptions,
        });
        projectLicensesChart.options.title.text = "License Summary"

        ''' %(projectSummaryData["projectNames"], projectSummaryData["numP1Licenses"], projectSummaryData["numP2Licenses"], projectSummaryData["numP3Licenses"],  projectSummaryData["numNALicenses"])  )

    html_ptr.write(''' 
    
    var projectVulnerabilities= document.getElementById("projectVulnerabilities");
    var projectVulnerabilityChart = new Chart(projectVulnerabilities, {
        type: 'horizontalBar',
        data: {
            labels: %s,
            datasets: [''' %projectSummaryData["projectNames"])

    if cvssVersion == "3.x":
        html_ptr.write('''{          
                // Critical Vulnerabilities
                label: 'Critical',
                data: %s,
                backgroundColor: "#400000"
            },''' %projectSummaryData["numCriticalVulnerabilities"])
    html_ptr.write('''{
                // High Vulnerabilities
                label: 'High',
                data: %s,
                backgroundColor: "#C00000"
            },{
                // Medium Vulnerabilities
                label: 'Medium',
                data: %s,
                backgroundColor: "#FFA500"
            },{
                // Low Vulnerabilities
                label: 'Low',
                data: %s,
                backgroundColor: "#FFFF00"
            },{
                // N/A Vulnerabilities
                label: 'N/A',
                data: %s,
                backgroundColor: "#D3D3D3"
            },
            ]
        },

        options: defaultBarChartOptions,
        
    });
    projectVulnerabilityChart.options.title.text = "Vulnerability Summary"
    
    
    ''' %( projectSummaryData["numHighVulnerabilities"], projectSummaryData["numMediumVulnerabilities"], projectSummaryData["numLowVulnerabilities"], projectSummaryData["numNoneVulnerabilities"]) )
    

    html_ptr.write('''  
    var projectReviewStatus = document.getElementById("projectReviewStatus");
    var projectReviewStatusChart = new Chart(projectReviewStatus, {
        type: 'horizontalBar',
        data: {
            labels: %s,
            datasets: [{
                label: 'Approved',
                data: %s,
                backgroundColor: "#008000"
            },{
                label: 'Rejected',
                data: %s,
                backgroundColor: "#C00000"
            },{
                label: 'Unreviewed',
                data: %s,
                backgroundColor: "#d0d0d0"
            }]
        },

        options: defaultBarChartOptions,
        
    });

    projectReviewStatusChart.options.title.text = "Review Status Summary"
    
    ''' %(projectSummaryData["projectNames"], projectSummaryData["numApproved"], projectSummaryData["numRejected"], projectSummaryData["numDraft"]) )





    