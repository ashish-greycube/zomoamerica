from __future__ import unicode_literals

import frappe
from frappe import scrub
from textwrap import wrap

@frappe.whitelist()
# def create_lead(business_name,first_name,last_name,address,city,state,zipcode,website,email_address,telephone_number):
def create_lead(email_address):
	business_name='ys'
	first_name='yd'
	last_name='y'
	address='yyydyyyyyyyyssssssssssssdddddddddddddddddddddddd'
	city='yd'
	state='yd'
	zipcode='11212'
	website='yd.com'
	# email_address='y@y.com'
	telephone_number='11322'	
	
	# hard coded values
	# lead_owner="ahmed@zomoamerica.com"
	lead_owner="ashish@greycube.in"
	request_type="Product Enquiry"
	territory='United States'
	country="United States"
	status="Lead"
	organization_lead=1
	company = frappe.db.get_single_value('Global Defaults', 'default_company')
	address_type="Billing"

	lead_name=frappe.scrub(first_name)+frappe.scrub(last_name)

	# 
# "lead_owner":lead_owner,
	lead_map={
	"company_name":business_name,
	"lead_name":lead_name,
	"website":website,
	"email_id":email_address,
	"phone":telephone_number,
	"organization_lead":organization_lead,
	"status":status,
	"request_type":request_type,
	"company":company,
	"territory":territory
	}		

	lead = frappe.new_doc("Lead")
	lead.update(lead_map)
	lead.insert(ignore_permissions=True)
	# lead.save(ignore_permissions=True)
	print(lead.name,"lead")

	address_list=wrap(address,40)
	print(address_list)
	address_map={
		"address_line1":address_list[0],
		"address_line2":address_list[1],
		"address_type":address_type,
		"city":city,
		"state":state,
		"pincode":zipcode,
		"email_id":email_address,
		"phone":telephone_number,
		"country":country
	}

	address = frappe.new_doc("Address")
	address.update(address_map)
	lead_link={
		"link_doctype":"Lead",
		"link_name":lead.name,
		"link_title":lead.name
	}
	# address.append("links",lead_link)
	# # address.save(ignore_permissions=True)
	# address.insert(ignore_permissions=True)
	# print(address.name,"address")
	# frappe.db.commit()