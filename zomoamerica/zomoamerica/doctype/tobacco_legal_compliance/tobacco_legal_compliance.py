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
        tlc.city,
        tlc.zipcode,
        tlc.us_state
    ) as 'topmostSubform[0].Page1[0].compname[0]',
    tlc.legal_head as 'topmostSubform[0].Page1[0].contactname[0]',
    MTIW.mti_w + PRW.p_weight  as 'topmostSubform[0].Page2[0].voimport12[0]',
    PRTAX.ptax+ MTTAX.TAX_7501 as 'topmostSubform[0].Page2[0].volimport12[0]',
    tlc.title as 'topmostSubform[0].Page2[0].title[0]',
    DATE_FORMAT(CURDATE(), '%%m/%%d/%%Y') as 'topmostSubform[0].Page2[0].dateprepared[0]'
	FROM
    `tabTobacco Legal Compliance` tlc,
    (SELECT 
  	SUM(coalesce(LCT.amount, 0))
    as TAX_7501
    FROM `tabLanded Cost Taxes and Charges` AS LCT 
    where LCT.expense_account IN (SELECT distinct name from tabAccount as AC1 where AC1.account_type = 'Tax') 
    AND LCT.PARENT IN (select distinct parent from `tabStock Entry Detail` SED 
    where SED.s_warehouse like '%%bonded%%' and SED.t_warehouse  = %s
    AND SED.item_group in (
        select
            distinct name
        from
            `tabItem Group`
        where
            parent_item_group = 'TOBACCO'
    )
    and SED.parent in (select distinct name from `tabStock Entry` as SE 
    WHERE SE.purpose = 'Material Transfer'
    and SE.docstatus = 1
    and MONTHNAME(SE.posting_date) = %s 
    and year(SE.posting_date) = %s ) )) as MTTAX,
    (SELECT 
    SUM(coalesce(PTC.base_tax_amount, 0)) as ptax
 	from
 	`tabPurchase Taxes and Charges` AS PTC 
 	INNER JOIN `tabPurchase Receipt` PR 
 	ON PR.name = PTC.parent 
    AND PR.docstatus = 1
    and PR.set_warehouse = %s
    and MONTHNAME(PR.posting_date) =  %s 
    and year(PR.posting_date) = %s
    INNER JOIN tabAccount as AC 
    on PTC.account_head = AC.name
     and AC.account_type = 'Tax'
    AND PR.name in (select distinct parent from  `tabPurchase Receipt Item` PRI 
    where PRI.item_group in (
        select
            distinct name
        from
            `tabItem Group`
        where
            parent_item_group = 'TOBACCO'
    ))) AS PRTAX,
    (select  coalesce(round(SUM(coalesce(coalesce(I.weight_per_unit,0) * coalesce(SED.qty,0), 0)) * 2.20462,2),0)  as mti_w
    from `tabStock Entry Detail` SED 
    INNER JOIN tabItem  as I 
    ON I.item_code= SED.item_code
    where SED.s_warehouse 
    like '%%bond%%' and SED.t_warehouse  = %s 
    AND SED.item_group in (
        select
            distinct name
        from
            `tabItem Group`
        where
            parent_item_group = 'TOBACCO'
    )
    and SED.parent in (select distinct name from `tabStock Entry` as SE 
    WHERE SE.purpose = 'Material Transfer'
    and SE.docstatus = 1
    and MONTHNAME(SE.posting_date) = %s 
    and year(SE.posting_date) = %s 
    )) as MTIW,   
    (select 
    round(SUM(coalesce(PR.total_net_weight, 0)) * 2.20462,2) AS p_weight
 	from `tabPurchase Receipt` PR 
 	where PR.docstatus = 1
    and PR.set_warehouse = %s 
    and MONTHNAME(PR.posting_date) = %s 
    and year(PR.posting_date) = %s
    AND PR.name in (select distinct parent  from `tabPurchase Receipt Item` PRI
    where  PRI.item_group in (
        select
            distinct name
        from
            `tabItem Group`
        where
            parent_item_group = 'TOBACCO'
    ) ) ) as PRW
    where tlc.name = %s
                 """, (self.company_warehouse, self.month, self.year, self.company_warehouse, self.month, self.year, self.company_warehouse, self.month, self.year, self.company_warehouse, self.month, self.year, self.name), as_dict=True)
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
#     "topmostSubform[0].Page2[0].voimport12[0]": '3968.32',
#     "topmostSubform[0].Page2[0].volimport12[0]": '11243.60',
#     "topmostSubform[0].Page2[0].title[0]": 'OWNER',
#     "topmostSubform[0].Page2[0].dateprepared[0]": '02/15/2020'
# }

# return field_dictionary

    def get_55206(self):
        month_and_year = "%s %s" % (time.strptime(
            self.month, '%B').tm_mon, self.year)

        field_dictionary = frappe.db.sql("""SELECT
    tlc.company as '1 NAME OF IMPORTER',
    tlc.permit_number as '4 PERMIT NUMBER',
    SUBSTR( tlc.employer_identification_number FROM 1 FOR 2 ) as '5 EMPLOYER IDENTIFICATION NUMBER EIN',
    tlc.phone as '(Enter the telephone number including area code.)',
    %s as "3 MONTH AND YEAR",  
    SUBSTR( tlc.employer_identification_number FROM 3 ) as 'undefined',
    CONCAT_WS(
        '\n',
        tlc.address_line1,
        tlc.city,
        tlc.zipcode,
        tlc.us_state
    ) as '2 PRINCIPAL BUSINESS ADDRESS Number Street City State and ZIP Code',
    tlc.opening_stock as 'PIPE TOBACCO Pounds g6 On Hand Beginning of Month', 
     MTIW.mti_w + PRW.p_weight 
    as 'PIPE TOBACCO Pounds g7 Imported and Released from Customs Custody into the United States',
    tlc.opening_stock +  MTIW.mti_w + PRW.p_weight  as 'PIPE TOBACCO Pounds g11 TOTAL',
    domesticsales.total_tobacco_weight_lbs  as 'PIPE TOBACCO Pounds g13 Transferred to Domestic Customers',
    tlc.opening_stock +  MTIW.mti_w + PRW.p_weight  - domesticsales.total_tobacco_weight_lbs  as 'PIPE TOBACCO Pounds g19 On Hand End of Month',
    domesticsales.total_tobacco_weight_lbs  + tlc.opening_stock +  MTIW.mti_w + PRW.p_weight  - domesticsales.total_tobacco_weight_lbs  as 'PIPE TOBACCO Pounds g20 TOTAL',
    DATE_FORMAT(CURDATE(), '%%m/%%d/%%Y') as '22 DATE',
    tlc.email as '23 EMAIL ADDRESS',
    tlc.title  as '24 TITLE OR STATUS State whether individual owner partner member of a limited liability company or if officer of corporation give title',
    SUBSTR( tlc.phone FROM 1 FOR 3 ) as '25 TELEPHONE NUMBER.0',
    SUBSTR( tlc.phone FROM 3 FOR 3 ) as '25 TELEPHONE NUMBER.1',
    SUBSTR( tlc.phone FROM -3 ) as '25 TELEPHONE NUMBER.2'
    FROM
    `tabTobacco Legal Compliance` tlc ,
    (select  coalesce(round(SUM(coalesce(coalesce(I.weight_per_unit,0) * coalesce(SED.qty,0), 0)) * 2.20462,2),0)  as mti_w
    from `tabStock Entry Detail` SED 
    INNER JOIN tabItem  as I 
    ON I.item_code= SED.item_code
    where SED.s_warehouse 
    like '%%bond%%' and SED.t_warehouse  = %s 
    AND SED.item_group in (
        select
            distinct name
        from
            `tabItem Group`
        where
            parent_item_group = 'TOBACCO'
    )
    and SED.parent in (select distinct name from `tabStock Entry` as SE 
    WHERE SE.purpose = 'Material Transfer'
    and SE.docstatus = 1
    and MONTHNAME(SE.posting_date) = %s 
    and year(SE.posting_date) = %s 
    )) as MTIW,     
    (select 
    round(SUM(coalesce(PR.total_net_weight, 0)) * 2.20462,2) AS p_weight
 	from `tabPurchase Receipt` PR 
 	where PR.docstatus = 1
    and PR.set_warehouse = %s 
    and MONTHNAME(PR.posting_date) = %s 
    and year(PR.posting_date) = %s 
    AND PR.name in (select distinct parent  from `tabPurchase Receipt Item` PRI
    where  PRI.item_group in (
        select
            distinct name
        from
            `tabItem Group`
        where
            parent_item_group = 'TOBACCO'
    ) )) as PRW,
  	(select sum(round(coalesce(item.total_weight,0)*2.20462,2)) as total_tobacco_weight_lbs from `tabSales Invoice` si
    LEFT JOIN (SELECT sum(total_weight)as total_weight, parent from (select CASE weight_uom
                            WHEN 'Gram' then sum(total_weight/1000)
                            ELSE sum(total_weight)
                            END as total_weight,
                            parent from `tabSales Invoice Item` 
                            where item_group
                            in
                            (select distinct name from `tabItem Group` 
                            where parent_item_group = 'TOBACCO') group by parent,weight_uom) as t group by parent) item 
                            on item.parent=si.name
    WHERE si.docstatus=1
    and si.is_return <> 1 
    AND MONTHNAME(si.posting_date) = %s
    and year(si.posting_date) = %s 
    and si.company = %s
   ) as domesticsales 
    where tlc.name = %s""", (month_and_year, self.company_warehouse, self.month, self.year, self.company_warehouse, self.month, self.year, self.month, self.year, self.company, self.name), as_dict=True)

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

    def get_tpt10(self):
        field_dictionary = frappe.db.sql("""SELECT
        CASE tlc.month 
        when 'January' THEN 1 
        WHEN 'February' THEN 2
        when 'March' THEN 3
        WHEN 'April' THEN 4
        when 'May' THEN 5
        WHEN 'June' THEN 6
        WHEN 'July' THEN 7
        WHEN 'August' THEN 8
        WHEN 'September' THEN 9
        WHEN 'October' THEN 10
        WHEN 'November' THEN 11
        WHEN 'December' THEN 12
        ELSE 0 END as 'Month',
        tlc.year as 'Year',
        tlc.employer_identification_number as 'Federal ID Number',
        tlc.title as 'Title',
        DATE_FORMAT(CURDATE(), '%%m/%%d/%%Y') as 'Date',
        tlc.legal_head as  'Printed Taxpayer Name',
        tlc.phone as 'Telephone Number' ,
        tlc.tax_payer_id as 'Taxpayer ID',
        CONCAT_WS(
                '\n',
                tlc.preparer_address_line1,
                tlc.preparer_address_line2,
                tlc.preparer_city,
                tlc.preparer_state,
                tlc.preparer_zipcode
            ) AS 'Preparer s Address',
        tlc.preparer_id as 'Preparer s ID',
        tlc.legal_company as 'Taxpayer Name',
        TRIM(tlc.address_line1) as 'Address',
        'PATERSON NJ 07053' as 'City',
        0 as 1A,
        (COALESCE(MTA.mt_total_amt,0)+ COALESCE(PRA.p_total,0)) AS 2A,
        COALESCE(MTA.mt_total_amt,0)+ COALESCE(PRA.p_total,0)  AS 7A,
        COALESCE(TOTAL_SALES.total_sales,0) - COALESCE(NJSAMPLES.nj_sample_sales,0) as  8A,
        TOTAL_SALES.total_sales - NJSALES.nj_sales as 10A,
        (TOTAL_SALES.total_sales - NJSAMPLES.nj_sample_sales) - (TOTAL_SALES.total_sales - NJSALES.nj_sales) as 11A,
        0 AS 12A,
        NJSAMPLES.nj_sample_sales AS 13A,
        0 AS 14A,
        NJSAMPLES.nj_sample_sales  AS 15A,
        (TOTAL_SALES.total_sales - NJSAMPLES.nj_sample_sales) - (TOTAL_SALES.total_sales - NJSALES.nj_sales) +  NJSAMPLES.nj_sample_sales AS 16A,
        round(((TOTAL_SALES.total_sales - NJSAMPLES.nj_sample_sales) - (TOTAL_SALES.total_sales - NJSALES.nj_sales) +  NJSAMPLES.nj_sample_sales )* tlc.state_tax_percent,2) as 18A,
        round(((TOTAL_SALES.total_sales - NJSAMPLES.nj_sample_sales) - (TOTAL_SALES.total_sales - NJSALES.nj_sales) +  NJSAMPLES.nj_sample_sales )* tlc.state_tax_percent,2) as 19A,
        0 AS 20A,
        round(((TOTAL_SALES.total_sales - NJSAMPLES.nj_sample_sales) - (TOTAL_SALES.total_sales - NJSALES.nj_sales) +  NJSAMPLES.nj_sample_sales )* tlc.state_tax_percent,2) as 21A
        from `tabTobacco Legal Compliance` AS tlc ,
        (select  SUM(total_amount)   as mt_total_amt
            from `tabStock Entry` as SE 
            WHERE SE.purpose = 'Material Transfer'
            and SE.docstatus = 1
            and SE.from_warehouse like '%%bond%%' and SE.to_warehouse  = %s
            and MONTHNAME(SE.posting_date) = %s 
            and year(SE.posting_date) =  %s 
            and SE.name IN (SELECT DISTINCT parent from  `tabStock Entry Detail` AS SED 
            where SED.item_group in (
                select
                    distinct name
                from
                    `tabItem Group`
                where
                    parent_item_group = 'TOBACCO'
            ))
            ) as MTA,   
            (select 
            SUM(rounded_total) AS p_total
            from `tabPurchase Receipt` PR 
            where PR.docstatus = 1
            and PR.set_warehouse =  %s  
            and MONTHNAME(PR.posting_date) =  %s  
            and year(PR.posting_date) =  %s 
            and name in (select distinct parent from `tabPurchase Receipt Item` PRI
            where  PRI.item_group in (
                select
                    distinct name
                from
                    `tabItem Group`
                where
                    parent_item_group = 'TOBACCO'))
            ) as PRA,
            (SELECT  sum(amount) AS total_sales from  `tabSales Invoice Item` 
                                    where item_group in
                                    (select distinct name from `tabItem Group` 
                                    where parent_item_group = 'TOBACCO') 
                                    and parent in (select distinct name from `tabSales Invoice` si 
            WHERE si.docstatus=1
            and si.is_return <> 1 
            AND MONTHNAME(si.posting_date) = %s  
            and year(si.posting_date) =  %s 
            and si.company = %s  ))    
            as TOTAL_SALES,
            (SELECT  sum(amount)as nj_sample_sales from  `tabSales Invoice Item` 
                                    where item_group in
                                    (select distinct name from `tabItem Group` 
                                    where parent_item_group = 'TOBACCO') 
                                    and parent in (select distinct si.name from `tabSales Invoice` si 
                                    inner JOIN tabAddress  AS CA ON 
                                    si.customer_address = CA.name and CA.state = 'NJ'
            AND si.docstatus=1
            and si.is_return <> 1 
            AND si.customer in ('SAMPLE/TASTING','SAMPLE/EVENT')
            AND MONTHNAME(si.posting_date) = %s 
            and year(si.posting_date) =  %s 
            and si.company =  %s ) 
            )as NJSAMPLES,
            (SELECT  sum(amount)as nj_sales from  `tabSales Invoice Item` 
                                    where item_group in
                                    (select distinct name from `tabItem Group` 
                                    where parent_item_group = 'TOBACCO') 
                                    and parent in (select distinct si.name from `tabSales Invoice` si 
                                    inner JOIN tabAddress  AS CA ON 
                                    si.customer_address = CA.name and CA.state = 'NJ'
            AND si.docstatus=1
            and si.is_return <> 1 
            AND MONTHNAME(si.posting_date) = %s 
            and year(si.posting_date) =  %s   
            and si.company =  %s ) 
            )as NJSALES
        where tlc.name = %s""", (self.company_warehouse, self.month, self.year, self.company_warehouse, self.month, self.year, self.month, self.year, self.company, self.month, self.year, self.company, self.month, self.year, self.company, self.name), as_dict=True)
        return field_dictionary and field_dictionary[0] or {}


def touch_random_file():
    fname = os.path.join(
        "/tmp", "{0}.pdf".format(frappe.generate_hash(length=10)))
    touch_file(fname)
    return fname


@frappe.whitelist()
def download_tlc(docname="FDA-3852-January-year-Zomo America"):

    # Uses https://github.com/revolunet/pypdftk for form filling and merging pdf
    # pypdftk depends on pdftk
    # need to install pypdftk and pdftk
    # sudo apt-get install pdftk
    # pip install pypdftk

    ttbf_template = frappe.get_site_path('private', 'files', 'ttbf_52206.pdf')
    fda_template = frappe.get_site_path('private', 'files', 'FDA3852.pdf')
    tpt10_template = frappe.get_site_path(
        'private', 'files', 'TPT-10_template.pdf')

    doc = frappe.get_doc("Tobacco Legal Compliance", docname)
    file_name = "%s.pdf" % doc.name

    pdfreport = ""

    if doc.report_type == "FDA-3852":
        pdfreport = pypdftk.fill_form(
            fda_template, doc.get_fda(), out_file=touch_random_file())
    elif doc.report_type == "TTB-5220":
        pdfreport = pypdftk.fill_form(
            ttbf_template, doc.get_55206(), out_file=touch_random_file())
    elif doc.report_type == "NJ TPT-10":
        pdfreport = pypdftk.fill_form(
            tpt10_template, doc.get_tpt10(), out_file=touch_random_file())
    else:
        pass

    if not pdfreport:
        frappe.throw("No format found for report type %s" % doc.report_type)

    # merged_file = pypdftk.concat([fda, ttbf], touch_random_file())

    # print(merged_file)
    # return merged_file

    with open(pdfreport, "rb") as fileobj:
        filedata = fileobj.read()
        frappe.local.response.filename = file_name
        frappe.local.response.filecontent = filedata
        frappe.local.response.type = "download"
