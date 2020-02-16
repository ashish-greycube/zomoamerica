# -*- coding: utf-8 -*-
# Copyright (c) 2020, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import os
from frappe.model.document import Document
import io
import pypdftk
from frappe.utils import touch_file
from pprint import pprint
import time


class TobaccoLegalCompliance(Document):
    def get_fda(self):
        field_dictionary = frappe.db.sql("""
                SELECT
    tlc.permit_number as 'topmostSubform[0].Page1[0].TTBpermit[0]',
    tlc.phone as 'topmostSubform[0].Page1[0].Phone[0]',
    tlc.employer_identification_number as 'topmostSubform[0].Page1[0].empID[0]',
    tlc.email as 'topmostSubform[0].Page1[0].emailaddress[0]',
    tlc.month as 'topmostSubform[0].Page1[0].month[0]',
    tlc.year as 'topmostSubform[0].Page1[0].activityyear[0]',
    CONCAT_WS(
        '\n',
        tlc.address_line1,
        tlc.address_line2,
        tlc.zipcode,
        tlc.us_state
    ) as 'topmostSubform[0].Page1[0].compname[0]',
    tlc.legal_head as 'topmostSubform[0].Page1[0].contactname[0]',
    round(
        SUM(coalesce(PR.total_net_weight, 0)) * 2.20462,
        2
    ) as 'topmostSubform[0].Page2[0].volimport8[0]',
    case
        AC.account_type
        when "Tax" then SUM(coalesce(PTC.base_tax_amount, 0))
        else 0
    end as 'topmostSubform[0].Page2[0].volimport8[1]',
    'OWNER' as 'topmostSubform[0].Page2[0].title[0]',
    DATE_FORMAT(CURDATE(), '%%m/%%d/%%Y') as 'topmostSubform[0].Page2[0].dateprepared[0]'
FROM
    `tabTobacco Legal Compliance` tlc
    INNER JOIN `tabPurchase Receipt` PR ON PR.company = tlc.company
    and PR.docstatus = 1
    and MONTHNAME(PR.posting_date) = %s
    and year(PR.posting_date) = tlc.year
    INNER JOIN `tabPurchase Receipt Item` PRI on PR.name = PRI.parent
    AND PRI.item_group in (
        select
            distinct name
        from
            `tabItem Group`
        where
            parent_item_group = 'TOBACCO'
    )
    LEFT JOIN `tabPurchase Taxes and Charges` AS PTC ON PR.name = PTC.parent
    LEFT JOIN tabAccount as AC on PTC.account_head = AC.name  and AC.account_type = 'Tax'
    where tlc.name = %s
                 """, (self.month, self.name,), as_dict=True)
        return field_dictionary and field_dictionary[0] or {}


# field_dictionary = {
#     "topmostSubform[0].Page1[0].TTBpermit[0]": 'NJ-T1-40017',
#     "topmostSubform[0].Page1[0].Phone[0]": '(201)778-0188',
#     "topmostSubform[0].Page1[0].empID[0]": '82-5123531',
#     "topmostSubform[0].Page1[0].emailaddress[0]": 'AHMED@ZOMOAMERICA.COM',
#     "topmostSubform[0].Page1[0].month[0]": 'February',
#     "topmostSubform[0].Page1[0].activityyear[0]": '2020',
#     "topmostSubform[0].Page1[0].compname[0]": '138-140 MICHIGAN AVENUE \n PATERSON \n , NJ 07503',
#     "topmostSubform[0].Page1[0].contactname[0]": 'AHMED',
#     "topmostSubform[0].Page2[0].volimport8[0]": '3968.32',
#     "topmostSubform[0].Page2[0].volimport8[1]": '11243.60',
#     "topmostSubform[0].Page2[0].title[0]": 'OWNER',
#     "topmostSubform[0].Page2[0].dateprepared[0]": '02/15/2020'
# }

# return field_dictionary

    def get_55206(self):
        month_and_year = "%s %s" % (time.strptime(
            self.month, '%B').tm_mon, self.year)

        field_dictionary = frappe.db.sql("""
  SELECT
    tlc.company as '1 NAME OF IMPORTER',
    tlc.permit_number as '4 PERMIT NUMBER',
    SUBSTR( tlc.employer_identification_number FROM 1 FOR 2 ) as '5 EMPLOYER IDENTIFICATION NUMBER EIN',
    tlc.phone as '(Enter the telephone number including area code.)',
    %s as "3 MONTH AND YEAR",  
    SUBSTR( tlc.employer_identification_number FROM 3 ) as 'undefined',
    CONCAT_WS(
        '\n',
        tlc.address_line1,
        tlc.address_line2,
        tlc.zipcode,
        tlc.us_state
    ) as '2 PRINCIPAL BUSINESS ADDRESS Number Street City State and ZIP Code',
    tlc.opening_stock as 'PIPE TOBACCO Pounds g6 On Hand Beginning of Month',   -- opening allow user to enter
    round(SUM(coalesce(PR.total_net_weight, 0)) * 2.20462, 2) as 'PIPE TOBACCO Pounds g7 Imported and Released from Customs Custody into the United States',
    tlc.opening_stock + round(SUM(coalesce(PR.total_net_weight, 0)) * 2.20462, 2) as 'PIPE TOBACCO Pounds g11 TOTAL',
    2954 as 'PIPE TOBACCO Pounds g13 Transferred to Domestic Customers',
    tlc.opening_stock + round(SUM(coalesce(PR.total_net_weight, 0)) * 2.20462, 2) - 2954 as 'PIPE TOBACCO Pounds g19 On Hand End of Month',
    2954 + tlc.opening_stock + round(SUM(coalesce(PR.total_net_weight, 0)) * 2.20462, 2) - 2954 as 'PIPE TOBACCO Pounds g20 TOTAL',
    DATE_FORMAT(CURDATE(), '%%m/%%d/%%Y') as '22 DATE',
    tlc.email as '23 EMAIL ADDRESS',
    'OWNER' as '24 TITLE OR STATUS State whether individual owner partner member of a limited liability company or if officer of corporation give title',
    SUBSTR( tlc.phone FROM 1 FOR 3 ) as '25 TELEPHONE NUMBER.0',
    SUBSTR( tlc.phone FROM 3 FOR 3 ) as '25 TELEPHONE NUMBER.1',
    SUBSTR( tlc.phone FROM -3 ) as '25 TELEPHONE NUMBER.2'
FROM
    `tabTobacco Legal Compliance` tlc
    INNER JOIN `tabPurchase Receipt` PR ON PR.company = tlc.company
    and PR.docstatus = 1 
    and MONTHNAME(PR.posting_date) = %s
    and year(PR.posting_date) = tlc.year
    INNER JOIN `tabPurchase Receipt Item` PRI on PR.name = PRI.parent
    AND PRI.item_group in (
        select
            distinct name
        from
            `tabItem Group`
        where
            parent_item_group = 'TOBACCO'
    )
    LEFT JOIN `tabPurchase Taxes and Charges` AS PTC ON PR.name = PTC.parent
    LEFT JOIN tabAccount as AC on PTC.account_head = AC.name and AC.account_type = 'Tax'
    where tlc.name = %s""", (month_and_year, self.month, self.name), as_dict=True)

        # field_dictionary = {
        #     '1 NAME OF IMPORTER': 'MAWGROUP LLC',
        #     '4 PERMIT NUMBER': 'NJ-T1-40017',
        #     '5 EMPLOYER IDENTIFICATION NUMBER EIN': '82',
        #     '3 MONTH AND YEAR': "02/2020",
        #     'undefined': '5123531',
        #     '2 PRINCIPAL BUSINESS ADDRESS Number Street City State and ZIP Code': '138-140 MICHIGAN AVENUE \n PATERSON \n , NJ 07503',
        #     'PIPE TOBACCO Pounds g6 On Hand Beginning of Month': '6,355.33',
        #     'PIPE TOBACCO Pounds g7 Imported and Released from Customs Custody into the United States': '3,968.32',
        #     'PIPE TOBACCO Pounds g11 TOTAL': '10,323.65',
        #     'PIPE TOBACCO Pounds g13 Transferred to Domestic Customers': '2,954.75',
        #     'PIPE TOBACCO Pounds g19 On Hand End of Month': '7,368.90',
        #     'PIPE TOBACCO Pounds g20 TOTAL': '10,323.65',
        #     '22 DATE': '02/15/2020',
        #     '23 EMAIL ADDRESS': 'AHMED@TOBACCO.COM',
        #     '24 TITLE OR STATUS State whether individual owner partner member of a limited liability company or if officer of corporation give title': 'OWNER',
        #     '0': '201',
        #     '1': '778',
        #     '2': '0188'
        # }
        return field_dictionary and field_dictionary[0] or {}


def touch_random_file():
    fname = os.path.join(
        "/tmp", "{0}.pdf".format(frappe.generate_hash(length=10)))
    touch_file(fname)
    return fname


@frappe.whitelist()
def download_52206(docname="FDA-3852-January-year-Zomo America"):

    # Uses https://github.com/revolunet/pypdftk for form filling and merging pdf
    # pypdftk depends on pdftk
    # need to install pypdftk and pdftk
    # sudo apt-get install pdftk
    # pip install pypdftk

    ttbf_template = frappe.get_site_path('private', 'files', 'ttbf_52206.pdf')
    fda_template = frappe.get_site_path('private', 'files', 'FDA3852.pdf')

    doc = frappe.get_doc("Tobacco Legal Compliance", docname)
    file_name = "%s.pdf" % doc.name

    ttbf = pypdftk.fill_form(
        ttbf_template, doc.get_55206(), out_file=touch_random_file())

    fda = pypdftk.fill_form(
        fda_template, doc.get_fda(), out_file=touch_random_file())

    merged_file = pypdftk.concat([fda, ttbf], touch_random_file())

    # print(merged_file)
    # return merged_file

    with open(merged_file, "rb") as fileobj:
        filedata = fileobj.read()
        frappe.local.response.filename = file_name
        frappe.local.response.filecontent = filedata
        frappe.local.response.type = "download"


def test():
    download_52206()
