from __future__ import unicode_literals

import frappe
from frappe import scrub
from textwrap import wrap
from frappe.utils import add_to_date, nowdate

@frappe.whitelist()
def create_lead(business_name,first_name,last_name,address,city,state,zipcode,website,email_address,telephone_number,territory,source=None,organization_lead=None,notes=None):

	if territory:
		if frappe.db.exists("Territory", territory):
			territory=territory
		else:
			territory='United States'
	else:
		territory='United States'

	if organization_lead!=None:
		organization_lead=organization_lead
	else:
		organization_lead=1
	
	if 	notes!=None:
		notes=notes
	else:
		notes=''

	if 	source!=None:
		source=source
	else:
		source="Wholesale Inquiry form"

	# hard coded values
	lead_owner="ahmed@zomoamerica.com"
	# lead_owner="ashish@greycube.in"
	request_type="Product Enquiry"
	country="United States"
	status="Lead"
	organization_lead=organization_lead
	company = frappe.db.get_single_value('Global Defaults', 'default_company')
	address_type="Billing"
	source=source
	contact_by="ahmed@zomoamerica.com"
	last_followup_date=add_to_date(nowdate(), months=0, days=7)
	first_followup_date=add_to_date(nowdate(), months=0, days=1)

	lead_map={
	"company_name":business_name,
	"website":website,
	"organization_lead":organization_lead,
	"status":status,
	"request_type":request_type,
	"company":company,
	"lead_owner":lead_owner,
	"territory":territory,
	"source":source,
	"contact_by":contact_by,
	"contact_date":first_followup_date,
	"ends_on":last_followup_date,
	"notes":notes
	}

	# Check if existing lead
	lead_name = None
	if email_address:
		lead_name = frappe.db.get_value("Lead", {"email_id": email_address})
		if not lead_name:
			lead_map.update({"email_id":email_address})

	if not lead_name and telephone_number:
		lead_name = frappe.db.get_value("Lead", {"phone": telephone_number})
		if not lead_name:
			lead_map.update({"phone":telephone_number})	

	if not lead_name:
		#new
		lead_name=frappe.scrub(first_name)+' '+frappe.scrub(last_name)
		lead_map.update({"lead_name":lead_name})	
		lead = frappe.new_doc("Lead")
		lead.update(lead_map)
		lead.insert(ignore_permissions=True)
		print(lead.name,"new lead")
	else:
		#existing lead
		lead=frappe.get_doc("Lead", lead_name)
		lead.update(lead_map)
		lead.save(ignore_permissions=True)
		print(lead.name,"existing lead")
	frappe.db.commit()

	address_list=wrap(address,40)
	print(len(address_list),'len(address_list)')
	if len(address_list)>1:
		address_line2=address_list[1]
		address_line1=address_list[0]+','
	else:
		address_line1=address_list[0]
		address_line2=None

	address_map={
		"address_line1":address_line1,
		"address_line2":address_line2,
		"address_type":address_type,
		"city":city,
		"state":state,
		"pincode":zipcode,
		"email_id":email_address,
		"phone":telephone_number,
		"country":country
	}
#check if existing address
	address_name=lead_name+"-"+address_type
	if frappe.db.exists("Address", address_name):
		address=frappe.get_doc("Address", address_name)
		address.update(address_map)
		address.save(ignore_permissions=True)
		print(address.name,"address existing")
	else:
		address = frappe.new_doc("Address")
		address.update(address_map)
		lead_link={
			"link_doctype":"Lead",
			"link_name":lead.name,
			"link_title":lead.name
		}
		address.append("links",lead_link)
		address.insert(ignore_permissions=True)
		print(address.name,"address new")
	frappe.db.commit()



def copy_shipping_details_from_item_to_SI(self,method):
	if self.items:
		if self.items[0]:
			if self.items[0].delivery_note:
				delivery_note=self.items[0].delivery_note
				shipping_method_za,shipment_tracking_no_za,	no_of_boxes_za = frappe.db.get_value('Delivery Note', delivery_note, ['shipping_method_za', 'shipment_tracking_no_za','no_of_boxes_za'])
				self.shipping_method_za=shipping_method_za
				self.shipment_tracking_no_za=shipment_tracking_no_za
				self.no_of_boxes_za=no_of_boxes_za
			

def calculate_total_tobacco_weight(self,method):
	self.total_tobacco_weight_za=0
	for item in self.items:
		if item.item_group =='TOBACCO':
			self.total_tobacco_weight_za+=item.total_weight
		else:
			item_group = frappe.get_doc("Item Group", item.item_group)
			parent_groups = frappe.db.sql("""select name from `tabItem Group`
			where lft <= %s and rgt >= %s
			and name = 'TOBACCO'
			order by lft asc""", (item_group.lft, item_group.rgt), as_list=True)
			if parent_groups:
				parent_tobacco_group=parent_groups[0][0]
				if parent_tobacco_group:
					self.total_tobacco_weight_za+=item.total_weight

def update_delivery_note_workflow_state(self,method):
	print('update_delivery_note_worflow_state-------')
	if self.status == 'Completed':
		print('---------inside')
		self.db_set('workflow_state', self.status, update_modified = True)

