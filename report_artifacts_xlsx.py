'''
Copyright 2021 Flexera Software LLC
See LICENSE.TXT for full license text
SPDX-License-Identifier: MIT

Author : sgeary  
Created On : Thu Oct 28 2021
File : report_artifacts_xlsx.py
'''

import logging
from datetime import datetime
import xlsxwriter

import _version

logger = logging.getLogger(__name__)
#------------------------------------------------------------------#
def generate_xlsx_report(reportData):
    logger.info("    Entering generate_xlsx_report")

    reportName = reportData["reportName"]
    projectName = reportData["projectName"]
    projectNameForFile  = reportData["projectNameForFile"] 
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

    if len(projectList)==1:
        xlsxFile = projectNameForFile + "-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".xlsx"
    else:
        xlsxFile = projectNameForFile + "-with-children-" + str(projectID) + "-" + reportName.replace(" ", "_") + "-" + fileNameTimeStamp + ".xlsx" 

    logger.debug("        xlsxFile: %s" %xlsxFile)

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


    dataWorksheet.merge_range('B1:F1', "Report Generated: %s" %(datetime.now().strftime("%B %d, %Y at %H:%M:%S")))
    dataWorksheet.merge_range('B2:F2', "Report Version: %s" %_version.__version__)

    # Populate the summary data for the charts
    dataWorksheet.write('A8', "Application Summary")
    dataWorksheet.write_column('A9', projectSummaryData["projectNames"])

    dataWorksheet.merge_range('B6:E6', 'License Summary', tableHeaderFormat)
    
    dataWorksheet.write('B7', "P1 Licenses")
    dataWorksheet.write('B8', applicationSummaryData["numP1Licenses"])
    dataWorksheet.write_column('B9', projectSummaryData["numP1Licenses"])  

    dataWorksheet.write('C7', "P2 Licenses")
    dataWorksheet.write('C8', applicationSummaryData["numP2Licenses"])
    dataWorksheet.write_column('C9', projectSummaryData["numP2Licenses"])  

    dataWorksheet.write('D7', "P3 Licenses")
    dataWorksheet.write('D8', applicationSummaryData["numP3Licenses"])
    dataWorksheet.write_column('D9', projectSummaryData["numP3Licenses"]) 

    dataWorksheet.write('E7', "NA Licenses")
    dataWorksheet.write('E8', applicationSummaryData["numNALicenses"])
    dataWorksheet.write_column('E9', projectSummaryData["numNALicenses"]) 

    dataWorksheet.merge_range('F6:J6', 'Vulnerabilities', tableHeaderFormat)

    if cvssVersion == "3.x": 
        dataWorksheet.write('F7', "Critical")
        dataWorksheet.write('F8', applicationSummaryData["numCriticalVulnerabilities"])
        dataWorksheet.write_column('F9', projectSummaryData["numCriticalVulnerabilities"])  

    dataWorksheet.write('G7', "High")
    dataWorksheet.write('G8', applicationSummaryData["numHighVulnerabilities"])
    dataWorksheet.write_column('G9', projectSummaryData["numHighVulnerabilities"])  

    dataWorksheet.write('H7', "Medium")
    dataWorksheet.write('H8', applicationSummaryData["numMediumVulnerabilities"])
    dataWorksheet.write_column('H9', projectSummaryData["numMediumVulnerabilities"])  

    dataWorksheet.write('I7', "Low")
    dataWorksheet.write('I8', applicationSummaryData["numLowVulnerabilities"])
    dataWorksheet.write_column('I9', projectSummaryData["numLowVulnerabilities"])  

    dataWorksheet.write('J7', "None")
    dataWorksheet.write('J8', applicationSummaryData["numNoneVulnerabilities"])
    dataWorksheet.write_column('J9', projectSummaryData["numNoneVulnerabilities"])  

    dataWorksheet.merge_range('K6:M6', 'Review Status', tableHeaderFormat)

    dataWorksheet.write('K7', "Approved")
    dataWorksheet.write('K8', applicationSummaryData["numApproved"])
    dataWorksheet.write_column('K9', projectSummaryData["numApproved"])  

    dataWorksheet.write('L7', "Rejected")
    dataWorksheet.write('L8', applicationSummaryData["numRejected"])
    dataWorksheet.write_column('L9', projectSummaryData["numRejected"])  

    dataWorksheet.write('M7', "Draft")
    dataWorksheet.write('M8', applicationSummaryData["numDraft"])
    dataWorksheet.write_column('M9', projectSummaryData["numDraft"])  

    catagoryHeaderRow = 6
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
        applicationSummaryRow = 7  
        
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
    projectDataStartRow = 8 
    
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
        logger.debug("        Reporting for inventory item %s" %inventoryID)

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

        logger.debug("            Project Name:  %s   Inventory Item %s" %(projectName, inventoryItemName))
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

        # Highlight the version if it is old, not analyzed or invalid.
        if "Old version" in complianceIssues.keys():
            detailsWorksheet.write(row, column, componentVersionName, rejectedCellFormat)
            cellComment = "Old Version - " + complianceIssues["Old version"]
            detailsWorksheet.write_comment(row, column, cellComment, {'width' : 400, 'height' : 30})

        elif "Version not analyzed" in complianceIssues.keys():
            detailsWorksheet.write(row, column, componentVersionName, rejectedCellFormat)
            cellComment = "Version not analyzed - " + complianceIssues["Version not analyzed"]
            detailsWorksheet.write_comment(row, column, cellComment, {'width' : 400, 'height' : 30})

        elif "Invalid Version" in complianceIssues.keys():
            detailsWorksheet.write(row, column, componentVersionName, rejectedCellFormat)
            cellComment = "Invalid Version - " + complianceIssues["Invalid Version"]
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
        childProjects = parentProject["childProject"]
        childProjects.sort(key=lambda item: item.get("name"))
        
        for childProject in childProjects:
            projectName = childProject["name"]
            # Add this ID to the list of projects with other child projects
            # and get then do it again
            worksheet.write( row, column, projectName, boldCellFormat)

            row =  display_project_hierarchy(worksheet, childProject, row, column, boldCellFormat)
    return row
