from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=1000
    )

    open_robot_order_website()
    orders = get_orders()
    for order in orders:       
       fill_the_form(order)
    archive_receipts()
    
def open_robot_order_website():
    """Open the order website here"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")    

def download_order_file():
    """Download the order csv file"""
    http=HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv",overwrite=True)
     
def get_orders():
    """Get all the orders in table format"""
    download_order_file()

    read_from_csv=Tables()
    order = read_from_csv.read_table_from_csv("orders.csv",header=True)
    return order

def close_annoying_modal():
    """Close the popup"""
    page=browser.page()
    page.click("button:text('OK')")

def fill_the_form(order):
    """Fills in the order data and click the 'order' button"""
    close_annoying_modal()

    page=browser.page()
    page.select_option("#head",order["Head"])
    page.click("#id-body-"+order["Body"])
    page.fill("input[placeholder='Enter the part number for the legs']",order["Legs"])
    page.fill("#address",order["Address"])
    page.click("text=Preview")

    """Take screenshot"""
    screenshot_path=screenshot_robot(order["Order number"])

    page.click("button:text('Order')")

    # Check if the alert element exists using a CSS selector
    alert_element = page.locator('div.alert.alert-danger[role="alert"]')
    while alert_element.is_visible():
        page.click("button:text('Order')")
        alert_element = page.locator('div.alert.alert-danger[role="alert"]')

    """Store receipt as pdf"""
    receipt_pdf_path=store_receipt_as_pdf(order["Order number"])

    """Embed the screenshot and receipt"""
    embed_screenshot_to_receipt(screenshot_path,receipt_pdf_path)

    page.click("button:text('Order another robot')")

def store_receipt_as_pdf(order_number):
    """Store the reciept as PDF"""
    page=browser.page()
    order_results_html_page=page.locator("#order-completion").inner_html()

    pdf=PDF()
    order_pdf_path="output/order_result_"+order_number+".pdf"
    pdf.html_to_pdf(order_results_html_page,order_pdf_path)

    return order_pdf_path

def screenshot_robot(order_number):
    """Store the screenshot"""
    order_screenshot_path="output/order_screenshot_"+order_number+".png"

    page=browser.page()

    element=page.locator("#robot-preview-image")
    element.screenshot(path=order_screenshot_path)

    return order_screenshot_path

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the screenshot and receipt"""
    pdf =PDF()
    
    files_to_merge=[
        pdf_file,
        screenshot
    ]

    pdf.add_watermark_image_to_pdf(
        image_path=screenshot,
        source_path=pdf_file,
        output_path=pdf_file
    )

def archive_receipts():
    """Archive the reciepts"""
    archive=Archive()
    archive.archive_folder_with_zip("output","output/final.zip",include="*.pdf")




