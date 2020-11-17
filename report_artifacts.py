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
    projectName = reportData["projectName"] 
    inventoryData = reportData["inventoryData"]
    projectList = reportData["projectList"]
    projectSummaryData = reportData["projectSummaryData"]
    applicationSummaryData = reportData["applicationSummaryData"]
   
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
 
    # If there is some sort of hierarchy then show specific project summeries
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
    html_ptr.write("            <th colspan='8' class='text-center'><h4>Inventory Items</h4></th>\n") 
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
        inventoryLink = inventoryData[inventoryID]["inventoryLink"]
        projectLink = inventoryData[inventoryID]["projectLink"]

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
    html_ptr.write("  <div style='float:left'>&copy; 2020 Flexera</div>\n")
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
        generate_project_hierarchy_tree(html_ptr, projectList)
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
        
            var table = $('#inventoryData').DataTable();

            $(document).ready(function() {
                table;
            } );
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
                }]
            },

            options: defaultBarChartOptions,
        });
        applicationLicensesChart.options.title.text = "License Summary"
        applicationLicensesChart.options.tooltips.titleFontSize = 0

        ''' %(applicationSummaryData["numP1Licenses"], applicationSummaryData["numP2Licenses"], applicationSummaryData["numP3Licenses"])  )

   
    html_ptr.write(''' 
    
    var applicationVulnerabilities= document.getElementById("applicationVulnerabilities");
    var applicationVulnerabilityChart = new Chart(applicationVulnerabilities, {
        type: 'horizontalBar',
        data: {
            datasets: [{
                // Critical Vulnerabilities
                label: 'Critical',
                data: [%s],
                backgroundColor: "#400000"
            },{
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
    
    ''' %(applicationSummaryData["numCriticalVulnerabilities"], applicationSummaryData["numHighVulnerabilities"], applicationSummaryData["numMediumVulnerabilities"], applicationSummaryData["numLowVulnerabilities"], applicationSummaryData["numNoneVulnerabilities"]) )
    

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
def generate_project_hierarchy_tree(html_ptr, projectHierarchy):
    logger.info("Entering generate_project_hierarchy_tree")

    html_ptr.write('''var hierarchy = [\n''')

    for project in projectHierarchy:

        html_ptr.write('''{
            'id': '%s', 
            'parent': '%s', 
            'text': '%s',
            'a_attr': {
                'href': '%s'
            }
        },\n'''  %(project["projectID"], project["parent"], project["projectName"], project["projectLink"]))

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
                }]
            },

            options: defaultBarChartOptions,
        });
        projectLicensesChart.options.title.text = "License Summary"

        ''' %(projectSummaryData["projectNames"], projectSummaryData["numP1Licenses"], projectSummaryData["numP2Licenses"], projectSummaryData["numP3Licenses"])  )

    html_ptr.write(''' 
    
    var projectVulnerabilities= document.getElementById("projectVulnerabilities");
    var projectVulnerabilityChart = new Chart(projectVulnerabilities, {
        type: 'horizontalBar',
        data: {
            labels: %s,
            datasets: [{
                // Critical Vulnerabilities
                label: 'Critical',
                data: %s,
                backgroundColor: "#400000"
            },{
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
    
    
    ''' %(projectSummaryData["projectNames"], projectSummaryData["numCriticalVulnerabilities"], projectSummaryData["numHighVulnerabilities"], projectSummaryData["numMediumVulnerabilities"], projectSummaryData["numLowVulnerabilities"], projectSummaryData["numNoneVulnerabilities"]) )
    

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
