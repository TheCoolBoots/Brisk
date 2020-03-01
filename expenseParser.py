import re
import price_parser
from price_parser import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dateutil import parser as dateParser
import io
import os
from google.cloud import vision
from google.cloud.vision import types
import datetime

# food, groceries, quality of life, bills/utilities/rent, gas/transportation

class expenseParser:
    def __init__(self):
        self.whitespace = "\n\t "
        self.today = datetime.datetime.now()

    # def get_prices(self, stringList):
    #     max_price = 0
    #     for index in range(len(stringList) - 1):
    #         combined = stringList[index].append(stringList[index+1])

    def get_descriptionAndCategory(self, receiptList):
        foodListFile = open("foodlist.txt", "r")
        foodList = foodListFile.read().split("\n")
        groceriesFile = open("groceries.txt", "r")
        groceryList = groceriesFile.read().split("\n")
        qualityOfLifeFile = open("QOL.txt", "r")
        QOLList = qualityOfLifeFile.read().split("\n")
        utilFile = open("utilities.txt", "r")
        utilList = utilFile.read().split("\n")
        transportFile = open("transport.txt", "r")
        transportList = transportFile.read().split("\n")

        foodListFile.close()
        groceriesFile.close()
        qualityOfLifeFile.close()
        utilFile.close()
        transportFile.close()

        for string in receiptList:
            string = self.cleanString(string)
            for food in foodList:
                # thisFood = food
                if food.lower() in string:
                    return food, "food"
            for grocery in groceryList:
                if grocery.lower() in string:
                    return grocery, "groceries"
            for QOL in QOLList:
                if QOL.lower() in string:
                    return QOL, "Quality Of Life"
            for util in utilList:
                if util.lower() in string:
                    return util, "bills/utilities/rent"
            for trans in transportList:
                if trans.lower() in string:
                    return trans, "car/transportation"

        return "couldn't generate description", "couldn't generate category"

    def get_price(self, stringList):
        prices = []
        max_price = None
        for item in stringList:
            prices.append(Price.fromstring(item))
        for price in prices:
            if "." in str(price.amount):
                if max_price is None:
                    max_price = price.amount
                elif max_price < price.amount:
                    max_price = price.amount
                else:
                    next
        return max_price

    def cleanString(self, string):
        string = string.lower()
        string = string.replace('\n', ' ')
        string = string.replace('\t', ' ')
        string = string.replace('\\', '/')
        string = re.sub(' +', ' ', string)
        return string

    def listContainsDate(self, stringList):
        # print(stringList)
        for i in stringList:
            returnVal = self.stringContainsDate(i)
            if(returnVal != -1):
                return returnVal
        return -1

    def stringContainsDate(self, string):
        string = self.cleanString(string)
        tempList = string.split(" ")
        # print(tempList)
        for str in tempList:
            try:
                date = dateParser.parse(str, ignoretz = True)
                deltaCheck = self.today - date
                years = deltaCheck.total_seconds()/31557600  # 31557600 seconds in a year
                if(years > 30):
                    # if date is 30 years ago, don't consider it
                    continue
                return date
            except ValueError:
                continue
        return -1

    def getModified(self):
        return self.modified

    def setInput(self, inputString):
        self.original = inputString
        self.modified = self.original

class expenseStruct:
    def __init__(self, timestamp, DOP, amount, description, category):
        self.timestamp = timestamp
        self.DOP = DOP
        self.amount = amount
        self.description = description
        self.category = category

class expenseManager:
    def __init__(self):
        self.defaultSpreadsheetName = "brisk_records"
        self.jsonFile = 'admin.json'
        self.scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        pass

    def logExpense(self, expense):
        sheet = self.getSheetObject(self.jsonFile, self.scope)
        sheet.append_row([expense.timestamp, expense.DOP, expense.amount, expense.description, expense.category], 'USER_ENTERED')
        pass

    def getSheetObject(self, jsonFile, scope):
        creds = ServiceAccountCredentials.from_json_keyfile_name(jsonFile, scope)
        gc = gspread.authorize(creds)
        return gc.open("brisk_records").sheet1

def getInputString(filepath):
    # Instantiates a client
    # scope = ['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/cloud-vision']
    # creds = ServiceAccountCredentials.from_json_keyfile_name('visionClient.json', scope)
    # client = gspread.authorize(creds)gcl
    client = vision.ImageAnnotatorClient()

    # The name of the image file to read
    file_name = os.path.abspath(filepath)

    # Loads the image into memory
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Text Detection
    response_text = client.text_detection(image=image)
    texts = response_text.text_annotations

    # Prints text
    total_text = []
    for text in texts:
        total_text.append(text.description)
    return total_text


# parsedList = ['Mustang Station\n185 KARA\nCHK 79762\n2/4/2020 12:10 PM\nDine In Student\n1 Mediterranean sl\n1 Meat lovers sl\nMastercard\nat021105 xXx0630\nTrans: 226331786\n3.50\n3.50\n$7.00\nSubtotal\nPayment\nChange Due\n$7.00\n$7.00\n$0.00\nCheck Closed\n2/4/2020 12:11 PM\n', 'Mustang', 'Station', '185', 'KARA', 'CHK', '79762', '2/4/2020', '12:10', 'PM', 'Dine', 'In', 'Student', '1', 'Mediterranean', 'sl', '1', 'Meat', 'lovers', 'sl', 'Mastercard', 'at021105', 'xXx0630', 'Trans:', '226331786', '3.50', '3.50', '$7.00', 'Subtotal', 'Payment', 'Change', 'Due', '$7.00', '$7.00', '$0.00', 'Check', 'Closed', '2/4/2020', '12:11', 'PM']
# parsedList =  ['Payment', '2/4/2020', 'Change', 'Due', '$7.00', '$7.00', '$0.00', 'Check', 'Closed', '2/4/2020', '12:11', 'PM']
# parsedList = ['CALIFORNIA\nFRESH MARKET\nIGA\ntur locel, hometman pronad\n771 Foothill Blvd, SLO, CA 93405\n805-250-1425\n2/29/2020 10:33:35 AM 2 1131 2 20\nCashier: Jessica 0.\n7.99 FA\n6.00 I A\n8.35 t C\nLARK ELLEN CUMIN CRNCH MX\nTRI TIP BURRITO\nE/R WINGS BAR\n"1.05 LB @ $7.99/LB\nFRESH SOUP BAR\n"0.96 LB @ $6.99/LB\nTRI TIP BURRITO\n6.71 T C\n-6.00 VD\nSUBTOTAL\n15.06\nfÖTAL\nCREDIT CARD\nCREDIT ACCT\n23.05\nTAX 7.75\n24.22\n24.22\n0.00\nItem Count 3\nThạnk you for shopping with us!\nCalifornia Fresh Market\nwww.californiafreshmarket.com\nwww.igastore-feedback.com\n..U\'STO MER COPY*\nCalifornia Fresh Market\n771 E. Foothil Blvd.\nSan Luis Obispo, CA 93405\n(805) 250-1425\n10:33:52\nChip\n02/29/2020\nVISA CREDIT\nCARD #:\nPURCHASE\nAUTH CODE:029484\nEntry Method:\nXXXXXXXXXXXX5859\nAPPROVED\nMode:\nAID:\nTVR:\nIAD:\nTSI:\nARC:\nTC:\nMID: 499867\nIssuer\nA0000000031010\n8000008000\n06010A03A0A000\n6800\n00\nB47A19E1A88EBC81\n001 SEQ: 020608\nTID:\nTotal:\nUSD$ 24.22\nTHANK YOU FOR\nSHOPPING WITH US!\n', 'CALIFORNIA', 'FRESH', 'MARKET', 'IGA', 'tur', 'locel,', 'hometman', 'pronad', '771', 'Foothill', 'Blvd,', 'SLO,', 'CA', '93405', '805-250-1425', '2/29/2020', '10:33:35', 'AM', '2', '1131', '2', '20', 'Cashier:', 'Jessica', '0.', '7.99', 'FA', '6.00', 'I', 'A', '8.35', 't', 'C', 'LARK', 'ELLEN', 'CUMIN', 'CRNCH', 'MX', 'TRI', 'TIP', 'BURRITO', 'E/R', 'WINGS', 'BAR', '"1.05', 'LB', '@', '$7.99/LB', 'FRESH', 'SOUP', 'BAR', '"0.96', 'LB', '@', '$6.99/LB', 'TRI', 'TIP', 'BURRITO', '6.71', 'T', 'C', '-6.00', 'VD', 'SUBTOTAL', '15.06', 'fÖTAL', 'CREDIT', 'CARD', 'CREDIT', 'ACCT', '23.05', 'TAX', '7.75', '24.22', '24.22', '0.00', 'Item', 'Count', '3', 'Thạnk', 'you', 'for', 'shopping', 'with', 'us!', 'California', 'Fresh', 'Market', 'www.californiafreshmarket.com', 'www.igastore-feedback.com', "..U'STO", 'MER', 'COPY*', 'California', 'Fresh', 'Market', '771', 'E.', 'Foothil', 'Blvd.', 'San', 'Luis', 'Obispo,', 'CA', '93405', '(805)', '250-1425', '10:33:52', 'Chip', '02/29/2020', 'VISA', 'CREDIT', 'CARD', '#:', 'PURCHASE', 'AUTH', 'CODE:029484', 'Entry', 'Method:', 'XXXXXXXXXXXX5859', 'APPROVED', 'Mode:', 'AID:', 'TVR:', 'IAD:', 'TSI:', 'ARC:', 'TC:', 'MID:', '499867', 'Issuer', 'A0000000031010', '8000008000', '06010A03A0A000', '6800', '00', 'B47A19E1A88EBC81', '001', 'SEQ:', '020608', 'TID:', 'Total:', 'USD$', '24.22', 'THANK', 'YOU', 'FOR', 'SHOPPING', 'WITH', 'US!']
# parsedList = ['The Avenue\n1951 HANNAH\nCHK 126729\n2/27/2020 3:08 PM\nDine In Student\n1 ABC BB\nABC Burger\nFrench Fries\nCOKE FTN\nMastercard\nat050909 xxx0630\nTrans: 227690613\n9.45\n$9.45\nSubtotal\nPayment\nChange Due\n$9.45\n$9.45\n$0.00\nCheck Closed\n2/27/2020 3:09 PM\n', 'The', 'Avenue', '1951', 'HANNAH', 'CHK', '126729', '2/27/2020', '3:08', 'PM', 'Dine', 'In', 'Student', '1', 'ABC', 'BB', 'ABC', 'Burger', 'French', 'Fries', 'COKE', 'FTN', 'Mastercard', 'at050909', 'xxx0630', 'Trans:', '227690613', '9.45', '$9.45', 'Subtotal', 'Payment', 'Change', 'Due', '$9.45', '$9.45', '$0.00', 'Check', 'Closed', '2/27/2020', '3:09', 'PM']
def scanReceiptIntoSheets(filepath):
    parsedList = getInputString(filepath)
    parser = expenseParser()
    # print(parsedList)
    DOP = parser.listContainsDate(parsedList)
    # print(DOP.date())
    price = parser.get_price(parsedList)
    # print(price)
    descriptionCategory = parser.get_descriptionAndCategory(parsedList)
    # print(descriptionCategory[0])
    # print(descriptionCategory[1])
    now = datetime.datetime.today()
    manager = expenseManager()
    manager.logExpense(expenseStruct(str(now), str(DOP.date()), str(price), descriptionCategory[0], descriptionCategory[1]))



